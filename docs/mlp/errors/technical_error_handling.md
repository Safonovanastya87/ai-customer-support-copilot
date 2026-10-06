# Technical Error Handling — MLP V14.6

Used when otherwise valid **required processing** cannot execute because of integration, transport, persistence, runtime, or technical payload-validation failure.

## Examples

- timeout / connection failure / unexpected 5xx for a required operation;
- required OMS or Knowledge source unavailable;
- required outbound message not accepted by channel adapter;
- Support handoff not accepted;
- database/queue/persistence failure;
- required Use Case, Scenario, Policy, or rule definition cannot be loaded technically;
- identification or authorization execution failure;
- invalid OMS payload violating required type/enum/relationship/data-integrity contract;
- unexpected runtime exception affecting the required path.

## Main Flow

1. Capture failure context.
2. If retryable, perform bounded idempotent retry of the **failed required technical operation only**.
3. On success, resume from that operation.
4. On exhausted/non-retryable failure, use Technical Escalation.

Do not restart the whole business flow or repeat already completed side effects.

## Optional Enrichment Boundary

A technical failure that is limited to an `OPTIONAL` source/enrichment does **not** trigger Technical Escalation when all required processing remains executable.

For an optional-only failure:

- capture/log the optional-source issue;
- optional bounded retry may be used;
- omit the unavailable optional enrichment;
- do not use unavailable optional content in a support draft;
- continue the normal required business path.

If the same failure also prevents a required operation, this exception no longer applies and normal Technical Error Handling is used.

A technical failure loading a required Use Case, Scenario, Policy, or rule definition is never treated as an optional-source failure.

## State Commit Rule

Commit business state only after required side effect is accepted.

- CLARIFY accepted -> `AWAITING_CUSTOMER`.
- Support handoff accepted -> `owner = HUMAN_SUPPORT`, `CLOSED`, `HANDED_TO_SUPPORT`.
- required terminal customer message accepted -> then close with its configured closure reason.

## Optional Communication

Failure of optional `COMMUNICATION_ONLY_RESPONSE` does not alone trigger business technical escalation. Log/optionally retry; Request remains `AWAITING_CUSTOMER`.

No-Request courtesy-message failure is handled operationally and does not create a business Request solely for the failure.

## Technical Escalation

Technical Escalation of an existing business Request transfers responsibility for the **customer case**, not only a technical incident record.

The escalation payload must preserve, where available:

- the Request / `request_id`;
- current `use_case_id`, if already identified;
- ordered accepted customer business-message references and any additional handoff-relevant message references, including the current triggering message where applicable;
- attachment references unchanged;
- already retrieved valid permitted OMS/business facts;
- already retrieved approved Knowledge context;
- active clarification context, if relevant;
- the technical failure reason/context required for Support and operational traceability.

A Support draft is not required for Technical Escalation.

If an existing business Request exists and durable technical fallback accepts the escalation:

- `owner = HUMAN_SUPPORT`;
- retain the returned `support_handoff_reference`, where provided;
- `Request = CLOSED`;
- `closure_reason = TECHNICAL_ESCALATION`;
- deactivate active clarification and retain history.

After accepted Technical Escalation, future messages are routed according to the active Human Support conversation/ticket state. While that Support conversation is active, messages bypass Copilot.

If fallback cannot accept it:

- `Request = TECHNICAL_ERROR`;
- preserve failure context and the customer-case evidence already retained by the Request;
- raise operational alert;
- correlated same-channel inbound is held/routed by recovery policy.

If no business Request exists, do not create one solely for the technical error.

## Processing Timeout

A Request must not remain `PROCESSING` indefinitely. Exceeding configured processing timeout is a technical failure.

## Delivery Success

Required delivery is successful when the responsible adapter/boundary accepts the operation. Customer read/open confirmation is not required.
