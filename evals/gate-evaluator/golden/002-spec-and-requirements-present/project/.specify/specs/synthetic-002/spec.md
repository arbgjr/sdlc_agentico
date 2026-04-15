---
spec_id: synthetic-002
status: approved
created_at: 2026-04-15T00:00:00Z
constitution_version: "1.0.0"
applicable_principles: [II, III, VIII]
clarify_rounds_completed: 1
last_clarified_at: 2026-04-15T00:00:00Z
---

# Checkout Feature Spec

## Problem
Customers cannot complete a purchase via PIX.

## Solution
Add a PIX option in the checkout payment selector that triggers the
PIX integration described in ADR-014.

## Acceptance criteria

- given: a customer at checkout
  when: they select PIX
  then: a QR code is displayed within 2 seconds

- given: the QR code was scanned and paid
  when: the bank confirms the payment
  then: the order is marked paid within 30 seconds
