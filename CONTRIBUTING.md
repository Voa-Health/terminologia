# Contribuindo

## Ambiente

Instale [uv](https://docs.astral.sh/uv/) e prepare o projeto:

```sh
uv sync --all-extras --group dev
uvx pre-commit install
```

## Padrões

- Escreva textos curtos.
- Comente apenas para explicar uma intenção não óbvia.
- Prefira poucos testes parametrizados pela API pública.
- Use apenas dados sintéticos nos testes.

## Como contribuir

Antes de enviar, execute:

```sh
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
```
