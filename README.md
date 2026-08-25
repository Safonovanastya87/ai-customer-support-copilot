# AI Customer Support Copilot

Generative AI copilot for assisting customer support employees in the fictional German e-commerce company NordShop GmbH.

The Copilot helps support employees understand customer requests, retrieve relevant approved business information and verified operational data, determine the appropriate handling path, and prepare grounded response drafts.

The system follows a human-in-the-loop approach: the Copilot supports the employee but does not communicate directly with customers or autonomously perform business actions requiring human handling.

## Business Goal

Reduce customer request handling time, improve response consistency and quality, and support increasing request volume while keeping human support employees in control.

## MVP Scope

The MVP covers:

- Order Status
- Shipping
- Returns and Withdrawal
- Refunds

Supported customer-request languages:

- German
- English

Detailed supported functionality and routing boundaries are defined in the product documentation. Detailed business rules are defined in the approved Knowledge Base policies.

## Product Definition

The product requirements are organized in three levels:

1. **Use Cases** — supported functional capabilities
2. **Scenarios** — UC-specific functional paths and reusable global handling situations
3. **Acceptance Criteria** — testable expected behavior

The frozen product definition contains:

- 13 Use Cases
- 21 Scenarios
- 57 Acceptance Criteria

## Repository Structure

```text
data/
└── knowledge_base/
    ├── shipping_policy.md
    ├── returns_policy.md
    └── refund_policy.md

docs/
├── data/
│   └── oms_data_contract.md
│
└── product/
    ├── acceptance_criteria.csv
    ├── discovery.md
    ├── scenarios.csv
    ├── success_metrics.md
    └── use_cases.csv

README.md
```

Seed data and test artifacts are intentionally not included in the frozen documentation set yet. They will be created after the product, policy, and OMS definitions have been finalized.

## Product Documentation

### Product Discovery

[Product Discovery](docs/product/discovery.md)

Describes the business problem, product goal, target users, MVP scope, information sources, and high-level product principles.

### Success Metrics

[Success Metrics](docs/product/success_metrics.md)

Defines how the usefulness, quality, safety, adoption, and operational performance of the MVP will be evaluated.

### Use Cases

[Use Cases](docs/product/use_cases.csv)

Defines the supported functional capabilities of the Copilot.

### Scenarios

[Scenarios](docs/product/scenarios.csv)

Defines UC-specific scenarios and reusable global handling scenarios.

### Acceptance Criteria

[Acceptance Criteria](docs/product/acceptance_criteria.csv)

Defines the testable expected behavior for the frozen scenario set.

## Knowledge Base

Approved business information used by the Copilot is stored in:

- [Shipping Policy](data/knowledge_base/shipping_policy.md)
- [Returns Policy](data/knowledge_base/returns_policy.md)
- [Refund Policy](data/knowledge_base/refund_policy.md)

The Knowledge Base is the source of truth for detailed business rules used to ground shipping, return, withdrawal, and refund-related responses.

## OMS Data

The simplified Order Management System provides verified operational information for order-specific processing.

Its structure, fields, relationships, status values, and data boundaries are defined in:

[OMS Data Contract](docs/data/oms_data_contract.md)

The OMS is the source of verified operational facts. It does not define business-policy rules or Copilot routing behavior.

## Runtime Information Sources

The MVP uses three primary runtime information sources:

1. Customer Request
2. Approved Knowledge Base
3. Order Management System (OMS)

Customer-reported information remains distinguishable from verified OMS information.

## Supported AI Actions

The Copilot uses four handling actions:

- `ANSWER`
- `CLARIFY`
- `ESCALATE`
- `OUT_OF_SCOPE`

The exact conditions for these actions are defined in the frozen Scenarios and Acceptance Criteria rather than duplicated in this README.

## Human-in-the-Loop

The Copilot is an internal decision-support tool.

A support employee reviews the Copilot result before any response is communicated to the customer.

Business actions requiring human handling remain under the responsibility of authorized NordShop employees.

## Development Status

The following documentation layers are frozen for the current MVP:

- Product Discovery
- Success Metrics
- 13 Use Cases
- 21 Scenarios
- 57 Acceptance Criteria
- Shipping Policy
- Returns Policy
- Refund Policy
- OMS Data Contract

A full cross-document consistency review has been completed for the frozen documentation set.

The next project stage is the creation of seed data, validation/test coverage, and implementation artifacts based on these frozen definitions.
