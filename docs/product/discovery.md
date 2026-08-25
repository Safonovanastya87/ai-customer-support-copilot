# Product Discovery

## 1. Product Overview

The NordShop Customer Support Copilot is a Generative AI assistant for customer support employees of the fictional German e-commerce company NordShop GmbH.

The Copilot helps support employees:

- understand customer requests;
- identify the relevant supported customer intent;
- retrieve relevant approved business information;
- retrieve verified operational information where required;
- determine the appropriate handling path;
- prepare grounded customer-facing response drafts.

The Copilot is an internal human-in-the-loop decision-support system. It does not communicate directly with customers.

## 2. Business Context

NordShop receives approximately 30,000–40,000 customer requests per month.

The support organization consists of approximately 60 employees.

Customer requests are mainly received through:

- email;
- web chat.

Most requests are in German, with a smaller share in English.

Support employees currently spend significant time interpreting requests, searching for relevant policies, retrieving operational information, determining the appropriate support process, and preparing repetitive responses.

Increasing support volume without proportional growth in support staffing is therefore a relevant business objective.

## 3. Business Problem

Customer support employees often need to combine information from multiple sources before they can respond reliably.

Depending on the request, handling may require:

1. understanding the customer intent;
2. identifying the relevant business case;
3. retrieving approved policy information;
4. retrieving verified operational information;
5. determining the appropriate handling path;
6. preparing a customer-facing response.

This manual process increases handling effort and can lead to inconsistent responses.

## 4. Business Goal

The primary business goals are to:

- reduce customer request handling time;
- improve response consistency;
- maintain or improve support quality;
- increase the number of requests handled by the existing support organization;
- support increasing request volume without proportional staff growth.

Reducing staff is not an MVP objective.

## 5. Product Goal

The MVP combines customer requests, approved business knowledge, and verified operational information to support customer service employees in handling supported requests consistently and efficiently.

The intended output is:

- a recommended handling action;
- relevant supporting information;
- a grounded customer-facing response draft where appropriate.

The support employee remains responsible for reviewing the result and sending the final response.

## 6. Target Users

The primary users are NordShop customer support employees.

The MVP is not a public customer chatbot. Customers do not interact directly with the Copilot.

## 7. MVP Scope

The MVP supports customer requests in the following business areas:

- Order Status;
- Shipping;
- Returns and Withdrawal;
- Refunds.

The detailed supported functionality and routing boundaries are defined in:

- `docs/product/use_cases.csv`;
- `docs/product/scenarios.csv`;
- `docs/product/acceptance_criteria.csv`.

Detailed business rules are defined in the approved Knowledge Base policies.

Business processes that do not map to the supported MVP functionality are outside the current product scope.

## 8. Supported Languages

The MVP supports customer requests in:

- German;
- English.

Detailed handling of unsupported language input is defined in the product scenarios and acceptance criteria.

## 9. Human-in-the-Loop Principle

The Copilot supports, but does not replace, the customer support employee.

A human employee reviews the Copilot result before anything is communicated to the customer.

Business actions requiring human handling remain under the responsibility of authorized NordShop employees.

## 10. Information Sources

The MVP uses three primary runtime information sources:

1. Customer Request
2. Approved Knowledge Base
3. Order Management System (OMS)

The Approved Knowledge Base contains the business information used for shipping, returns, withdrawal, and refund-related responses.

The OMS provides verified operational information required for order-specific processing.

Detailed business rules belong to the Knowledge Base. Detailed operational fields and relationships belong to the OMS Data Contract.

## 11. Product Principles

The MVP follows these high-level principles:

- use approved business information and verified operational information where required;
- keep customer-reported information distinguishable from verified system information;
- do not invent unavailable information;
- route cases requiring human handling rather than pretending an action has been completed;
- keep the support employee in control of the final customer communication.

Detailed routing behavior is defined in the frozen Scenarios and Acceptance Criteria.

## 12. MVP Non-Goals

The MVP does not aim to:

- replace customer support employees;
- communicate directly with customers;
- autonomously execute business or financial actions;
- support business processes outside the defined MVP scope.

## 13. Product Outcome

The intended MVP outcome is a support copilot that can:

1. understand customer requests within the supported scope;
2. retrieve relevant approved and verified information;
3. determine the appropriate handling path;
4. prepare grounded response drafts where appropriate;
5. keep the support employee in control.

## 14. Related Product Documentation

- [Success Metrics](success_metrics.md)
- [Use Cases](use_cases.csv)
- [Scenarios](scenarios.csv)
- [Acceptance Criteria](acceptance_criteria.csv)
- [OMS Data Contract](../data/oms_data_contract.md)

Approved business knowledge is maintained separately in:

- `data/knowledge_base/shipping_policy.md`
- `data/knowledge_base/returns_policy.md`
- `data/knowledge_base/refund_policy.md`
