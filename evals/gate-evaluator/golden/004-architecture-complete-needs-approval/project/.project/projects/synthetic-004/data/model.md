# Data Model

entities:
  - name: Order
    fields: [id, customer_id, total_cents, status, created_at]
  - name: Payment
    fields: [id, order_id, provider, status, provider_ref]
