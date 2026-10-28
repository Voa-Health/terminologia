"""Cliente FHIR baseado em urllib."""

from __future__ import annotations

import copy
import json
import os
import threading
import urllib.error
import urllib.request
from collections import OrderedDict
from typing import Any
from urllib.parse import urlencode, urlsplit

from . import __version__
from ._erros import (
    ChaveInvalidaError,
    RedeError,
    TerminologiaError,
    erro_http,
    erro_rede,
)
from ._modelos import MARCADORES, Conceito, Resultado, Validacao
from ._sistemas import Sistema

_CACHE_MAXIMO = 256
_CACHE_PADRAO: dict[str, Terminologia | None] = {"cliente": None}
_CACHE_LOCK = threading.Lock()
_URL_PADRAO = "https://terminologia.voa.health/api/v1/fhir"


def _origem(url: str) -> tuple[str, str | None, int | None]:
    partes = urlsplit(url)
    porta = partes.port
    if porta is None:
        porta = {"http": 80, "https": 443}.get(partes.scheme)
    return partes.scheme, partes.hostname, porta


class _RedirectMesmaOrigem(urllib.request.HTTPRedirectHandler):
    """Preserve credenciais somente em redirects para a mesma origem."""

    http_error_308 = urllib.request.HTTPRedirectHandler.http_error_302

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> urllib.request.Request | None:
        """Evite que um redirect exponha a chave de acesso."""
        try:
            mesma_origem = _origem(req.full_url) == _origem(newurl)
        except ValueError:
            mesma_origem = False
        if not mesma_origem:
            fp.close()
            raise RedeError("Redirecionamento para outra origem bloqueado.", status=code)
        # Python 3.10 só reconhece o código equivalente 307 neste método.
        return super().redirect_request(req, fp, 307 if code == 308 else code, msg, headers, newurl)


_OPENER = urllib.request.build_opener(_RedirectMesmaOrigem())


