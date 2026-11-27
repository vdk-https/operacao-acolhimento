"""Testes automatizados isolados: repositório e API externa simulados.
Não alegam comprovar um MongoDB real ou disponibilidade da Open-Meteo.
"""
import pytest
pytest.importorskip("flask")
import pymongo
from app import create_app
from core.validation import validar_registro, ValidationError


class FakeRepo:
    def __init__(self):
        self.itens = {}
        self.sequencia = 1
    def listar(self, grupo=None):
        return [x for x in self.itens.values() if not grupo or grupo.casefold() in x["grupo"].casefold()]
    def buscar(self, identificador): return self.itens.get(identificador)
    def criar(self, dados):
        identificador = self.sequencia
        self.sequencia += 1
        self.itens[identificador] = {"id": identificador, **dados, "situacao": "aberto", "criado_em": "2026-11-05T10:00:00", "atualizado_em": "2026-11-05T10:00:00"}
        return identificador
    def atualizar(self, identificador, dados):
        if identificador not in self.itens: return False
        self.itens[identificador].update(dados)
        return True
    def excluir(self, identificador): return self.itens.pop(identificador, None) is not None


@pytest.fixture
def cliente(tmp_path):
    app = create_app(
        repo=FakeRepo(),
        weather_fetcher=lambda: {"temperatura_c": 22, "precipitacao_mm": 0, "proximas_horas": []},
        settings={"WRITE_TOKEN": "minha_chave_local_123456", "LOG_PATH": str(tmp_path / "auditoria.log")},
    )
    app.config.update(TESTING=True, TEST_LOG_PATH=str(tmp_path / "auditoria.log"))
    return app.test_client()


DADOS = {"grupo": "Grupo Alfa", "necessidade": "Alimentacao", "observacao": "Cenario de acolhimento simulado.", "prioridade": "alto"}
CHAVE = {"X-API-Key": "minha_chave_local_123456"}


def test_fluxo_crud(cliente):
    assert cliente.get("/api/registros").status_code == 200
    resposta = cliente.post("/api/registros", json=DADOS, headers=CHAVE)
    assert resposta.status_code == 201 and resposta.json["id"] == 1
    assert resposta.headers["Location"] == "/api/registros/1"
    assert cliente.get("/api/registros/1").json["prioridade"] == "alto"
    assert cliente.put("/api/registros/1", json={"situacao": "resolvido"}, headers=CHAVE).status_code == 200
    assert cliente.get("/api/registros/1").json["situacao"] == "resolvido"
    assert cliente.delete("/api/registros/1", headers=CHAVE).status_code == 204
    assert cliente.get("/api/registros/1").status_code == 404


def test_acesso_sem_chave_bloqueado(cliente):
    assert cliente.post("/api/registros", json=DADOS).status_code == 401
    assert cliente.delete("/api/registros/1").status_code == 401


def test_entrada_invalida(cliente):
    assert cliente.post("/api/registros", json={**DADOS,"prioridade":"crítica"}, headers=CHAVE).status_code == 422
    assert cliente.post("/api/registros", json={**DADOS,"observacao":"<script>alert(1)</script>"}, headers=CHAVE).status_code == 422
    assert cliente.put("/api/registros/1", json={"campo_sql":"invasao"}, headers=CHAVE).status_code == 422
    assert cliente.post("/api/registros", data="texto", headers=CHAVE).status_code == 422


def test_http_limite(cliente):
    assert cliente.post("/api/registros", data="X" * 5000, content_type="application/json", headers=CHAVE).status_code == 413


def test_clima_mockado(cliente):
    assert cliente.get("/api/clima").status_code == 200
    assert cliente.get("/api/clima").json["temperatura_c"] == 22


def test_arquivo_log_criado(cliente):
    from pathlib import Path
    cliente.get("/api/registros")
    conteudo = Path(cliente.application.config["TEST_LOG_PATH"]).read_text(encoding="utf-8")
    assert "acao=LISTAR resultado=OK" in conteudo


def test_metodo_http_errado(cliente):
    assert cliente.patch("/api/registros").status_code == 405


def test_texto_com_sql_nao_e_executado_como_sql():
    dado = validar_registro({**DADOS, "grupo": "Grupo Bravo"})
    assert dado["grupo"] == "Grupo Bravo"
    with pytest.raises(ValidationError):
        validar_registro({**DADOS, "grupo": "X'; DROP TABLE registros; --"})


def test_metodo_nao_permitido(cliente):
    assert cliente.patch("/api/registros/1", headers=CHAVE).status_code == 405
