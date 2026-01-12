# Pattern: Large Files (Arquivos Grandes)

## Sinais de Identificacao

- Upload de arquivos grandes (>10MB)
- Download pesado
- Alto consumo de banda
- Videos, imagens em alta resolucao, backups

## Perguntas Obrigatorias

1. **Qual o tamanho medio e maximo dos arquivos?**
   - MB? GB? TB?
   - Define estrategia de upload

2. **O backend precisa processar os bytes?**
   - Apenas armazenar?
   - Ou precisa transformar/validar?

3. **O upload precisa ser retomavel?**
   - Conexao instavel?
   - Arquivos muito grandes?

## Opcoes de Decisao

### Upload Direto para Object Storage
- **Como funciona**: Cliente envia direto para S3/GCS/Azure Blob
- **Quando usar**: Backend nao precisa processar bytes
- **Trade-off**: Eficiente mas menos controle

### Multipart Upload
- **Como funciona**: Arquivo dividido em partes, enviadas separadamente
- **Quando usar**: Arquivos grandes, upload retomavel necessario
- **Trade-off**: Retomavel mas complexidade de gerenciar partes

### URLs Assinadas (Presigned URLs)
- **Como funciona**: Backend gera URL temporaria para upload/download
- **Quando usar**: Controle de acesso + upload direto
- **Trade-off**: Seguro e eficiente, padrao recomendado

### Streaming via Backend
- **Como funciona**: Backend recebe e repassa para storage
- **Quando usar**: Precisa processar/validar durante upload
- **Trade-off**: Mais controle mas backend vira gargalo

## Fluxo Recomendado (Presigned URL)

```
1. Cliente solicita upload ao backend
2. Backend valida permissao
3. Backend gera presigned URL (PUT) com expiracao
4. Cliente faz upload direto para object storage
5. Object storage notifica backend (webhook) ou cliente confirma
6. Backend registra metadata
```

## Modos de Falha Comuns

| Falha | Causa | Mitigacao |
|-------|-------|-----------|
| Backend como proxy | Todo trafego passa pelo backend | Upload direto com presigned URL |
| Upload sincrono | Request timeout em arquivos grandes | Multipart ou async |
| Sem retentativa | Falha no meio perde tudo | Multipart upload retomavel |
| URLs sem expiracao | URLs vazam e sao reusadas | Presigned com TTL curto |

## Otimizacoes

- **Compressao**: Comprimir antes de enviar (gzip, brotli)
- **Chunking**: Dividir em partes para paralelismo
- **CDN para download**: Servir arquivos via CDN
- **Lifecycle policies**: Mover para storage frio apos tempo

## Exemplo de Decisao

**Cenario**: Plataforma de video com upload de arquivos ate 5GB

**Analise**:
- Tamanho: ate 5GB
- Backend nao processa bytes (apenas metadata)
- Upload deve ser retomavel (conexao movel)

**Decisao**: Multipart Upload com Presigned URLs para S3
- Cliente solicita upload, backend gera presigned URL
- Upload multipart em chunks de 100MB
- Se falhar, retoma do ultimo chunk
- Webhook do S3 notifica backend ao completar
- CDN (CloudFront) para servir videos
- Trade-off aceito: complexidade de multipart em troca de reliability
