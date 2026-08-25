# Copilot Output Contract

## 1. Purpose

This document defines the structured business result produced by the NordShop Customer Support Copilot for one processed customer request.

The contract defines how the Copilot communicates its handling result to the support workflow.

It does not define:

- customer-intent classification rules;
- business-policy rules;
- OMS data rules;
- routing conditions;
- prompt implementation;
- model reasoning;
- transport protocol or API design.

Those concerns are defined in the applicable product, Knowledge Base, data, and solution-design documentation.

## 2. Output Model

The Copilot business result contains five fields:

```json
{
  "use_case_id": "UC-SH-02",
  "scenario_id": "SC-SH-02B",
  "action": "ESCALATE",
  "supporting_information": [
    {
      "source_type": "OMS",
      "information": "Shipment status is SHIPPED."
    }
  ],
  "response_draft": null
}
```

## 3. Top-Level Fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `use_case_id` | string or null | yes | Identified supported Use Case when one has been reliably identified |
| `scenario_id` | string | yes | Frozen Scenario that determines the handling result |
| `action` | enum | yes | Handling action selected for the request |
| `supporting_information` | array | yes | Relevant grounded information made available to the support employee |
| `response_draft` | string or null | yes | Grounded customer-facing draft when appropriate |

These fields form the required business-result payload for the MVP.

Technical transport or observability metadata may be added during solution design, for example a request identifier or processing timestamp, provided that such metadata does not change the semantics of the business-result fields defined in this contract.

## 4. `use_case_id`

`use_case_id` contains one frozen Use Case identifier when a supported Use Case has been reliably identified.

Example:

```json
"use_case_id": "UC-RT-05"
```

The field is `null` when no supported Use Case has been reliably identified for the current handling stage.

For `SC-G01`, `use_case_id` is `null` because the customer intent has not yet been identified reliably.

For `SC-G02`, `use_case_id` is `null` because the request does not belong to a supported MVP Use Case.

For `SC-G03`, `use_case_id` may be `null` if processing stops before a supported Use Case is reliably identified.

If a supported Use Case has already been reliably identified before `SC-G03` is applied, the identified `use_case_id` is retained.

When a supported Use Case has already been reliably identified, `use_case_id` must contain that Use Case identifier even if the final handling branch is a Global Scenario.

This applies, for example, to:

- `SC-G04`;
- `SC-G05`;
- `SC-G06`;
- `SC-G07`.

Example:

```json
{
  "use_case_id": "UC-RF-03",
  "scenario_id": "SC-G05",
  "action": "ESCALATE"
}
```

The Global Scenario represents the applied handling branch and does not replace the already identified supported Use Case.

The MVP output represents one applicable supported Use Case for the processed handling path.

The Output Contract does not introduce multi-Use-Case response processing.

## 5. `scenario_id`

`scenario_id` is mandatory.

It contains exactly one Scenario identifier from the frozen Scenario set.

Examples:

```json
"scenario_id": "SC-OS-01A"
```

```json
"scenario_id": "SC-G05"
```

The Scenario identifies the handling branch applied to the request.

The Copilot must not return an invented or dynamically generated Scenario identifier.

## 6. `action`

Allowed values are:

- `ANSWER`
- `CLARIFY`
- `ESCALATE`
- `OUT_OF_SCOPE`

No additional business-action values are defined for the frozen MVP.

The applicable action is determined by the frozen Scenarios and Acceptance Criteria.

This Output Contract does not redefine the conditions under which an action applies.

## 7. `supporting_information`

`supporting_information` contains grounded information relevant to the Copilot result and made available to the support employee.

The field must always be present.

It may contain zero or more information items.

Each information item has the following structure:

```json
{
  "source_type": "OMS",
  "information": "Shipment status is DELIVERED."
}
```

### Supporting-information fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `source_type` | enum | yes | Runtime information source |
| `information` | string | yes | Grounded information relevant to the handling result |

Allowed `source_type` values are:

- `CUSTOMER_REQUEST`
- `KNOWLEDGE_BASE`
- `OMS`

These values correspond to the three primary runtime information sources defined for the MVP.

### Source distinction

Customer-reported information and verified OMS information must remain separate when both are relevant to the result.

Example:

```json
[
  {
    "source_type": "CUSTOMER_REQUEST",
    "information": "Customer reports that the parcel was not received."
  },
  {
    "source_type": "OMS",
    "information": "Shipment status is DELIVERED."
  }
]
```

A customer statement must not be represented as verified OMS information.

Generated assumptions must not be represented as approved Knowledge Base information.

### Source metadata boundary

The MVP Output Contract does not require:

- technical retrieval identifiers;
- vector-database identifiers;
- document chunk identifiers;
- model citations;
- retrieval scores;
- internal retrieval traces.

The `supporting_information` structure is intended to provide relevant grounded information for human review rather than expose retrieval-engine internals.

## 8. `response_draft`

`response_draft` contains a customer-facing draft that may be reviewed and edited by the support employee.

The Copilot does not send the draft directly to the customer.

The field is always present but may contain `null` according to the handling context.

### `ANSWER`

For `ANSWER`, the Copilot may provide a grounded response draft when appropriate for the supported request.

