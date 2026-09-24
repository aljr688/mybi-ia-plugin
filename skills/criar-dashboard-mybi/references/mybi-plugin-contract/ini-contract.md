# INI — perfil confirmado

Seção [dashboard1] usa o nome do XML sem extensão; seção individual
[dashboard1_item1] acrescenta o ComponentName. O nome deve acompanhar o XML-base.
O gerador atual escreve dashboard-image-background=../SystemImages/back.png,
modo-image-background=default, ativar-configuracao-geral-componente-geral=true,
component-aplicar-background-transparency-geral=true,
component-remover-background-transparency-title-geral=false e
component-title-font-color-geral=#FFFFFF (ou appearance.titleColor).
Cards recebem background-transparency=true, remove-background-transparency-title=false
e title-font-size-conteudo=26. A imagem precisa existir na instalação, não vai no ZIP.

No runtime, cor/tamanho/itálico/negrito/sublinhado/fundo do título aceitam opções
individuais. A opção geral não vazia prevalece quando a configuração geral está ativa.
O gerador ainda não serializa essas opções adicionais. Limites e valores padrão da
interface não foram confirmados; ausência de configuração preserva o estilo padrão.
