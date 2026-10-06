# Anas Shop AI Customer Support Copilot

## 1. Purpose

This repository contains the MLP definition for the Anas Shop AI Customer Support Copilot.

The Copilot processes supported customer-support requests, identifies the applicable Use Case, retrieves permitted approved business knowledge and verified OMS data where required, evaluates the documented business scenario, and prepares the case for Human Support.

The MLP is **not an autonomous business-action system**. It does not independently execute returns, refunds, order changes, investigations, or other restricted business actions. Normal supported processing ends in Human Support handoff, with a grounded support draft where the applicable scenario requires one.

## 2. MLP Scope

The current MLP covers four business areas:

- Order Status
- Shipping
- Returns and Withdrawal
- Refunds

The supported functionality is defined in `docs/product/use_cases.csv`.

The current product definition contains:

- 12 Use Cases
- 16 Level-5 business scenarios
- 80 Acceptance Criteria

Customer-facing language handling supports German and English according to the rules in `docs/mlp/rules/supporting_rules.md`.

## 3. Repository Structure

```text
ai-customer-support-copilot/
│
├── data/
│   └── knowledge_base/
│       ├── shipping_policy.md
│       ├── returns_policy.md
│       └── refund_policy.md
│
├── docs/
│   ├── data/
│   │   └── oms_data_contract.md
│   │
│   ├── mlp/
│   │   ├── errors/
│   │   │   ├── semantic_business_logic_error_handling.md
│   │   │   └── technical_error_handling.md
│   │   │
│   │   ├── levels/
│   │   │   ├── level_1.md
│   │   │   ├── level_2.md
│   │   │   ├── level_3.md
│   │   │   ├── level_4.md
│   │   │   ├── level_5.md
│   │   │   └── level_6.md
│   │   │
│   │   └── rules/
│   │       └── supporting_rules.md
│   │
│   └── product/
│       ├── use_cases.csv
│       ├── scenarios.csv
│       └── acceptance_criteria.csv
│
├── .gitignore
└── README.md
```

## 4. Source of Truth by Topic

Each document has one defined responsibility. Business rules should not be duplicated across files.

| Topic | Source of Truth |
|---|---|
| Supported customer intents and Use Cases | `docs/product/use_cases.csv` |
| Required customer input | `docs/product/use_cases.csv` |
| Required / conditional / optional OMS fields per Use Case | `docs/product/use_cases.csv` |
| Required business sources per Use Case | `docs/product/use_cases.csv` |
| Restricted-action safety per Use Case | `docs/product/use_cases.csv` |
| Level-5 scenario matching and Decision Result | `docs/product/scenarios.csv` |
| Testable expected behavior | `docs/product/acceptance_criteria.csv` |
| Request lifecycle, identification, routing and common MLP rules | `docs/mlp/rules/supporting_rules.md` |
| Runtime processing flow | `docs/mlp/levels/level_1.md` through `level_6.md` |
| Technical failure handling | `docs/mlp/errors/technical_error_handling.md` |
| Semantic / business-logic failure handling | `docs/mlp/errors/semantic_business_logic_error_handling.md` |
| OMS structure, field types, formats, enums and data-integrity rules | `docs/data/oms_data_contract.md` |
| Shipping business rules | `data/knowledge_base/shipping_policy.md` |
| Returns / withdrawal business rules | `data/knowledge_base/returns_policy.md` |
| Refund business rules | `data/knowledge_base/refund_policy.md` |

## 5. Runtime Flow

The MLP processing path is divided into six levels.

### Level 1 — Inbound Message and Request Handling

Receives the customer message, resolves or creates the current Request, handles communication-only messages, preserves message and attachment references, and controls serialized processing.

### Level 2 — Logical Case and Use Case Identification

Determines whether the request belongs to one logical case, identifies the supported Use Case, applies scope and precedence rules, and performs channel routing.

### Level 3 — Required Input and Authorization

Checks required customer input and, for OMS/private processing, performs the Email authorization check using the verified sender and `order_id`.

### Level 4 — Data Retrieval

Retrieves only the business sources and OMS fields permitted for the selected Use Case.

Policy retrieval follows the approved Knowledge Base.

OMS retrieval follows both:

- the field requirements in `use_cases.csv`; and
- the structural and validation rules in `oms_data_contract.md`.

