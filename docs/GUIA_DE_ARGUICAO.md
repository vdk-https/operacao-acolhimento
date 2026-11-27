# Arguição
**Problema:** dispersão de solicitações humanitárias em cenário simulado.
**Solução:** painel web, API REST e MongoDB com operações CRUD.
**Estruturas:** dicionários Python representam objetos JSON; conjuntos definem opções permitidas; listas representam registros.
**Rede:** HTTP para API, TCP local para contagem e HTTPS para consulta meteorológica externa.
**Segurança:** validação por allowlist, Filtros MongoDB fixos e valores validados contra injeção NoSQL, chave de edição, limite de payload e logs.
**Privacidade:** não há dados reais nem localização de refugiados. Os grupos Alfa, Bravo e Charlie são rótulos sintéticos.
**Limitações:** prioridade é selecionada manualmente, não é triagem real. Clima é contextual e não está ligado a qualquer grupo. Os testes mockados não comprovam integração real.
