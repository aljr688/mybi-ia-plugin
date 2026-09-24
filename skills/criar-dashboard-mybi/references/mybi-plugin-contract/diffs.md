# Diferenças das fixtures

Exemplos sintéticos, não destinados a dados reais. Base: dashboard-padrao.xml e
formatacao-padrao.ini. Não representam aprovação do usuário em uma conversa.
- dashboard-cor-titulo.ini: somente component-title-font-color-geral muda de
  #FFFFFF para #112233, escopo títulos. Reverter para #FFFFFF.
- dashboard-formatacao-numerica.xml: somente NumericFormat passa de Number para
  Currency com CurrencyCultureName=pt-BR; precisão permanece 2. Reverter removendo
  CurrencyCultureName e definindo FormatType=Number. Escopo medida Receita.
Confirmados pela serialização local; importação/renderização não testadas.
Fixtures de propriedades ainda não suportadas não foram inventadas.
