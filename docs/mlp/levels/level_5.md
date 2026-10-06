# Level 5 - Business Scenario and Action Decision

**Baseline:** Architecture V14.6

## Input

- Request
- saved `use_case_id`
- Retrieval Result
- Runtime Context

Runtime Context for the current MLP contains:

```text
current_local_date
current_timezone = Europe/Berlin
```

`current_local_date` is the local calendar date, not a calculated business-day calendar.

## Rule: Do Not Re-identify Intent or Policy Scope

Level 5 trusts the `use_case_id` selected at Level 2.

Scenario conditions evaluate business/data state only. They must not reclassify the customer intent or repeat the Policy Scope Gate.

Customer-reported facts already preserved in the Request may be compared with verified OMS facts, but this does not re-identify the Use Case.

## Scenario Resolution

Load from `scenarios.csv` the scenarios applicable to the saved Use Case and evaluate their conditions.

Exactly one scenario must match.

### Exactly 1 match

Validate that the scenario action and decision reason are permitted by the Decision Result rules in `supporting_rules.md`.

If valid:

- copy scenario `Action` to Decision Result `action`;
- copy `Decision_Reason`;
- copy scenario `Support_Draft_Required` to `support_draft_required`;
- build Decision Result;
- go to **Level 6**.

If the action/reason pair is not permitted -> Semantic / Business Logic Error Handling.

### 0 matches

Semantic / Business Logic Error Handling: scenario gap.

### More than 1 match

Semantic / Business Logic Error Handling: scenario conflict.

## Allowed Normal Level 5 Action

```text
HANDOFF_TO_SUPPORT
```

`CLARIFY` is not allowed at Level 5.

Out-of-scope, channel-routing, access, and clarification decisions are handled earlier.

## Support Draft Contract

`Support_Draft_Required` in `scenarios.csv` is the source of truth.

- `YES` -> Level 6 attempts to create a grounded draft for Human Support. Draft creation is non-blocking: if a reliable grounded draft cannot be produced, the handoff still proceeds with context/data only.
- `NO` -> handoff contains context/data only.

Direct handoffs from L1-L3 and semantic/technical fallbacks default to `support_draft_required = false`.
