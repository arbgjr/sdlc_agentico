# Technical Plan — PIX Payment Integration

## Components
- payment-service: signs outbound, validates inbound callbacks
- order-service: consumes payment_confirmed events

## Flows
1. Client hits payment-service, receives QR code
2. PIX provider sends async callback on successful payment
3. payment-service publishes payment_confirmed
4. order-service marks order paid
