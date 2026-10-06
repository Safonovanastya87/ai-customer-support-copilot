# Level 2 - Logical Case, Use Case Identification and Channel Routing

**Baseline:** Architecture V14.6

## Input

- Request
- current accepted business context
- saved `use_case_id`, where already present

Use Case identification follows the Scope, Identification, Policy Scope Gate, and precedence rules in `supporting_rules.md` together with the Use Case definitions in `use_cases.csv`.

Before a Policy-based Use Case can be selected, Level 2 applies the Policy Scope Gate. If the customer's requested process is explicitly outside the Policy scope declared for that Use Case, that Use Case is excluded. If no supported policy-free/status Use Case matches the primary requested outcome, the result is `UNSUPPORTED_BY_COPILOT`.

## Logical Case Check

Before Use Case identification, check whether the accepted business context contains more than one independent business issue.

If multiple independent issues are present:

- do not force them into one supported Use Case;
- `state = PROCESSING`;
- build Decision Result:
  - `action = HANDOFF_TO_SUPPORT`
  - `decision_reason = MULTIPLE_ISSUES`
  - `support_draft_required = false`
- go to **Level 6**.

This rule applies to the first actionable message as well as later accepted business context.

## Identification Outcome Contract

Exactly one outcome must be produced:

1. `UNSUPPORTED_BY_ANAS_SHOP` - clearly outside Anas Shop scope.
2. `UNSUPPORTED_BY_COPILOT` - clearly inside Anas Shop scope, but no supported MLP Use Case applies.
3. `USE_CASE_AMBIGUITY` - customer information is sufficient, but more than one supported Use Case remains valid after precedence/exclusion/Policy-scope rules.
4. `USE_CASE_INPUT_INSUFFICIENT` - information is not sufficient to identify or reject a Use Case reliably.
5. `SUPPORTED_USE_CASE` - exactly one supported Use Case applies.

If the documented identification rules cannot produce one valid outcome because they are missing, conflicting, or semantically invalid -> **Semantic / Business Logic Error Handling**.

If identification cannot execute because of a technical failure -> **Technical Error Handling**.

## Outcome Handling

### USE_CASE_INPUT_INSUFFICIENT

If no successful clarification with `decision_reason = USE_CASE_INPUT_INSUFFICIENT` exists for this Request:

- build Decision Result:
  - `action = CLARIFY`
  - `decision_reason = USE_CASE_INPUT_INSUFFICIENT`
  - `context.expected_customer_input = information required to identify the Use Case`
- go to **Level 6**.

Otherwise:

- build Decision Result:
  - `action = HANDOFF_TO_SUPPORT`
  - `decision_reason = CLARIFICATION_LIMIT`
  - `support_draft_required = false`
- go to **Level 6**.

### USE_CASE_AMBIGUITY

- build Decision Result:
  - `action = HANDOFF_TO_SUPPORT`
  - `decision_reason = USE_CASE_AMBIGUITY`
  - `support_draft_required = false`
- go to **Level 6**.

### UNSUPPORTED_BY_ANAS_SHOP

- build Decision Result:
  - `action = OUT_OF_SCOPE_RESPONSE`
  - `decision_reason = UNSUPPORTED_BY_ANAS_SHOP`
- go to **Level 6**.

### UNSUPPORTED_BY_COPILOT

- build Decision Result:
  - `action = HANDOFF_TO_SUPPORT`
  - `decision_reason = UNSUPPORTED_BY_COPILOT`
  - `support_draft_required = false`
- go to **Level 6**.

### SUPPORTED_USE_CASE

On every Level 2 entry after accepted new business input, identify the current Use Case from `use_cases.csv`.

If unchanged:

- retain `use_case_id`.

If changed:

- retain the previous `use_case_id` in history;
- set the new `use_case_id`.

Missing, inconsistent, or semantically invalid Use Case definition -> Semantic / Business Logic Error Handling.

Technical inability to load required definitions -> Technical Error Handling.

## Restricted-Action Safety Rule

Read from the current Use Case in `use_cases.csv`:

- `Restricted_Action_Safety`;
- `Restricted_Action_Decision_Reason`.

If `Restricted_Action_Safety = YES` and the Request is in Webchat:

- do not attempt OMS/private processing;
- preserve customer message references and attachments;
- build `HANDOFF_TO_SUPPORT` immediately using the Use Case's `Restricted_Action_Decision_Reason`;
- `support_draft_required = false`;
- go to **Level 6**.

## Channel Capability

The MLP does not correlate Requests across channels.

### EMAIL

Go to **Level 3**.

### WEBCHAT + no OMS/private processing required

Go to **Level 3**.

A Use Case requires OMS/private processing when its `Data_Sources` includes `Order Management System`.

### WEBCHAT + OMS/private processing required

If `Restricted_Action_Safety = YES` -> handoff as defined above.

Otherwise:

- build Decision Result:
  - `action = CHANNEL_REDIRECTION`
  - `decision_reason = PRIVATE_PROCESSING_REQUIRES_EMAIL`
- go to **Level 6**.

The Webchat Request is not transferred to Email. A later Email message starts a new Request.