Any factual or policy statement in the draft must be supported by the information permitted by the applicable:

- Use Case;
- Scenario;
- Acceptance Criteria;
- Knowledge Base policy;
- OMS data.

The Copilot must not fill unavailable information with generated assumptions.

### `CLARIFY`

For `CLARIFY`, `response_draft` must contain the clarification that should be requested from the customer.

For unsupported-language handling under `SC-G03`, the clarification must comply with the frozen Scenario and Acceptance Criteria.

### `ESCALATE`

For `ESCALATE`, `response_draft` may be `null`.

A draft may be provided only when a customer-facing response can be prepared safely from the available grounded information.

The draft must not claim that:

- human investigation has already occurred;
- approval has already been granted;
- a business action has already been performed;
- a financial action has already been executed

unless the authoritative operational information confirms that this occurred.

### `OUT_OF_SCOPE`

For `OUT_OF_SCOPE`, `response_draft` may be `null`.

If a draft is produced, it must not represent the unsupported request as a supported MVP capability.

## 9. Missing and Insufficient Information

This Output Contract does not introduce additional missing-information behavior.

Whether missing information results in:

- `ANSWER`;
- `CLARIFY`;
- `ESCALATE`

is determined by the frozen Scenarios and Acceptance Criteria.

Missing information must not be replaced with generated assumptions.

Optional information that is not required for the applicable handling path may remain unavailable.

## 10. Restricted Actions

The output must not state or imply that the Copilot itself:

- approved;
- registered;
- initiated;
- modified;
- executed;
- completed

a restricted business or financial action.

If an authoritative operational source confirms that an action was performed outside the Copilot, that verified fact may be communicated when relevant.

The Output Contract does not provide commands for autonomous execution of restricted actions.

## 11. Null and Empty Values

The following rules apply:

- `use_case_id` may be `null` only when no supported Use Case has been reliably identified according to Section 4;
- `scenario_id` must not be `null` or an empty string;
- `action` must not be `null` or an empty string;
- `supporting_information` must always be present and may be an empty array;
- `response_draft` may be `null` according to Section 8.

Required identifier and enum fields must not contain arbitrary or unsupported values.

## 12. Output Example — ANSWER

```json
{
  "use_case_id": "UC-OS-01",
  "scenario_id": "SC-OS-01A",
  "action": "ANSWER",
  "supporting_information": [
    {
      "source_type": "OMS",
      "information": "Shipment status is SHIPPED."
    },
    {
      "source_type": "OMS",
      "information": "Estimated delivery date is 2026-09-02."
    }
  ],
  "response_draft": "Your order has been shipped and is currently expected to arrive on 2 September 2026."
}
```

## 13. Output Example — CLARIFY

```json
{
  "use_case_id": "UC-OS-01",
  "scenario_id": "SC-G04",
  "action": "CLARIFY",
  "supporting_information": [],
  "response_draft": "Please provide the order number so that the order can be identified."
}
```

## 14. Output Example — ESCALATE

```json
{
  "use_case_id": "UC-SH-03",
  "scenario_id": "SC-SH-03",
  "action": "ESCALATE",
  "supporting_information": [
    {
      "source_type": "CUSTOMER_REQUEST",
      "information": "Customer reports that the parcel was not received."
    },
    {
      "source_type": "OMS",
      "information": "Shipment status is DELIVERED."
    }
  ],
  "response_draft": null
}
```

## 15. Output Example — OUT_OF_SCOPE

```json
{
  "use_case_id": null,
  "scenario_id": "SC-G02",
  "action": "OUT_OF_SCOPE",
  "supporting_information": [],
  "response_draft": null
}
```

## 16. Output Example — Global Scenario After Use Case Identification

A Global Scenario may be applied after a supported Use Case has already been identified.

Example:

```json
{
  "use_case_id": "UC-RF-03",
  "scenario_id": "SC-G05",
  "action": "ESCALATE",
  "supporting_information": [],
  "response_draft": null
}
```

In this example, the supported customer intent is known, but required verified information is unavailable or insufficient.

The Global Scenario does not replace the identified Use Case.

## 17. Contract Boundaries

The Copilot Output Contract does not expose or require:

- private model reasoning;
- chain-of-thought;
- model confidence scores;
- internal prompt content;
- retrieval-engine traces;
- final legal decisions;
- final financial decisions;
- autonomous business-action commands.

It also does not define:

- API endpoints;
- HTTP methods or status codes;
- authentication;
- serialization transport;
- persistence;
- model provider;
- model version;
- prompt architecture;
- retrieval architecture.

Those concerns belong to solution design and implementation.

## 18. Related Documentation

### Product

- [Product Discovery](../product/discovery.md)
- [Success Metrics](../product/success_metrics.md)
- [Use Cases](../product/use_cases.csv)
- [Scenarios](../product/scenarios.csv)
- [Acceptance Criteria](../product/acceptance_criteria.csv)
- [Non-Functional Requirements](../product/non_functional_requirements.md)

### Data

- [OMS Data Contract](../data/oms_data_contract.md)

### Knowledge Base

- `data/knowledge_base/shipping_policy.md`
- `data/knowledge_base/returns_policy.md`
- `data/knowledge_base/refund_policy.md`