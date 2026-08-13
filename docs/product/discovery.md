# Product Discovery

## Business Context

NordShop GmbH is a fictional German e-commerce company.

The Customer Support department has approximately 60 employees.
Customers contact support via email and web chat.

Support employees currently need to search across several sources
when answering customer requests.

## Business Problem

The project aims to:

- reduce customer request handling time;
- improve consistency of customer responses;
- improve support quality;
- enable increasing support volume without proportional staff growth.

Staff reduction is not an explicit goal of the MVP.

## Users

The primary users are Customer Support employees.

The AI system is an internal copilot and does not communicate
directly with customers in the MVP.

## MVP Scope

Initial supported topics:

- Shipping
- Returns
- Refund Policy
- Order Status

Supported customer languages:

- German
- English

The response should normally be generated in the customer's language.

## Expected System Behaviour

The assistant should:

- analyse customer requests;
- use internal company policies;
- use order information when required;
- generate a suggested customer response;
- show the business sources used for the response;
- indicate when available information is insufficient;
- allow the support employee to review and edit the response.

If the customer's intent cannot be determined reliably,
the system should not invent an answer. It should request
clarification or recommend escalation.

## Out of Scope

The AI must not autonomously:

- issue refunds;
- cancel orders;
- modify orders;
- modify customer data;
- perform financial transactions;
- communicate directly with customers.

## Known Information Sources

### Customer Request

Free-text customer message.

Possible information:

- language;
- customer intent;
- order ID, if provided;
- description of the problem;
- additional customer-provided context.

Customer statements are not considered authoritative for the
actual order status.

### Knowledge Base

Current known documents:

- Shipping Policy;
- Returns Policy;
- Refund Policy.

These contain company rules, procedures, exceptions and
business conditions.

### Order Management System

Currently known fields:

- order_id
- customer_id
- order_date
- shipment_status
- estimated_delivery_date
- delivered_at
- tracking_number
- items
- total_amount

### Historical Support Requests

Historical customer requests exist, but their quality and
availability have not yet been assessed.

They are therefore not a required information source for the MVP.

## Open Questions

- What exactly constitutes insufficient information?
- Which criteria define an acceptable AI-generated response?
- What is the complete list of business-critical cases?
- Which additional order data may be required for refund decisions?
- Which cases require mandatory escalation?
- Which information should be shown to employees as answer sources?