# Data Model

entities:
  - name: Order
    fields: [id, customer_id, total_cents, status]
  - name: Payment
    fields: [id, order_id, provider, status, provider_ref, customer_cpf]
    sensitive_fields: [customer_cpf]   # PII
