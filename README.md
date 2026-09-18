# MyBI IA

Plugin de criação de dashboards MyBI. Identificador técnico: mybi-dashboard.
Contém a mesma Skill criar-dashboard-mybi distribuída para instalação direta.
Não conecta ao MyBI nem publica dashboards; entrega XML/ZIP para importação.
Não possui MCP, hooks, autenticação ou chamadas a APIs de modelos.

## Uso

Peça para criar um dashboard MyBI e informe os campos e o formato desejado.
Siga as propostas e aprovações da Skill antes da geração. Para fonte existente,
forneça também o XML-base conforme solicitado. Não envie senhas ou credenciais.
O ambiente precisa executar Python 3.10+; JavaScript automático requer Node.js
para validação de sintaxe. Consulte skills/criar-dashboard-mybi/references/contrato.md
para limites do catálogo e geração. Consulta aos manuais depende de acesso web.

## Teste local do plugin

Depois de extrair este ZIP numa pasta mybi-dashboard:

    claude plugin validate ./mybi-dashboard
    claude --plugin-dir ./mybi-dashboard

Em Claude Code, a Skill é invocada como /mybi-dashboard:criar-dashboard-mybi.
A instalação direta como Skill usa o outro ZIP, Skill-MyBI-IA-Claude.
Não instale as duas variantes simultaneamente no mesmo ambiente sem necessidade.

## Distribuição

Este pacote não é um dashboard para importar no MyBI nem comprova aprovação
pela Anthropic. A submissão ao catálogo é feita separadamente. Se o formulário
exigir repositório, publique somente o conteúdo deste pacote num repositório
dedicado autorizado, nunca o projeto completo BIWebIA ou dados de clientes.
Logo para identificação visual: assets/logo-ia.svg.
