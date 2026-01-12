# Política de RAG local

Objetivo
- Reforçar evidência quando solicitado
- Ajudar justificativas quando fracas

Não permitido
- Decidir padrões via RAG
- Inventar requisitos via RAG
- Citar sem indicar a origem do trecho

Fluxo
1. Colocar documentos markdown sob um diretório local do repo, por exemplo docs/
2. Rodar rag_ingest para gerar chunks
3. Rodar rag_search para recuperar trechos
4. Ao citar, indicar o id do chunk e o caminho do arquivo

Observação
O RAG aqui é deliberadamente simples para não depender de ferramentas externas.
Se você tiver MCP tools de busca vetorial, este é o ponto de integração.
Skills ensinam como usar ferramentas. MCP fornece ferramentas. :contentReference[oaicite:15]{index=15}