### Level 5 — Business Scenario Decision

Evaluates the scenarios defined in `scenarios.csv`.

Exactly one applicable scenario must match.

Normal Level-5 business processing produces `HANDOFF_TO_SUPPORT`. `CLARIFY` is not a Level-5 action.

### Level 6 — Decision Execution

Executes the previously created Decision Result without re-evaluating the business decision.

Depending on the Decision Result, Level 6 may:

- hand the case to Human Support;
- send a clarification;
- send a communication-only response;
- send an out-of-scope response;
- redirect Webchat to Email;
- send the approved Email-access instruction.

## 6. Human Support Boundary

Human Support remains responsible for the final customer handling.

A normal handoff provides the available case context, including:

- Request context;
- relevant customer message references;
- attachment references unchanged;
- permitted verified OMS facts where available;
- approved Policy context where applicable;
- the Decision Reason;
- a support draft when required and reliably producible.

A support draft is never automatically sent to the customer.

If a reliable grounded draft cannot be produced without speculation, the handoff still proceeds without the draft.

Technical Escalation also transfers the **customer case**, not only a technical incident.

## 7. Key Safety Boundaries

The MLP follows these boundaries:

- OMS/private data is accessed only after successful authorization.
- Webchat does not perform OMS/private retrieval.
- Only OMS fields permitted for the selected Use Case may be exposed to the Copilot path.
- Customer-reported information remains distinguishable from verified OMS facts.
- Attachments are retained as references and forwarded unchanged; Copilot does not OCR, interpret, or analyze attachment contents.
- Copilot does not autonomously execute return or refund actions.
- Missing information must not be invented.
- A technical failure must not be converted into an unsupported business answer.
- A semantic/business-rule conflict must not be resolved by arbitrarily choosing a result.

## 8. OMS Data Rules

`docs/data/oms_data_contract.md` defines the normalized OMS interface used by the MLP.

The contract defines:

- supported fields;
- data types;
- date and monetary formats;
- allowed enum values;
- null / empty-value handling;
- order/item integrity;
- invalid payload handling;
- the distinction between business `INSUFFICIENT` and Technical Error.

`use_cases.csv` remains the source of truth for whether an OMS field is Required, Conditional, Optional, or not permitted for a specific Use Case.

## 9. Knowledge Base

The approved Knowledge Base contains the business-policy rules used by the MLP:

- `shipping_policy.md`
- `returns_policy.md`
- `refund_policy.md`

The Policies define business rules. They do not define runtime routing, authorization, Request lifecycle, or technical error behavior.

A Policy is used only where the selected Use Case declares it as a required source.

## 10. Product Definition

### Use Cases

`docs/product/use_cases.csv` defines what the Copilot supports.

Each Use Case specifies, among other things:

- customer intent;
- business goal;
- permitted data sources;
- Policy scope;
- required customer input;
- required / conditional / optional OMS fields;
- restricted-action safety behavior.

### Scenarios

`docs/product/scenarios.csv` defines the Level-5 business-state evaluation for supported Use Cases.

Scenario rules must be complete and mutually exclusive for the applicable path.

### Acceptance Criteria

`docs/product/acceptance_criteria.csv` translates the current MLP definition into testable Given / When / Then behavior.

The criteria cover:

- global and cross-level behavior;
- Use Case identification and safety boundaries;
- all current Level-5 scenarios.

## 11. Recommended Reading Order

For a new project participant, the recommended order is:

1. `README.md`
2. `docs/product/use_cases.csv`
3. `docs/product/scenarios.csv`
4. `docs/mlp/levels/level_1.md` through `level_6.md`
5. `docs/mlp/rules/supporting_rules.md`
6. `data/knowledge_base/` Policies
7. `docs/data/oms_data_contract.md`
8. `docs/mlp/errors/`
9. `docs/product/acceptance_criteria.csv`

## 12. MLP Boundaries

The current documentation intentionally does not define every production implementation detail.

Examples of implementation/deployment details that may be fixed later include:

- exact PROCESSING timeout;
- exact AWAITING_CUSTOMER TTL;
- concrete Human Support queue/address;
- infrastructure-specific retry timing;
- production observability and deployment configuration.

These details must not change the documented business behavior, safety boundaries, or source-of-truth responsibilities above.
