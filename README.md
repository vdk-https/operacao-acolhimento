# Operação Acolhimento — GS CitizenTech

Protótipo acadêmico de uma missão militar de assistência humanitária a refugiados. Organiza solicitações fictícias de alimentação, água, abrigo e higiene. Não identifica, rastreia ou classifica pessoas reais. Não é ferramenta de comando militar, registro oficial ou resposta emergencial.

## Problema e solução
Em uma crise humanitária, solicitações de necessidades básicas podem se perder em registros dispersos. O protótipo centraliza solicitações de grupos simulados, com prioridade declarada e situação de atendimento. ODS 10 e 16. Não houve pesquisa de campo; trata-se de hipótese de projeto.

## Instalação (Windows)
Requer Python 3.10+ e MySQL 8+ em execução. No PowerShell, dentro desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```
No MySQL Workbench, execute `sql/schema.sql`. Em seguida, execute os comandos abaixo, substituindo a senha de exemplo:

```sql
CREATE USER 'acolhimento'@'127.0.0.1' IDENTIFIED BY 'SENHA_FORTE_LOCAL';
GRANT SELECT, INSERT, UPDATE, DELETE ON acolhimento_db.* TO 'acolhimento'@'127.0.0.1';
```
Edite `.env` com a mesma senha e gere uma chave aleatória com `python -c "import secrets; print(secrets.token_urlsafe(32))"`. Coloque a chave em API_WRITE_TOKEN. Execute `python app.py` e abra http://127.0.0.1:5000. Cole a chave no formulário para editar. A base inicia vazia. Não reutilize dados pessoais.

## API REST
| Método | Rota | Função |
|---|---|---|
| GET | /api/registros | Listar (filtro opcional grupo) |
| GET | /api/registros/1 | Consultar |
| POST | /api/registros | Criar |
| PUT | /api/registros/1 | Atualizar parcialmente |
| DELETE | /api/registros/1 | Excluir |
| GET | /api/clima | Previsão de referência fixa em São Paulo |
| GET | /health | Estado do processo Flask |

POST, PUT e DELETE exigem X-API-Key. Exemplo JSON: `{"grupo":"Grupo Alfa","necessidade":"Agua","observacao":"Cenario de acolhimento simulado.","prioridade":"alto"}`. Situação padrão: aberto; pode ser alterada para resolvido. A interface permite editar a situação; a API permite editar os demais campos autorizados.

## Rede, arquivos e testes
Em outro terminal com ambiente virtual ativo, execute `python tcp_status_server.py`; em um terceiro, `python tcp_status_client.py`. O socket local retorna apenas a quantidade de registros. Os logs rotativos ficam em logs/acoes.log. Execute `python -m pytest tests -v` para testes isolados; repositório e clima são simulados nos testes da API. Faça também teste real com MySQL, navegador, Open-Meteo e TCP. Não exponha o protótipo na rede.

## Evidências
Não há prints reaproveitados do AlertaBairro. Capture as telas reais após executar: painel inicial, cadastro, atualização para atendido, exclusão ou resposta TCP. Consulte docs/ROTEIRO_DEMO.md.
