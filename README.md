# MyBI IA — 0.1.25

Mesmas instruções, exemplos e referências para GPT e Claude. Geração direta de XML
pelo modelo, sem Python, Node, executáveis, MCP, conexão de banco ou API de IA incluídos.
Os manifestos e o formato de instalação são específicos de cada plataforma.

Peça um dashboard MyBI, informe campos/referência e aprove a proposta. Para editar
fonte existente, forneça o XML exportado. O modelo usa as ferramentas de arquivos do
chat para produzir XML/ZIP; a disponibilidade dessas ferramentas depende do ambiente.
Consulte skills/criar-dashboard-mybi/SKILL.md e references/geracao-direta.md na skill.
Não há validador determinístico incluído: teste importação/renderização no MyBI.
Este ZIP é um plugin, não um dashboard para importar no MyBI.

No Claude Code, extraia o plugin e use `claude --plugin-dir ./mybi-dashboard`.
O ZIP Skill-MyBI-IA-Claude é a alternativa de instalação direta como skill.
Não instale ambas as variantes juntas. No GPT, envie o ZIP de plugin no portal.
A publicação/revisão no catálogo é separada; este pacote não comprova aprovação.

Licença MIT (LICENSE), sem conceder direitos sobre o software MyBI ou suas marcas.
