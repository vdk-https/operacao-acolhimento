"""Somente categorias de demonstração; sem informações pessoais ou localização."""
PRIORIDADES = {'baixo','medio','alto'}
SITUACOES = {'aberto','resolvido'}
OPCOES = {'grupo': {'Grupo Alfa','Grupo Bravo','Grupo Charlie'}, 'necessidade': {'Alimentacao','Agua','Abrigo','Higiene'}, 'observacao': {'Cenario de acolhimento simulado.','Distribuicao simulada de suprimentos.','Reposicao simulada de kits.'}, 'prioridade': PRIORIDADES, 'situacao': SITUACOES}
CAMPOS_CRIACAO = set(OPCOES)-{'situacao'}
class ValidationError(ValueError): pass

def validar_registro(dados, atualizacao=False):
    if not isinstance(dados,dict) or not dados or set(dados)-set(OPCOES):
        raise ValidationError('Campos invalidos.')
    if not atualizacao and set(dados)!=CAMPOS_CRIACAO:
        raise ValidationError('Informe os quatro campos de demonstracao.')
    limpo={}
    for k,v in dados.items():
        if not isinstance(v,str) or ' '.join(v.split()) not in OPCOES[k]:
            raise ValidationError(f'{k}: selecione uma opcao ficticia permitida.')
        limpo[k]=' '.join(v.split())
    return limpo

def validar_id(identificador):
    if type(identificador) is not int or not 1<=identificador<=4294967295:
        raise ValidationError('Identificador invalido.')
    return identificador
