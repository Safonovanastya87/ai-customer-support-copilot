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
├── knowledge_base/
│   ├── shipping_policy.md
│   ├── returns_policy.md
│   └── refund_policy.md
└── seed/

docs/
├── data/
│   └── oms_data_contract.md
│
├── product/
│   ├── acceptance_criteria.csv
│   ├── discovery.md
│   ├── non_functional_requirements.md
│   ├── scenarios.csv
│   ├── success_metrics.md
│   └── use_cases.csv
│
└── technical/
    ├── diagrams/
    │   ├── solution_architecture_flow.png
    │   └── uc_sh_02_delivery_delay_decision_flow.png
    ├── copilot_output_contract.md
    └── solution_architecture.md

scripts/
└── validate_product_docs.py

README.md
```

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

### Non-Functional Requirements

[Non-Functional Requirements](docs/product/non_functional_requirements.md)

Defines the frozen non-functional requirements for the MVP, including quality, safety, privacy, isolation, and operational constraints.

## Knowledge Base

Approved business information used by the Copilot is stored in:

- [Shipping Policy](data/knowledge_base/shipping_policy.md)
- [Returns Policy](data/knowledge_base/returns_policy.md)
- [Refund Policy](data/knowledge_base/refund_policy.md)

The Knowledge Base is the source of truth for detailed business rules used to ground shipping, return, withdrawal, and refund-related responses.

## OMS Data

The simplified Order Management System provides verified operational information for order-specific processing.

Its structure, fields, relationships, status values, payload-validation rules, and data boundaries are defined in:

[OMS Data Contract](docs/data/oms_data_contract.md)

The OMS is the source of verified operational facts. It does not define business-policy rules or Copilot routing behavior.

## Technical Design

### Solution Architecture

[Solution Architecture](docs/technical/solution_architecture.md)

Defines the Phase 3.1 high-level solution architecture, including:

- request analysis and supported Use Case assignment;
- semantic fact extraction and customer-reference resolution;
- deterministic source selection;
- Approved Knowledge Base and OMS retrieval;
- grounded processing;
- Scenario and Action determination;
- response generation, output assembly, and validation;
- the human-in-the-loop boundary;
- the cross-cutting Technical Failure Path.

The architecture includes two supporting diagrams:

- [Main Solution Architecture Flow](docs/technical/diagrams/solution_architecture_flow.png)
- [UC-SH-02 Delivery-Delay Decision Flow](docs/technical/diagrams/uc_sh_02_delivery_delay_decision_flow.png)

### Copilot Output Contract

[Copilot Output Contract](docs/technical/copilot_output_contract.md)

Defines the structured business result returned by the Copilot and the separate technical failure output.

The business result contains:

- `use_case_id`
- `scenario_id`
- `action`
- `supporting_information`
- `response_draft`

Technical failures do not produce a business Scenario or Action. They return a separate `TechnicalFailureState`.

## Runtime Information Sources

The MVP uses exactly three primary runtime information sources:

1. Customer Request
2. Approved Knowledge Base
3. Order Management System (OMS)

Customer-reported information remains distinguishable from verified OMS information.

The current processing date may be used as application processing context where required by deterministic routing, but it is not an additional runtime information source.

## Supported Copilot Actions

The Copilot uses four business handling actions:

- `ANSWER`
- `CLARIFY`
- `ESCALATE`
- `OUT_OF_SCOPE`

The exact conditions for these actions are defined in the frozen Scenarios and Acceptance Criteria and implemented through the Solution Architecture rather than duplicated in this README.

## Human-in-the-Loop

The Copilot is an internal decision-support tool.

A support employee reviews the Copilot result before any response is communicated to the customer.

Business actions requiring human handling remain under the responsibility of authorized NordShop employees.

The Copilot does not autonomously perform delivery investigations, withdrawals, returns, refunds, approvals, financial actions, or customer communication.

## Development Status

The following product and business-definition artifacts are frozen for the current MVP:

- Product Discovery
- Success Metrics
- 13 Use Cases
- 21 Scenarios
- 57 Acceptance Criteria
- Non-Functional Requirements
- Shipping Policy
- Returns Policy
- Refund Policy
- OMS Data Contract

**Phase 3.1 — Solution Architecture: CLOSED / FROZEN**

The completed Phase 3.1 baseline includes:

- high-level hybrid AI/deterministic architecture;
- end-to-end processing and decision flow;
- source-routing model;
- Scenario and Action decision model;
- human-in-the-loop boundary;
- Technical Failure Path;
- Copilot business output contract;
- separate technical failure output;
- detailed deterministic routing for `UC-SH-02`.

**Current stage: Phase 3.2 — Integration & Data Flow Design**

Phase 3.2 defines the runtime data objects, their fields, provenance, creation points, and movement between processing stages while remaining consistent with the frozen Phase 3.1 architecture.

Implementation, seed-data completion, validation, and test coverage follow the approved design baseline.
