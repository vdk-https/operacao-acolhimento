"""Operação Acolhimento: API REST de solicitações fictícias de assistência humanitária."""
import hmac
import hashlib
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import mysql.connector
import requests
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from core.config import load_settings
from core.database import RegistroRepository
from core.validation import validar_registro, validar_id, ValidationError, OPCOES
from core.weather import obter_clima


def _configurar_log(caminho):
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("acolhimento_auditoria." + hashlib.sha256(str(destino.resolve()).encode("utf-8")).hexdigest()[:12])
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler(destino, maxBytes=1_000_000, backupCount=2, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        logger.addHandler(handler)
    logger.propagate = False
    return logger


def create_app(repo=None, weather_fetcher=None, settings=None):
    configuracao = settings if settings is not None else load_settings()
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.config["MAX_CONTENT_LENGTH"] = 4096  # Rejeita JSONs exagerados.
    repositorio = repo if repo is not None else RegistroRepository(configuracao)
    clima = weather_fetcher if weather_fetcher is not None else obter_clima
    auditoria = _configurar_log(configuracao["LOG_PATH"])

    def registrar(acao, resultado, identificador="-"):
        auditoria.info("acao=%s resultado=%s id=%s", acao, resultado, identificador)

    def exigir_token():
        esperado = configuracao.get("WRITE_TOKEN", "")
        recebido = request.headers.get("X-API-Key", "")
        if not esperado or len(esperado) < 24 or esperado.startswith("SUBSTITUA") or not hmac.compare_digest(recebido.encode("utf-8"), esperado.encode("utf-8")):
            registrar(request.method, "NEGADO")
            return jsonify({"erro": "Acesso de edição não autorizado."}), 401
        return None

    def ler_json():
        if not request.is_json:
            raise ValidationError("Use Content-Type: application/json.")
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            raise ValidationError("Envie um objeto JSON válido.")
        return body

    @app.route("/")
    def inicio():
        return render_template("index.html")

    @app.get("/api/registros")
    def listar():
        grupo = request.args.get("grupo", "").strip()
        if grupo and grupo not in OPCOES["grupo"]:
            raise ValidationError("Grupo fictício inválido.")
        dados = repositorio.listar(grupo=grupo or None)
        registrar("LISTAR", "OK")
        return jsonify({"total": len(dados), "registros": dados}), 200

    @app.get("/api/registros/<int:identificador>")
    def detalhar(identificador):
        validar_id(identificador)
        registro = repositorio.buscar(identificador)
        if registro is None:
            registrar("DETALHAR", "NAO_ENCONTRADO", identificador)
            return jsonify({"erro": "Registro não encontrada."}), 404
        registrar("DETALHAR", "OK", identificador)
        return jsonify(registro), 200

    @app.post("/api/registros")
    def criar():
        negado = exigir_token()
        if negado is not None:
            return negado
        dados = validar_registro(ler_json())
        identificador = repositorio.criar(dados)
        registro = repositorio.buscar(identificador)
        registrar("CRIAR", "OK", identificador)
        return jsonify(registro), 201, {"Location": f"/api/registros/{identificador}"}

    @app.put("/api/registros/<int:identificador>")
    def atualizar(identificador):
        negado = exigir_token()
        if negado is not None:
            return negado
        validar_id(identificador)
        dados = validar_registro(ler_json(), atualizacao=True)
        alterado = repositorio.atualizar(identificador, dados)
        if not alterado:
            registrar("ATUALIZAR", "NAO_ENCONTRADO", identificador)
            return jsonify({"erro": "Registro não encontrada."}), 404
        registrar("ATUALIZAR", "OK", identificador)
        return jsonify(repositorio.buscar(identificador)), 200

    @app.delete("/api/registros/<int:identificador>")
    def excluir(identificador):
        negado = exigir_token()
        if negado is not None:
            return negado
        validar_id(identificador)
        excluido = repositorio.excluir(identificador)
        registrar("EXCLUIR", "OK" if excluido else "NAO_ENCONTRADO", identificador)
        if not excluido:
            return jsonify({"erro": "Registro não encontrada."}), 404
        return "", 204

    @app.get("/api/clima")
    def clima_atual():
        try:
            dados = clima()
            registrar("CLIMA", "OK")
            return jsonify(dados), 200
        except (requests.RequestException, ValueError, KeyError, TypeError):
            registrar("CLIMA", "INDISPONIVEL")
            return jsonify({"erro": "Dados meteorológicos indisponíveis no momento."}), 503

    @app.get("/health")
    def health():
        return jsonify({"aplicacao": "Operação Acolhimento", "status": "online"}), 200

    @app.errorhandler(ValidationError)
    def erro_validacao(erro):
        registrar(request.method, "DADOS_INVALIDOS")
        return jsonify({"erro": str(erro)}), 422

    @app.errorhandler(mysql.connector.Error)
    def erro_banco(erro):
        registrar(request.method, "FALHA_BANCO")
        return jsonify({"erro": "Serviço de dados temporariamente indisponível."}), 503

    @app.errorhandler(413)
    def erro_tamanho(erro):
        registrar(request.method, "TAMANHO_EXCEDIDO")
        return jsonify({"erro": "Conteúdo excede o limite permitido."}), 413

    @app.errorhandler(404)
    def erro_rota(erro):
        return jsonify({"erro": "Recurso não encontrado."}), 404

    @app.errorhandler(HTTPException)
    def erro_http(erro):
        registrar(request.method, "HTTP_INVALIDO")
        return jsonify({"erro": "Requisição inválida ou método não permitido."}), erro.code

    @app.errorhandler(Exception)
    def erro_geral(erro):
        registrar(request.method, "ERRO_INTERNO")
        # Não exponha stack trace, SQL, credenciais ou IPs em mensagens HTTP.
        return jsonify({"erro": "Não foi possível concluir a solicitação."}), 500

    return app


if __name__ == "__main__":
    cfg = load_settings()
    # Execução somente local, para demonstração: não exponha na Internet.
    if cfg["APP_HOST"] not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError("O protótipo deve ser executado somente no localhost.")
    create_app(settings=cfg).run(host=cfg["APP_HOST"], port=cfg["APP_PORT"], debug=False)
