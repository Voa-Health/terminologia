from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest

from terminologia import Terminologia


class ServidorFalso:
    def __init__(self) -> None:
        self.respostas: dict[str, dict[str, Any]] = {}
        self.requisicoes: list[dict[str, Any]] = []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                parsed = urlsplit(self.path)
                owner.requisicoes.append(
                    {
                        "path": parsed.path,
                        "query": parse_qs(parsed.query),
                        "headers": dict(self.headers.items()),
                    }
                )
                response = owner.respostas.get(parsed.path.removeprefix("/"), {})
                if response.get("atraso"):
                    time.sleep(response["atraso"])
                body = json.dumps(response.get("corpo", {})).encode("utf-8")
                self.send_response(response.get("status", 200))
                for name, value in response.get("headers", {}).items():
                    self.send_header(name, value)
                self.send_header("Content-Type", "application/fhir+json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: Any) -> None:
                return

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_port}"
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def fechar(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join()


@pytest.fixture
def servidor():
    server = ServidorFalso()
    try:
        yield server
    finally:
        server.fechar()


@pytest.fixture
def cliente(servidor: ServidorFalso) -> Terminologia:
    return Terminologia(api_key="sk_voa_teste", base_url=servidor.url, timeout=0.5)
