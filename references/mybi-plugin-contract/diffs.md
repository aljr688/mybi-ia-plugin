# Diferenças das fixtures

Exemplos sintéticos, não destinados a dados reais. Base: dashboard-padrao.xml.md e
formatacao-padrao.ini.md. Não representam aprovação do usuário em uma conversa.
- dashboard-cor-titulo.ini.md: somente component-title-font-color-geral muda de
  #FFFFFF para #112233, escopo títulos. Reverter para #FFFFFF.
- dashboard-formatacao-numerica.xml.md: somente NumericFormat passa de Number para
  Currency com CurrencyCultureName=pt-BR; precisão permanece 2. Reverter removendo
  CurrencyCultureName e definindo FormatType=Number. Escopo medida Receita.
Confirmados pela serialização local; importação/renderização não testadas.
Fixtures de propriedades ainda não suportadas não foram inventadas.
