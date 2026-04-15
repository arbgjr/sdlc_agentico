# Checkout Feature Spec

## Problem
Customers cannot complete a purchase via PIX.

## Solution
Add a PIX option in the checkout payment selector that triggers the
PIX integration described in ADR-014.

## Acceptance criteria
- User can select PIX as payment method
- QR code is generated within 2s p95
- Payment confirmation arrives within 30s
