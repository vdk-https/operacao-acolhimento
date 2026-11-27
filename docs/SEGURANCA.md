# Segurança e limitações
- Dados exclusivamente sintéticos e opções fixas; sem nomes, documentos, nacionalidade, endereço, posição, rotas ou texto livre.
- Filtros MongoDB fixos e valores validados contra injeção NoSQL; campos atualizáveis em lista permitida. Limite de JSON de 4096 bytes.
- Chave de edição comparada em tempo constante; segredo em .env; consultas locais sem autenticação, pois não há dados reais.
- Flask sem debug e TCP limitado ao localhost; logs rotativos sem chave ou conteúdo de registros.
- Interface renderiza valores por textContent. Open-Meteo recebe coordenadas fixas não associadas a grupos.
- Não é adequado para operação real. Não há controle de acesso por usuário, TLS, gestão de consentimento, verificação de elegibilidade ou avaliação de impacto.
