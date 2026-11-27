"""CRUD MongoDB via PyMongo, sem ORM, com filtros fixos e valores validados."""
from datetime import datetime, timezone
from pymongo import MongoClient, ReturnDocument
from core.validation import validar_registro, validar_id, OPCOES, ValidationError


class RegistroRepository:
    def __init__(self, settings):
        self.client = MongoClient(settings['MONGO_URI'], serverSelectionTimeoutMS=5000)
        db = self.client[settings['DB_NAME']]
        self.registros = db['registros']
        self.contadores = db['contadores']

    @staticmethod
    def _normalizar(item):
        if item is None:
            return None
        item = dict(item)
        item['id'] = item.pop('_id')
        for campo in ('criado_em', 'atualizado_em'):
            if isinstance(item.get(campo), datetime):
                item[campo] = item[campo].isoformat(timespec='seconds')
        return item

    def listar(self, grupo=None):
        if grupo is not None and (not isinstance(grupo, str) or grupo not in OPCOES['grupo']):
            raise ValidationError('Grupo fictício inválido.')
        filtro = {'grupo': grupo} if grupo else {}
        return [self._normalizar(x) for x in self.registros.find(filtro).sort([('criado_em', -1), ('_id', -1)]).limit(100)]

    def buscar(self, identificador):
        return self._normalizar(self.registros.find_one({'_id': validar_id(identificador)}))

    def criar(self, dados):
        dados = validar_registro(dados)
        contador = self.contadores.find_one_and_update({'_id': 'registros'}, {'$inc': {'valor': 1}}, upsert=True, return_document=ReturnDocument.AFTER)
        identificador = validar_id(contador['valor'])
        agora = datetime.now(timezone.utc)
        self.registros.insert_one({'_id': identificador, **dados, 'situacao': 'aberto', 'criado_em': agora, 'atualizado_em': agora})
        return identificador

    def atualizar(self, identificador, dados):
        dados = validar_registro(dados, atualizacao=True)
        resultado = self.registros.update_one({'_id': validar_id(identificador)}, {'$set': {**dados, 'atualizado_em': datetime.now(timezone.utc)}})
        return resultado.matched_count == 1

    def excluir(self, identificador):
        return self.registros.delete_one({'_id': validar_id(identificador)}).deleted_count == 1

    def contar(self):
        return self.registros.count_documents({})
