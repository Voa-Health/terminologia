"""Interface de linha de comando."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from . import __version__
from ._erros import TerminologiaError
from ._modelos import Conceito, Resultado
from ._sistemas import SISTEMAS, _serialize_sistema, sistema

_USAGE_ERROR = 2


def _arguments(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="terminologia")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    buscar = commands.add_parser("buscar", help="busca conceitos pelo texto")
    buscar.add_argument("sistema")
    buscar.add_argument("texto")
    buscar.add_argument("-n", type=int, default=20)
    buscar.add_argument("--json", action="store_true")

    for name, help_text in (
        ("lookup", "consulta um código"),
        ("validar", "valida um código"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("sistema")
        command.add_argument("codigo")
        command.add_argument("--json", action="store_true")

    traduzir = commands.add_parser("traduzir", help="traduz um código")
    traduzir.add_argument("sistema")
    traduzir.add_argument("codigo")
    traduzir.add_argument("--para")
    traduzir.add_argument("--json", action="store_true")

    sistemas_parser = commands.add_parser("sistemas", help="lista os sistemas disponíveis")
    sistemas_parser.add_argument("--json", action="store_true")
    commands.add_parser("mcp", help="inicia o servidor MCP local em stdio")
    return parser.parse_args(argv)


def _conceito_json(concept: Conceito | None) -> dict[str, str] | None:
    return concept.coding() if concept is not None else None


def _emitir_json(payload: Any) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _atribuicoes(*nomes: str) -> None:
    seen: set[str] = set()
    for name in nomes:
        if not name:
            continue
        attribution = sistema(name).atribuicao
        if attribution is not None and attribution not in seen:
            sys.stderr.write(attribution + "\n")
            seen.add(attribution)


def _resultado_payload(result: Resultado) -> dict[str, Any]:
    return {
        "conceitos": [concept.coding() for concept in result],
        "total": result.total,
        "degradado": sorted(result.degradado),
        "total_parcial": result.total_parcial,
    }


def _buscar(args: argparse.Namespace) -> int:
    item = sistema(args.sistema)
    result = item.buscar(args.texto, n=args.n)
    _atribuicoes(item.nome)
    if result.degradado:
        sys.stderr.write(f"aviso: busca degradada ({', '.join(sorted(result.degradado))})\n")
    if args.json:
        _emitir_json(_resultado_payload(result))
    else:
        for concept in result:
            sys.stdout.write(f"{concept.code}  {concept.display or ''}\n")
    if "search-unavailable" in result.degradado:
        return _USAGE_ERROR
    return 0 if result.conceitos else 1


def _lookup(args: argparse.Namespace) -> int:
    item = sistema(args.sistema)
    concept = item.lookup(args.codigo)
    _atribuicoes(item.nome)
    if args.json:
        _emitir_json({"conceito": _conceito_json(concept)})
    elif concept is not None:
        sys.stdout.write(f"{concept.code}  {concept.display or ''}  ({concept.system})\n")
    return 0 if concept is not None else 1


def _validar(args: argparse.Namespace) -> int:
    item = sistema(args.sistema)
    validation = item.validar(args.codigo)
    _atribuicoes(item.nome)
    if args.json:
        _emitir_json(
            {
                "valido": validation.valido,
                "conceito": _conceito_json(validation.conceito),
                "mensagem": validation.mensagem,
            }
        )
    elif validation.valido:
        display = validation.conceito.display if validation.conceito is not None else ""
        sys.stdout.write(f"válido: {args.codigo}  {display or ''}\n")
    else:
        sys.stdout.write(f"inválido: {args.codigo} — {validation.mensagem or ''}\n")
    return 0 if validation.valido else 1


def _traduzir(args: argparse.Namespace) -> int:
    from ._cliente import padrao

    item = sistema(args.sistema)
    target = sistema(args.para) if args.para else None
    _atribuicoes(item.nome, target.nome if target is not None else "")
    payload = padrao().translate(
        item.system,
        args.codigo,
        target_system=target.system if target is not None else None,
    )
    if args.json:
        _emitir_json(payload)
    else:
        translated = False
        for match in payload.get("parameter", []):
            if not isinstance(match, dict) or match.get("name") != "match":
                continue
            parts = {
                part.get("name"): part for part in match.get("part", []) if isinstance(part, dict)
            }
            coding = parts.get("concept", {}).get("valueCoding", {})
            relationship = parts.get("relationship", {}).get("valueCode")
            if isinstance(coding, dict) and coding.get("code"):
                suffix = f"  ({relationship})" if relationship else ""
                sys.stdout.write(
                    f"{coding.get('code')}  {coding.get('display', '')}"
                    f"  ({coding.get('system', '')}){suffix}\n"
                )
                translated = True
        if not translated:
            message = next(
                (
                    item.get("valueString")
                    for item in payload.get("parameter", [])
                    if isinstance(item, dict)
                    and item.get("name") == "message"
                    and isinstance(item.get("valueString"), str)
                ),
                None,
            )
            if message:
                sys.stdout.write(f"sem tradução: {message}\n")
    result = next(
        (
            item.get("valueBoolean")
            for item in payload.get("parameter", [])
            if isinstance(item, dict) and item.get("name") == "result"
        ),
        False,
    )
    return 0 if result is True else 1


def _sistemas(args: argparse.Namespace) -> int:
    if args.json:
        _emitir_json([_serialize_sistema(item) for item in SISTEMAS])
    else:
        for item in SISTEMAS:
            sys.stdout.write(f"{item.nome}  {item.rotulo}  {item.system}\n")
    return 0


def _mcp() -> int:
    try:
        from ._mcp import main
    except ImportError:
        sys.stderr.write('Instale o extra: pip install "terminologia[mcp]"\n')
        return _USAGE_ERROR
    main()
    return 0


def main(argv: list[str] | None = None) -> int:
    """Execute a CLI e retorne seu código de saída."""
    try:
        args = _arguments(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 0
    try:
        if args.command == "buscar":
            return _buscar(args)
        if args.command == "lookup":
            return _lookup(args)
        if args.command == "validar":
            return _validar(args)
        if args.command == "traduzir":
            return _traduzir(args)
        if args.command == "sistemas":
            return _sistemas(args)
        return _mcp()
    except (TerminologiaError, ValueError) as exc:
        sys.stderr.write(f"{exc}\n")
        return _USAGE_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