class Terminologia:
    """Cliente da API de terminologia FHIR.

    Aceita chaves de produto ``sk_voa_`` e ``sk_tiss_`` com escopo
    ``terminology:read``; a validação da chave é feita pelo servidor.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.api_key = api_key
        resolved_url = (
            base_url if base_url is not None else os.environ.get("TERMINOLOGIA_URL") or _URL_PADRAO
        )
        self.base_url = resolved_url.rstrip("/")
        self.timeout = timeout
        self._cache: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._lock = threading.RLock()

    def _chave(self) -> str:
        key = self.api_key or os.environ.get("TERMINOLOGIA_KEY")
        if not key:
            raise ChaveInvalidaError(
                "Defina TERMINOLOGIA_KEY com a chave da organização em "
                "https://tiss-api.voa.health/org.",
                status=401,
            )
        return key

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        query = urlencode({key: value for key, value in params.items() if value is not None})
        url = f"{self.base_url}/{path}" + (f"?{query}" if query else "")
        with self._lock:
            cached = self._cache.get(url)
            if cached is not None:
                self._cache.move_to_end(url)
                return copy.deepcopy(cached)

        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self._chave()}",
                "Accept": "application/fhir+json, application/json;q=0.9",
                "User-Agent": f"terminologia/{__version__}",
                "X-Client": f"terminologia/{__version__}",
            },
            method="GET",
        )
        try:
            with _OPENER.open(request, timeout=self.timeout) as response:
                body = response.read()
                status = response.status
                headers = response.headers
        except urllib.error.HTTPError as exc:
            body = exc.read()
            raise erro_http(exc.code, body, exc.headers) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise erro_rede(exc) from exc
        if status >= 400:
            raise erro_http(status, body, headers)
        payload = json.loads(body.decode("utf-8"))
        if not isinstance(payload, dict):
            raise TerminologiaError("A resposta FHIR não é um objeto JSON.")
        if status == 200:
            with self._lock:
                self._cache[url] = copy.deepcopy(payload)
                self._cache.move_to_end(url)
                while len(self._cache) > _CACHE_MAXIMO:
                    self._cache.popitem(last=False)
        return payload

    def expand(
        self,
        url: str,
        filter: str | None = None,
        count: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """Expanda um ValueSet."""
        return self._get(
            "ValueSet/$expand",
            {"url": url, "filter": filter, "count": count, "offset": offset},
        )

    def lookup(
        self,
        system: str,
        code: str,
        version: str | None = None,
    ) -> dict[str, Any]:
        """Consulte um conceito em um CodeSystem."""
        return self._get(
            "CodeSystem/$lookup",
            {"system": system, "code": code, "version": version},
        )

    def validate_code(
        self,
        code: str,
        *,
        system: str | None = None,
        value_set: str | None = None,
        display: str | None = None,
    ) -> dict[str, Any]:
        """Valide um código em um sistema ou ValueSet."""
        if value_set is not None:
            path = "ValueSet/$validate-code"
            params = {"url": value_set, "code": code, "system": system, "display": display}
        elif system is not None:
            path = "CodeSystem/$validate-code"
            params = {"url": system, "code": code, "display": display}
        else:
            raise ValueError("Informe system ou value_set para validar o código.")
        return self._get(path, params)

    def translate(
        self,
        system: str,
        code: str,
        target_system: str | None = None,
        url: str | None = None,
    ) -> dict[str, Any]:
        """Traduza um conceito para outro sistema."""
        return self._get(
            "ConceptMap/$translate",
            {"system": system, "code": code, "targetsystem": target_system, "url": url},
        )

    def subsumes(self, system: str, code_a: str, code_b: str) -> dict[str, Any]:
        """Consulte a relação hierárquica entre dois códigos."""
        return self._get(
            "CodeSystem/$subsumes",
            {"system": system, "codeA": code_a, "codeB": code_b},
        )

    def search(
        self,
        filter: str,
        count: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """Pesquise no índice de terminologia."""
        return self._get(
            "CodeSystem/$voa-search",
            {"filter": filter, "count": count, "offset": offset},
        )

    def sistema(self, nome_ou_url: str) -> Sistema:
        """Associe este cliente a um sistema."""
        from ._sistemas import sistema

        item = sistema(nome_ou_url)
        if item.nome == "tuss":
            from ._sistemas import criar_tuss

            return criar_tuss(self)
        return item.com(self)


def _parameter_map(payload: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in payload.get("parameter", []):
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            continue
        name = item["name"]
        if "part" in item:
            result.setdefault(name, []).append(item["part"])
            continue
        for key, value in item.items():
            if key.startswith("value"):
                result[name] = value
                break
    return result


def _conceito_coding(coding: dict[str, Any]) -> Conceito:
    return Conceito(
        system=str(coding.get("system", "")),
        code=str(coding.get("code", "")),
        display=coding.get("display") if isinstance(coding.get("display"), str) else None,
        version=coding.get("version") if isinstance(coding.get("version"), str) else None,
        raw=coding,
    )


def _conceito_parameters(payload: dict[str, Any]) -> Conceito:
    values = _parameter_map(payload)
    system = values.get("system")
    code = values.get("code")
    display = values.get("display")
    version = values.get("version")
    return Conceito(
        system=system if isinstance(system, str) else "",
        code=code if isinstance(code, str) else "",
        display=display if isinstance(display, str) else None,
        version=version if isinstance(version, str) else None,
        raw=payload,
    )


def _marcadores(parameters: list[Any]) -> tuple[frozenset[str], bool]:
    degraded: set[str] = set()
    partial = False
    for item in parameters:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if name in MARCADORES:
            degraded.add(name)
        elif name == "total-partial":
            partial = True
    return frozenset(degraded), partial


def _resultado_busca(payload: dict[str, Any]) -> Resultado:
    if payload.get("resourceType") == "ValueSet":
        expansion = payload.get("expansion", {})
        if not isinstance(expansion, dict):
            expansion = {}
        concepts = tuple(
            _conceito_coding(item)
            for item in expansion.get("contains", [])
            if isinstance(item, dict)
        )
        degraded, partial = _marcadores(expansion.get("parameter", []))
        total = expansion.get("total")
        return Resultado(
            conceitos=concepts,
            total=total if isinstance(total, int) else None,
            degradado=degraded,
            total_parcial=partial,
            raw=payload,
        )

    matching_concepts: list[Conceito] = []
    degraded, partial = _marcadores(payload.get("parameter", []))
    for match in payload.get("parameter", []):
        if not isinstance(match, dict) or match.get("name") != "match":
            continue
        for part in match.get("part", []):
            if not isinstance(part, dict) or part.get("name") != "concept":
                continue
            coding = part.get("valueCoding")
            if isinstance(coding, dict):
                matching_concepts.append(_conceito_coding(coding))
    return Resultado(
        conceitos=tuple(matching_concepts),
        total=None,
        degradado=degraded,
        total_parcial=partial,
        raw=payload,
    )


def _validacao_parameters(payload: dict[str, Any]) -> Validacao:
    values = _parameter_map(payload)
    valid = values.get("result") is True
    code = values.get("code")
    system = values.get("system")
    display = values.get("display")
    version = values.get("version")
    concept = None
    if isinstance(code, str):
        concept = Conceito(
            system=system if isinstance(system, str) else "",
            code=code,
            display=display if isinstance(display, str) else None,
            version=version if isinstance(version, str) else None,
            raw=payload,
        )
    message = values.get("message")
    return Validacao(
        valido=valid,
        conceito=concept,
        mensagem=message if isinstance(message, str) else None,
        raw=payload,
    )


def padrao() -> Terminologia:
    """Retorne o cliente padrão criado sob demanda."""
    with _CACHE_LOCK:
        cliente = _CACHE_PADRAO["cliente"]
        if cliente is None:
            cliente = Terminologia()
            _CACHE_PADRAO["cliente"] = cliente
        return cliente


def _reset_padrao() -> None:
    with _CACHE_LOCK:
        _CACHE_PADRAO["cliente"] = None
