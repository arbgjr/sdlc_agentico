# Technical Plan — Checkout

## Components touched
- payment-service: add PIX adapter
- order-service: extend status machine

## Sequence
1. Selector returns provider_id=pix
2. payment-service.create_charge() returns QR
3. webhook → order-service.confirm()
