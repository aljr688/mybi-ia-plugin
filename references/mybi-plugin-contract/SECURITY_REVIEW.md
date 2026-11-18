> Versão 0.1.25: este contrato descreve estruturas e limites MyBI. Menções ao gerador/compilador e opções de linha de comando são contexto histórico; não execute esses comandos. Use geração direta e revisão conforme references/geracao-direta.md (a partir da raiz da skill).

# Revisão de distribuição

Inspecionados todos os arquivos listados no MANIFEST.json. Revisão textual das oito
páginas convertidas e varredura automática por padrões de segredos, conexões,
endereços privados, caminhos locais e referências internas: sem ocorrências.
Nenhum código-fonte da aplicação, dados de clientes ou arquivo original da aplicação
foi copiado para esta pasta. Exemplos de XML/INI são sintéticos, gerados pelo serializador
portátil. A varredura por padrões não é garantia absoluta de ausência de segredos.

Revisão humana ainda necessária: propriedades que excedem o perfil do gerador,
lacunas de unknowns.md e renderização/importação. O pacote é referência parcial;
não certifica o inventário integral nem habilita propriedades não implementadas.
O ZIP final é apenas o plugin GPT, não uma publicação automática.
