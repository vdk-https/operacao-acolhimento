"""Módulo extra: socket TCP LOCAL para consulta simples da quantidade de relatos.

Protocolo: cliente manda STATUS\n (max. 32 bytes), servidor retorna JSON + \n.
Não expose em 0.0.0.0 ou na Internet: é demonstração acadêmica.
"""
import json
import socket
from core.config import load_settings
from core.database import RegistroRepository


def executar():
    settings = load_settings()
    if settings["TCP_HOST"] not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError("Por segurança, o socket deve ficar somente no localhost.")
    repo = RegistroRepository(settings)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((settings["TCP_HOST"], settings["TCP_PORT"]))
        servidor.listen(3)
        print(f"Status TCP local: {settings['TCP_HOST']}:{settings['TCP_PORT']}")
        while True:
            conn, _ = servidor.accept()
            with conn:
                conn.settimeout(3)
                try:
                    comando = conn.recv(33)
                    if comando != b"STATUS\n":
                        resposta = {"erro": "Comando inválido"}
                    else:
                        resposta = {"servico": "Operação Acolhimento", "total": repo.contar()}
                except Exception:
                    resposta = {"erro": "Consulta indisponível"}
                conn.sendall((json.dumps(resposta, ensure_ascii=False) + "\n").encode("utf-8"))


if __name__ == "__main__":
    executar()
