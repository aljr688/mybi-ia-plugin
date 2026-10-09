# Configurações globais: seis abas

Leia ao orientar configurações ou gerar `formatting.dashboard`. Estas abas não são
páginas do dashboard nem o menu T. Grave somente valores solicitados/aprovados;
ausência preserva e vazio limpa/herda. Suporte no INI não comprova renderização visual.

## Aparência

Chaves aceitas em `formatting.dashboard`:

| Opção | Chave | Tipo |
| --- | --- | --- |
| Altura (modo cliente) | dashboard-altura | pixels positivos |
| Fundo | dashboard-color-background | cor |
| Título: negrito, itálico, sublinhado | dashboard-title-font-bold, dashboard-title-font-italic, dashboard-title-font-underline | booleanos |
| Título: texto, fundo, ícones | dashboard-title-font-color, dashboard-title-font-color-background, dashboard-title-icon-color | cores |
| Tamanho do título | dashboard-title-font-size | pixels positivos |
| Imagem | dashboard-image-background | caminho relativo de imagem existente |
| Modo da imagem | modo-image-background | somente default validado |
| Transparência do menu | dashboard-menu-left-background-transparency | booleano |
| Desativar limite de volumes | dlimite | booleano; explicar impacto antes de aprovar |
| Largura do menu (cliente) | leftwidth | pixels positivos |
| Fundo, ícones e título do menu | dashboard-menu-color, dashboard-menu-icon-color, dashboard-menu-text-color | cores |
| Nomes das abas, desktop/mobile | dashboard-menu-text-dash-color, dashboard-menu-text-dash-color-mobile | cores |

Booleanos são strings true/false. Cor: #RRGGBB ou rgb(R, G, B).
Imagens não são anexadas automaticamente. Área Útil ainda exige validação do contrato,
não inventar o valor. Paletas originais (global) é salva no `config.ini` da instalação,
fora do pacote. Copiar/colar formatação são ações da interface, não propriedades.

## Impressão

INI suportado: `dashboard-print-zoom` (percentual positivo),
`dashboard-print-margintop`, `dashboard-print-marginbottom`,
`dashboard-print-marginleft`, `dashboard-print-marginright` (milímetros não negativos).
Zero é válido para margens, não para zoom. Configurar não significa imprimir ou
gerar PDF. Conferir pré-visualização após importar.

## Outros

- Ocultar aba em modo cliente: `ativarproducao`, S para ocultar e N para não ocultar.
  Apesar do nome interno, S não significa publicar. A interface restringe a opção
  a administradores. Não é controle de acesso.
- Ocultar gráfico sem dados: `ocultarsdados`, S/N.
- Título do menu: `dashboard-menu-text`; subtítulo: `subtitulo-dashboard-text`.
  Texto simples até 128 caracteres, sem HTML, quebras de linha ou delimitadores INI.
- Alinhamento do menu: `dashboard-menutext-align`, left/center/right/justify.
- Ordenação: usa `dashboard_ordem.ini`, ainda fora do contrato do gerador.
  Orientar o ajuste manual; não confundir com a ordem dos itens no XML.
- Informações: texto usa `<dashboard>_infodash.memo`, ainda não gerado.
  Fornecer texto para inserir na interface, não criar chave INI fictícia.

## Configurações Componentes

Base comum do dashboard, distinta de opções específicas do menu T.
Ativação: `ativar-configuracao-geral-componente-geral`.
Chaves suportadas: `component-title-centralizar-geral`,
`component-title-font-bold-geral`, `component-title-font-italic-geral`,
`component-title-font-underline-geral`, `component-title-font-color-geral`,
`component-title-font-size-geral`, `component-title-color-icon-geral`,
`component-title-color-background-geral`, `component-color-background-geral`,
`component-aplicar-background-transparency-geral`,
`component-remover-background-transparency-title-geral`.
Booleanos true/false, tamanho positivo, cores conforme Aparência.

Ativada, a regra geral pode sobrepor valores individuais no runtime. Não prometer
que uma exceção local prevalece. Apresentar o conflito e propor desativar a regra
geral ou harmonizar valores, com aprovação. Copiar/colar são ações da interface.

## Formatações Numéricas

Interface: campo, formato Auto/General/Number/Currency/Scientific/Percent,
unidade Auto/Ones/Thousands/Millions/Billions, decimais 0–4.
Vale **por empresa**, persistida em `FieldFormats`, não no ZIP; exige recarregar.
Pode afetar outros dashboards. O gerador oferece `numericFormats` por medida no XML
(contrato.md), alternativa local e não equivalente a mudar o padrão da empresa.
Explicar o alcance e não executar banco nem inventar arquivo para esses padrões.

## Ícones

Substitui SVGs da toolbar, com botão próprio Salvar Ícones. Vazio usa o padrão;
recarregar a página para aplicar. Persistência:
`formatacoes/<dashboard>/icones_customizados.json`, não formatacao.ini.
O gerador ainda não produz esse JSON: orientar pela interface. Cor de ícone não
substitui desenho. SVG é conteúdo não confiável: não executar scripts, eventos
ou links externos embutidos. Não alegar substituição pelo pacote atual.

## Evidência e pendências

Conferido em 09/10/2026: Views/DefaultWeb/DefaultWeb.cshtml (layoutTab, printTab,
othersTab, configComponentsTab, formatNumTab, iconesTab) e
Controllers/DefaultWebController.cs (salvamento/aplicação geral e
SalvarIconesCustomizados). Contratos de persistência foram inspecionados;
homologação visual pós-importação continua necessária. Menu T será tratado
separadamente: parte comum e particularidades de cada componente.
