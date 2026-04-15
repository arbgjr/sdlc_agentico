# Synthetic Architecture Overview

components:
  - name: api-gateway
  - name: payment-service
  - name: order-service

technology_choices:
  api: FastAPI
  message_bus: RabbitMQ
  storage: PostgreSQL

nfr_approach:
  latency: p95 < 250ms via async dispatch
  availability: 99.9% with circuit breakers
