"""Checks independentes de Flask e MySQL."""
import pytest
from core.validation import validar_registro, validar_id, ValidationError

EXEMPLO = {"grupo": "Grupo Alfa", "necessidade": "Alimentacao",
           "observacao": "Cenario de acolhimento simulado.", "prioridade": "medio"}

def test_criar_campos_validos():
    assert validar_registro(EXEMPLO) == EXEMPLO

def test_campos_extras_bloqueados():
    with pytest.raises(ValidationError): validar_registro({**EXEMPLO, "admin": True})

def test_html_nao_permitido():
    with pytest.raises(ValidationError): validar_registro({**EXEMPLO, "observacao": "<img src=x onerror=alert(1)>"})

def test_erro_tipo_id():
    with pytest.raises(ValidationError): validar_id(True)

def test_atualizacao_parcial():
    assert validar_registro({"situacao": "resolvido"}, atualizacao=True) == {"situacao": "resolvido"}

def test_status_inesperado():
    with pytest.raises(ValidationError): validar_registro({"situacao": "suspenso"}, atualizacao=True)
