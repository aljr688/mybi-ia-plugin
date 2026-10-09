# Menu T e ações do dashboard

Use `configuracoes-inventario.json` para localizar os controles declarados e os
33 ícones pelo label/ID. Há condições de visibilidade por tipo e permissão: a mesma
aba não mostra todas as opções para todo componente. Não deduzir a ação só pelo desenho.

## Parte comum do T

Formatação Comum: título (estilo, texto/fundo, tamanho, cor dos ícones, alinhamento),
rótulos/conteúdo e cabeçalho de tabela quando aplicável, fundo/transparência, imagem,
modo de imagem, aplicação ao título, tamanho mobile e texto do botão de informações.
Para geração, usar somente chaves aceitas por mybi_formatting.py e personalizacao.md.
Mobile/tooltip e controles não aceitos ainda exigem ajuste manual: não inventar INI.
Configuração geral ativada pode sobrepor a formatação local; consultar
configuracoes-dashboard.md antes de prometer uma exceção por componente.

## Parte específica

Configuração pode incluir rolagem e recursos próprios de grade, gráficos e outros
tipos; Escala aparece quando aplicável. Pop-up, Alertas e Prompts IA são abas distintas,
não parte dos bindings do modelo. Localize o controle em configuracoes-inventario.json.
As opções do motor do componente também estão em toolbar-inventory.json, na entrada
do componente, em options/customProperties. Consulte ambos, não copie a configuração
de um componente para outro apenas porque compartilham o motor JavaScript.
Documentação de controles não autoriza executar serviços nem garante serialização.
Alertas, destinos de notificações, pop-ups e prompts sem contrato explícito devem
ser orientados na interface; não prometer que foram ativados pelo pacote.

## Ações principais

- Maximizar: tela cheia. Tema: esquema de cores.
- Imprimir: impressão/exportação PDF; não confundir com gerar um ZIP.
- Enviar por e-mail: abre configuração/agendamento; não envia pelo plugin offline.
- Snapshots: histórico dos dados; não confundir com imagem de referência.
- Gerenciar Painel: atualização e rodízio.
- Filtros Mestre: salvar/remover filtros; Limpar Filtros é outra ação.
- Atualizar: recarregar dados no MyBI. Configurações: seis abas globais.
- Formatação/T: opções do componente. Informação: texto de ajuda cadastrado.
- Copiar/Colar Formatação: ações de estilo. Ajuda, Log e Abrir Projeto são ações próprias.
- Ícones de IA (segmentação, finanças, recompra, ações, estoque, anomalias,
  afinidade, previsão, saúde, apresentação, correlação, tendência, agentes/sugestão)
  encaminham funcionalidades do MyBI. Explicar a finalidade nominal, sem afirmar
  que o plugin offline executa essas funções ou dispõe de credenciais do servidor.

Se só houver um print, diferencie o que é legível do que exige tooltip/versão instalada.
Para aplicar uma opção fora do contrato, peça configuração/exportação pertinente;
nunca renomeie controles ou invente uma configuração para esconder a limitação.
