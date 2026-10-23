"""Modelos públicos das respostas de terminologia."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

MARCADORES = ("semantic-degraded", "lexical-degraded", "search-unavailable")


@dataclass(frozen=True)
class Conceito:
    """Um conceito de um sistema de codificação."""

    system: str
    code: str
    display: str | None = None
    version: str | None = None
    raw: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)

    def coding(self) -> dict[str, str]:
        """Retorne o conceito no formato FHIR Coding."""
        result = {"system": self.system, "code": self.code}
        if self.display is not None:
            result["display"] = self.display
        if self.version is not None:
            result["version"] = self.version
        return result


@dataclass(frozen=True)
class Resultado:
    """Conceitos encontrados e metadados da busca."""

    conceitos: tuple[Conceito, ...]
    total: int | None
    degradado: frozenset[str]
    total_parcial: bool = False
    raw: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)

    def __iter__(self) -> Iterator[Conceito]:
        return iter(self.conceitos)

    def __len__(self) -> int:
        return len(self.conceitos)


@dataclass(frozen=True)
class Validacao:
    """Resultado da validação de um código."""

    valido: bool
    conceito: Conceito | None
    mensagem: str | None
    raw: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)

    def __bool__(self) -> bool:
        return self.valido
