"""Erros apresentados pelo cliente de terminologia."""

from __future__ import annotations

import json
import socket
import urllib.error
from typing import Any

URL_CHAVES = "https://tiss-api.voa.health/org"


class TerminologiaError(Exception):
    """Erro retornado pela API ou pelo transporte."""

    def __init__(
        self,
        mensagem: str,
        *,
        status: int | None = None,
        codigo: str | None = None,
    ) -> None:
        super().__init__(mensagem)
        self.status = status
        self.codigo = codigo
        self.mensagem = mensagem


class ChaveInvalidaError(TerminologiaError):
    """A chave está ausente ou não foi aceita."""


class AcessoNegadoError(TerminologiaError):
    """A chave não tem acesso ao recurso."""


class CotaExcedidaError(TerminologiaError):
    """A cota de consultas foi excedida."""

    def __init__(
        self,
        mensagem: str,
        *,
        retry_after: int | None = None,
        status: int = 429,
        codigo: str | None = None,
    ) -> None:
        super().__init__(mensagem, status=status, codigo=codigo)
        self.retry_after = retry_after


class RedeError(TerminologiaError):
    """Falha ao conectar ao serviço."""


class TempoEsgotadoError(RedeError):
    """A consulta excedeu o tempo limite."""


class ServidorError(TerminologiaError):
    """A API retornou um erro não classificado."""


def _mensagem_http(status: int, payload: Any) -> tuple[str, str | None]:
    codigo: str | None = None
    message: str | None = None
    if isinstance(payload, dict):
        issue = payload.get("issue")
        if isinstance(issue, list) and issue and isinstance(issue[0], dict):
            first = issue[0]
            candidate = first.get("code")
            codigo = candidate if isinstance(candidate, str) else None
            diagnostics = first.get("diagnostics")
            details = first.get("details")
            detail_text = details.get("text") if isinstance(details, dict) else None
            if isinstance(diagnostics, str) and diagnostics:
                message = diagnostics
            elif isinstance(detail_text, str) and detail_text:
                message = detail_text
        if message is None and isinstance(payload.get("detail"), str):
            message = payload["detail"]
    return message or f"HTTP {status}", codigo


def erro_http(
    status: int,
    body: bytes,
    headers: Any,
) -> TerminologiaError:
    """Converta uma resposta HTTP de erro em uma exceção tipada."""
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = None
    mensagem, codigo = _mensagem_http(status, payload)
    if status in {401, 403}:
        mensagem += f" Crie ou confira a chave da organização em {URL_CHAVES}."
    if status == 401:
        return ChaveInvalidaError(mensagem, status=status, codigo=codigo)
    if status == 403:
        return AcessoNegadoError(mensagem, status=status, codigo=codigo)
    if status == 429:
        retry_header = headers.get("Retry-After")
        try:
            retry_after = int(retry_header) if retry_header is not None else None
        except (TypeError, ValueError):
            retry_after = None
        return CotaExcedidaError(
            mensagem,
            retry_after=retry_after,
            status=status,
            codigo=codigo,
        )
    return ServidorError(mensagem, status=status, codigo=codigo)


def erro_rede(error: BaseException) -> RedeError:
    """Converta falhas de urllib e de timeout em erros públicos."""
    if isinstance(error, (TimeoutError, socket.timeout)):
        return TempoEsgotadoError(str(error) or "Tempo limite excedido.")
    if isinstance(error, urllib.error.URLError):
        reason = error.reason
        if isinstance(reason, (TimeoutError, socket.timeout)):
            return TempoEsgotadoError(str(reason) or "Tempo limite excedido.")
        return RedeError(str(reason) or "Falha de rede.")
    return RedeError(str(error) or "Falha de rede.")
