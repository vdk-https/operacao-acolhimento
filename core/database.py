"""Acesso MySQL via SQL parametrizado, sem ORM."""
from datetime import datetime
import mysql.connector


class RegistroRepository:
    CAMPOS_PERMITIDOS = {"grupo", "necessidade", "observacao", "prioridade", "situacao"}

    def __init__(self, settings):
        self.settings = settings

    def _connect(self):
        return mysql.connector.connect(
            host=self.settings["DB_HOST"], port=self.settings["DB_PORT"],
            user=self.settings["DB_USER"], password=self.settings["DB_PASSWORD"],
            database=self.settings["DB_NAME"], connection_timeout=5,
        )

    @staticmethod
    def _normalizar(item):
        if item is None:
            return None
        for campo in ("criado_em", "atualizado_em"):
            if isinstance(item.get(campo), datetime):
                item[campo] = item[campo].isoformat(timespec="seconds")
        return item

    def listar(self, grupo=None):
        con = self._connect()
        cur = con.cursor(dictionary=True)
        try:
            if grupo:
                cur.execute(
                    "SELECT * FROM registros WHERE grupo LIKE %s ORDER BY criado_em DESC, id DESC LIMIT 100",
                    (f"%{grupo}%",),
                )
            else:
                cur.execute("SELECT * FROM registros ORDER BY criado_em DESC, id DESC LIMIT 100")
            return [self._normalizar(x) for x in cur.fetchall()]
        finally:
            cur.close()
            con.close()

    def buscar(self, identificador):
        con = self._connect()
        cur = con.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM registros WHERE id = %s", (identificador,))
            return self._normalizar(cur.fetchone())
        finally:
            cur.close()
            con.close()

    def criar(self, dados):
        con = self._connect()
        cur = con.cursor()
        try:
            cur.execute(
                "INSERT INTO registros (grupo, necessidade, observacao, prioridade) "
                "VALUES (%s, %s, %s, %s)",
                (dados["grupo"], dados["necessidade"], dados["observacao"], dados["prioridade"]),
            )
            identificador = cur.lastrowid
            con.commit()
            return identificador
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

    def atualizar(self, identificador, dados):
        # Só interpolamos identificadores do conjunto fixo; VALORES sempre usam parâmetros SQL.
        if not dados or set(dados) - self.CAMPOS_PERMITIDOS:
            raise ValueError("Campos inválidos.")
        con = self._connect()
        cur = con.cursor()
        try:
            # SELECT FOR UPDATE permite diferenciar inexistente de registro sem alteração.
            cur.execute("SELECT id FROM registros WHERE id = %s FOR UPDATE", (identificador,))
            if cur.fetchone() is None:
                con.rollback()
                return False
            atribuicoes = ", ".join(f"{campo} = %s" for campo in dados)
            cur.execute(f"UPDATE registros SET {atribuicoes} WHERE id = %s", (*dados.values(), identificador))
            con.commit()
            return True
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

    def excluir(self, identificador):
        con = self._connect()
        cur = con.cursor()
        try:
            cur.execute("DELETE FROM registros WHERE id = %s", (identificador,))
            con.commit()
            return cur.rowcount > 0
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
            con.close()

    def contar(self):
        con = self._connect()
        cur = con.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM registros")
            return cur.fetchone()[0]
        finally:
            cur.close()
            con.close()
