"""Cliente TCP de demonstração (executar com servidor TCP ativo)."""
import socket
from core.config import load_settings


def executar():
    settings = load_settings()
    with socket.create_connection((settings["TCP_HOST"], settings["TCP_PORT"]), timeout=3) as sock:
        sock.sendall(b"STATUS\n")
        dados = sock.recv(512)
        print(dados.decode("utf-8").strip())


if __name__ == "__main__":
    executar()
