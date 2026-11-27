"""Testes realmente executáveis sem Flask nem MySQL: validação e serviço externo simulado."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from unittest.mock import Mock
import pytest
from core.validation import validar_registro, ValidationError
from core import weather

BASE = {"grupo": "Grupo Alfa", "necessidade": "Alimentacao", "observacao": "Cenario de acolhimento simulado.", "prioridade": "medio"}


def test_normaliza_espacos():
    assert validar_registro({**BASE, "grupo": " Grupo   Alfa  "})["grupo"] == "Grupo Alfa"


def test_exige_quatro_campos():
    with pytest.raises(ValidationError):
        validar_registro({"grupo": "Grupo Alfa"})


def test_rejeita_injecao_e_html():
    with pytest.raises(ValidationError):
        validar_registro({**BASE, "observacao": "<script>alert('xss')</script>"})


def test_rejeita_campos_surpresa():
    with pytest.raises(ValidationError):
        validar_registro({**BASE, "senha": "nao"})


def test_atualizacao_parcial():
    assert validar_registro({"situacao": "resolvido"}, atualizacao=True) == {"situacao": "resolvido"}


def test_consumo_weather_requests_json(monkeypatch):
    base = datetime.now(ZoneInfo("America/Sao_Paulo")).replace(minute=0, second=0, microsecond=0)
    horas = [(base + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(10)]
    response = Mock()
    response.json.return_value = {
        "current": {"temperature_2m": 23.2, "precipitation": 0.2},
        "hourly": {"time": horas, "precipitation_probability": [20]*10},
    }
    get = Mock(return_value=response)
    monkeypatch.setattr(weather.requests, "get", get)
    result = weather.obter_clima()
    assert result["fonte"] == "Open-Meteo"
    assert result["temperatura_c"] == 23.2
    assert len(result["proximas_horas"]) == 6
    assert get.call_args.kwargs["timeout"] == 5
