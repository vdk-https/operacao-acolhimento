"""Dados externos de previsão, sem geolocalização pessoal."""
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

ENDPOINT = "https://api.open-meteo.com/v1/forecast"
# Coordenadas fixas aproximadas do centro de São Paulo: não identificam usuários.
LATITUDE = -23.5505
LONGITUDE = -46.6333


def obter_clima():
    resposta = requests.get(
        ENDPOINT,
        params={
            "latitude": LATITUDE, "longitude": LONGITUDE,
            "current": "temperature_2m,precipitation",
            "hourly": "precipitation_probability",
            "forecast_days": 2,
            "timezone": "America/Sao_Paulo",
        },
        timeout=5,
    )
    resposta.raise_for_status()
    dados = resposta.json()
    atual = dados["current"]
    horario = dados["hourly"]
    horas = horario["time"]
    probabilidades = horario["precipitation_probability"]
    if not isinstance(horas, list) or not isinstance(probabilidades, list) or len(horas) != len(probabilidades):
        raise ValueError("Resposta meteorológica inválida")
    agora = datetime.now(ZoneInfo("America/Sao_Paulo")).replace(tzinfo=None)
    proximas = [
        {"hora": hora, "probabilidade": prob}
        for hora, prob in zip(horas, probabilidades)
        if datetime.fromisoformat(hora) >= agora.replace(minute=0, second=0, microsecond=0)
    ][:6]
    return {
        "local": "São Paulo - centro (referência geral)",
        "temperatura_c": atual["temperature_2m"],
        "precipitacao_mm": atual["precipitation"],
        "proximas_horas": proximas,
        "fonte": "Open-Meteo",
        "consultado_em": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(timespec="seconds"),
        "aviso": "Estimativa climática geral; não orienta operações reais.",
    }
