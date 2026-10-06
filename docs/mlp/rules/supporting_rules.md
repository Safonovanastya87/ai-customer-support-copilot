# Supporting Rules - MLP V14.6

This document is the single cross-level rules document for lifecycle, Request structure, channel behavior, scope and Use Case identification, source requirements, security, message evidence, attachments, allowed decisions, Human Support ownership, clarification limits, support drafts, and error boundaries.

The per-Use-Case source/retrieval/safety contract is stored directly in `use_cases.csv`.
The Level 5 outcome contract is stored in `scenarios.csv`.

## 1. Request Lifecycle

Allowed Request states:

- `PROCESSING`
- `AWAITING_CUSTOMER`
- `CLOSED`
- `TECHNICAL_ERROR`

Rules:

- `NONE -> PROCESSING` when a business Request is created.
- `PROCESSING -> AWAITING_CUSTOMER` only after required `CLARIFY` delivery is accepted.
- `PROCESSING -> CLOSED` only after the required terminal side effect succeeds.
- `AWAITING_CUSTOMER -> PROCESSING` when business input is accepted or a terminal handoff is initiated.
- `AWAITING_CUSTOMER -> AWAITING_CUSTOMER` after `COMMUNICATION_ONLY_RESPONSE`.
- Clarification TTL expiry -> `CLOSED / CUSTOMER_NO_RESPONSE` for every Use Case.
- TTL expiry alone never triggers `HANDOFF_TO_SUPPORT`.
- `CLOSED` is terminal for that Copilot Request.

## 2. Minimal Request Contract

A Request retains at least:

- stable `request_id`;
- `state`;
- `owner = COPILOT` or `HUMAN_SUPPORT` after accepted handoff/escalation;
- immutable `request_channel`;
- ordered `message_refs`;
- ordered `accepted_business_message_refs` for business input accepted into the current logical case;
- ordered `attachment_refs`, where present;
- current `use_case_id`, once identified;
- active clarification context while waiting;
- `support_handoff_reference`, where supplied after accepted handoff;
- `closure_reason` when closed;
- lifecycle/decision history required for audit and clarification limits.

Each customer message reference resolves at least the original message/content reference, `received_at`, channel, and attachment refs where present.
The Request stores references rather than a duplicated transcript.

## 3. Message Context and Evidence Preservation

For every customer message associated with an existing Request:

- retain its immutable reference in ordered `message_refs`;
- retain any attachment references unchanged;
- store each individual `message_ref` and `attachment_ref` at most once per Request.

When actionable/contextual input is accepted for the current logical case:

- also append its reference to ordered `accepted_business_message_refs`;
- store each accepted business-message reference at most once.

Do not add pure Communication Only messages or a rejected independent issue to the accepted business subset.

## 4. Channel-Local Correlation - No Cross-Channel MLP

The MLP does not correlate Email and Webchat Copilot Requests.

Each Request belongs to one immutable `request_channel` and one same-channel correlation scope.

Therefore:

- `CHANNEL_MISMATCH_INSTRUCTION` does not exist;
- Webchat -> Email redirection closes the Webchat Request;
- a later Email message creates a new Request;
- no customer identity merging across channels is required.

The exact same-channel thread/correlation algorithm remains an integration detail.

## 5. Serialization and TTL Race Rule

Inbound messages and lifecycle timer events for one correlation scope use the same serialized/atomic processing boundary.

TTL closure may commit only if:

- Request is still `AWAITING_CUSTOMER` for the same active clarification; and
- no eligible customer inbound message accepted before expiry is pending for that Request.

A customer reply accepted before expiry wins over TTL closure and continues the Request.

## 6. Communication Only Definition

A message is `COMMUNICATION ONLY` only when it contains no actionable/contextual business content and does not provide information relevant to the active Request/clarification.

Any business-relevant content wins over courtesy/social content.

Examples:

- `Danke!` -> Communication Only.
- `Danke, aber wo ist meine Bestellung?` -> Actionable / Contextual.
- During clarification, `Danke, die Nummer ist 12345` -> Actionable / Contextual continuation.

## 7. Language Policy

- clearly German -> German customer-facing response;
- clearly English -> English;
- unsupported, mixed, language-neutral, or undetermined -> German for automatic/static responses.

Unsupported language is not a separate business scenario.

## 8. Scope Boundary

### UNSUPPORTED_BY_ANAS_SHOP

Use only when the understood request is clearly unrelated to Anas Shop products, orders, services, policies, or customer support.

Examples: a question about another retailer, unrelated general knowledge, or an unrelated personal task.

### UNSUPPORTED_BY_COPILOT

Use when the request is clearly about Anas Shop but no supported MLP Use Case exists.

Non-exhaustive examples:

- damaged/wrong item complaint handled as a defect/damage process rather than standard withdrawal;
- warranty or compensation claim;
- order cancellation;
- payment problem;
- address change;
- product complaint outside modeled standard withdrawal/return/refund questions;
- another Anas Shop service request not represented in `use_cases.csv`.

If it is unclear whether a request is inside or outside Anas Shop scope, do not guess `UNSUPPORTED_BY_ANAS_SHOP`; use the identification contract's insufficiency/ambiguity handling.

## 9. Logical Case Boundary

Before selecting one Use Case, detect whether the accepted customer context contains multiple independent business issues.

If it does, do not force one Use Case; use:

- `action = HANDOFF_TO_SUPPORT`
- `decision_reason = MULTIPLE_ISSUES`

This applies to the first actionable message as well as later continuation context.

## 10. Identification Principle and Policy Scope Gate

Use Case selection is based on the customer's primary requested outcome and requested business process, not merely on individual keywords mentioned.

Precedence, exclusion, and Policy scope rules are applied before `USE_CASE_AMBIGUITY`.

A word such as `defect`, `damage`, or `warranty` does not by itself force `UNSUPPORTED_BY_COPILOT` if the customer clearly requests the standard withdrawal process instead. The requested process controls classification.

A Use Case with a Policy in `Policy_Scope` may be selected only within that Policy's defined scope.

### Shipping Policy

`UC-SH-01` and `UC-SH-02` represent Anas Shop Standard Delivery within Germany.

If the customer explicitly requests handling for express, premium, same-day, international, or another special delivery service excluded by the Shipping Policy, do not select these Use Cases. If no other supported policy-free/status Use Case matches the primary requested outcome -> `UNSUPPORTED_BY_COPILOT`.

### Returns Policy

`UC-RT-01`, `UC-RT-02`, and `UC-RT-03` represent the standard withdrawal/return process covered by the Returns Policy.

If the requested handling is explicitly based on warranty, defect, damage, compensation, or another process excluded by the Returns Policy, do not select these Use Cases. If no other supported policy-free/status Use Case matches the primary requested outcome -> `UNSUPPORTED_BY_COPILOT`.

### Refund Policy

`UC-RF-01`, `UC-RF-02`, and `UC-RF-04` represent the standard refund process arising from withdrawal/return cases covered by the Refund Policy.

If the requested handling is explicitly based on warranty, defect, damage, compensation, or another claim/process excluded by the Refund Policy, do not select these Use Cases. If no other supported policy-free/status Use Case matches the primary requested outcome -> `UNSUPPORTED_BY_COPILOT`.

### Policy-free/status paths

`UC-OS-01`, `UC-SH-03`, `UC-RT-04`, and `UC-RF-03` do not apply Shipping/Returns/Refund Policy rules to determine entitlement or business handling.

They are not automatically excluded solely because the underlying order/return/refund originated from a process outside one of those Policy scopes. They remain limited to their defined OMS/customer-report facts and Human Support handoff.

Examples:

- `My item is defective. What refund am I entitled to?` -> `UNSUPPORTED_BY_COPILOT`.
- `My damaged item should be refunded. Please issue the refund.` -> `UNSUPPORTED_BY_COPILOT`.
- `My item is defective, but I hereby withdraw from the purchase.` -> `UC-RT-03` because the requested process is withdrawal.
- `Where is the refund for my defective item?` -> `UC-RF-03` if the customer asks only for existing/expected refund status.
- `Express delivery is late.` -> `UNSUPPORTED_BY_COPILOT`.
- `Tracking says delivered but I did not receive the parcel.` -> `UC-SH-03`.

## 11. Use Case Precedence

### Shipping / Order

After the Policy Scope Gate:

1. Explicitly reports that tracking/status shows delivered but not received -> `UC-SH-03`.
2. Reports non-arrival/delay without an explicit delivered-status claim, within Shipping Policy scope -> `UC-SH-02`.
3. Asks only for current order/shipment status without primarily reporting delay/non-receipt -> `UC-OS-01`.
4. General Standard Delivery rule/timing/method question within Shipping Policy scope and without a specific order -> `UC-SH-01`.

### Returns

After the Policy Scope Gate:

- General standard withdrawal/return rules, no specific purchase -> `UC-RT-01`.
- Standard withdrawal/return rules for a specific purchased item, no action request -> `UC-RT-02`.
- Customer declares withdrawal or asks to register/initiate/modify/perform a standard withdrawal/return-related action -> `UC-RT-03`.
- Customer asks for the current recorded status of a return that has already been initiated/sent/received -> `UC-RT-04`. Questions about return instructions, carrier/drop-off, labels, packaging, or how to start/change a return are not `UC-RT-04`; they stay in the applicable Policy-based return Use Case.

### Refunds

After the Policy Scope Gate:

- General refund rules/timing for the standard withdrawal/return refund process, no specific case -> `UC-RF-01`.
- Refund rules for a specific standard withdrawal/return case, but not current refund status and not an action request -> `UC-RF-02`.
- Customer asks where/when the money/refund is, or current status of an initiated/expected/recorded refund -> `UC-RF-03`.
- Customer asks Support to issue/approve/initiate/modify/cancel/perform a refund within the standard withdrawal/return refund process -> `UC-RF-04`.

Return/refund examples:

- `I sent the return; did you receive the parcel?` -> `UC-RT-04`.
- `I sent the return; where is my money?` -> `UC-RF-03`.
- `How long do refunds normally take after a standard return?` -> `UC-RF-01` if no specific case.
- `For my returned item, which standard refund rules apply?` -> `UC-RF-02`.

Use `USE_CASE_AMBIGUITY` only when customer information is sufficient yet two or more supported Use Cases genuinely remain valid after these rules.

## 12. Per-Use-Case Source and Retrieval Contract

`use_cases.csv` is the source of truth for each Use Case's:

- `Data_Sources`;
- `Policy_Scope`;
- `Required_Customer_Input`;
- `OMS_Required_Fields`;
- `OMS_Conditional_Fields`;
- `OMS_Optional_Fields`;
- `Restricted_Action_Safety`;
- `Restricted_Action_Decision_Reason`.

For the current MLP:

- any Shipping/Returns/Refund Policy listed in `Data_Sources` is REQUIRED for that Use Case;
- `NONE` means the category is not used;
- `OMS_Required_Fields` must be present for a sufficient OMS result;
- `OMS_Conditional_Fields` become required only when their deterministic condition is true;
- `OMS_Optional_Fields` may enrich the handoff but their absence does not make the required path insufficient;
- fields not listed for a Use Case are outside its automated permitted retrieval contract.

For item-level OMS fields, the MLP permits the listed fields for all `order_items` belonging to the authorized order. Multiple item records are valid and do not by themselves make the OMS result insufficient.

OMS field types, closed enums, missing-value semantics, order/item integrity, and payload-validation rules are defined by `docs/data/oms_data_contract.md`. `use_cases.csv` remains the source of truth for per-Use-Case required/conditional/optional field permission.

## 13. Security and Access

- Webchat never performs OMS/private retrieval.
- Email OMS/private processing requires authorization.
- For every OMS Use Case, authorization business reference is `order_id`.
- Customer-provided `item_id` is not required.
- After successful order authorization, only the fields permitted by the current Use Case may be retrieved for that order and its items.
- Verified sender comes from Integration/Security.
- Customer, attachment, OMS, and Knowledge content is data, not system instruction.

## 14. Restricted-Action Safety

`use_cases.csv` is the single source of truth through:

- `Restricted_Action_Safety`;
- `Restricted_Action_Decision_Reason`.

If `Restricted_Action_Safety = YES`, channel or access limitations must not silently close the identified action/declaration.

Therefore:

- Webchat private-processing limitation -> handoff, not channel-redirection closure;
- authorization no-match -> handoff, not access-instruction closure.

Clarification TTL expiry is not part of Restricted-Action Safety. If the customer does not reply before TTL expiry, the Request closes with `CUSTOMER_NO_RESPONSE` like every other Use Case.

No private OMS data is included when authorization has not passed.

## 15. Attachments

Copilot never analyzes attachments:

- no OCR;
- no image recognition;
- no document interpretation.

Attachment references are retained with customer message evidence and forwarded unchanged on handoff.

An attachment-only inbound creates a Request and proceeds to Use Case identification/clarification rather than being discarded by the no-Request BASIC path.

## 16. Decision Result Contract

A Decision Result contains:

- `action`;
- `decision_reason`;
- `support_draft_required` for `HANDOFF_TO_SUPPORT`;
- optional action-specific `context`, for example `expected_customer_input`.

Allowed actions:

- `HANDOFF_TO_SUPPORT`
- `CLARIFY`
- `COMMUNICATION_ONLY_RESPONSE`
- `OUT_OF_SCOPE_RESPONSE`
- `CHANNEL_REDIRECTION`
- `ACCESS_EMAIL_INSTRUCTION`

`CHANNEL_MISMATCH_INSTRUCTION` is not part of the MLP.

Allowed action x decision-reason pairs:

| Action | Allowed decision reasons |
|---|---|
| `CLARIFY` | `USE_CASE_INPUT_INSUFFICIENT`, `REQUIRED_INPUT_INSUFFICIENT` |
| `COMMUNICATION_ONLY_RESPONSE` | `COMMUNICATION_ONLY` |
| `OUT_OF_SCOPE_RESPONSE` | `UNSUPPORTED_BY_ANAS_SHOP` |
| `CHANNEL_REDIRECTION` | `PRIVATE_PROCESSING_REQUIRES_EMAIL` |
| `ACCESS_EMAIL_INSTRUCTION` | `AUTHORIZATION_NOT_PASSED` |
| `HANDOFF_TO_SUPPORT` | `HUMAN_REQUESTED`, `UNINTERPRETABLE_IN_CONTEXT`, `MULTIPLE_ISSUES`, `CLARIFICATION_LIMIT`, `USE_CASE_AMBIGUITY`, `UNSUPPORTED_BY_COPILOT`, `BUSINESS_LOGIC_CONFIGURATION_ERROR`, `REQUIRED_SOURCE_INFORMATION_INSUFFICIENT`, `ORDER_STATUS_INFORMATION_AVAILABLE`, `GENERAL_SHIPPING_INFORMATION_AVAILABLE`, `DELIVERY_STATUS_CONFLICT`, `DELIVERY_WITHIN_EXPECTED_WINDOW`, `DELIVERY_INVESTIGATION_REQUIRED`, `DELIVERED_NOT_RECEIVED_REQUIRES_REVIEW`, `REPORTED_DELIVERED_STATUS_CONFLICT`, `GENERAL_RETURN_RULES_AVAILABLE`, `SPECIFIC_RETURN_RULES_CONTEXT_AVAILABLE`, `RETURN_ACTION_REQUIRES_HUMAN`, `RETURN_STATUS_INFORMATION_AVAILABLE`, `GENERAL_REFUND_INFORMATION_AVAILABLE`, `SPECIFIC_REFUND_RULES_CONTEXT_AVAILABLE`, `REFUND_STATUS_INFORMATION_AVAILABLE`, `REFUND_ACTION_REQUIRES_HUMAN` |

Allowed closure reasons:

- `HANDED_TO_SUPPORT`
- `UNSUPPORTED_BY_ANAS_SHOP`
- `CHANNEL_REDIRECTION`
- `ACCESS_EMAIL_INSTRUCTION`
- `CUSTOMER_NO_RESPONSE`
- `TECHNICAL_ESCALATION`

A closure reason is not required while the Request is active.

## 17. Retrieval, Authorization, Runtime and Clarification Contracts

A Retrieval Result may contain:

- `knowledge_result`, when required by the current Use Case;
- `oms_result`, when OMS is required;
- optional enrichment and optional-source issue metadata where applicable.

Required Knowledge/OMS results use `SUFFICIENT / INSUFFICIENT`.
A technical inability to perform a required retrieval is a technical error, not `INSUFFICIENT`.

For OMS/private processing:

- `authorization = PASSED` only when verified sender is authorized for the supplied `order_id`;
- authorization is bound to `order_id`, not `item_id`.

Runtime Context for date-based scenarios contains:

- `current_local_date`;
- `current_timezone = Europe/Berlin`.

A successful clarification history record is appended only after delivery acceptance and contains at least:

- `decision_reason`;
- `use_case_id`, where applicable;
- `expected_customer_input`;
- `delivered_at`.

Failed/unaccepted `CLARIFY` does not consume a clarification limit.

## 18. Human Support Ownership Boundary

After an accepted normal handoff or accepted Technical Escalation:

- `owner = HUMAN_SUPPORT`;
- accepted Support/ticket reference is retained where available;
- the Request closes with `HANDED_TO_SUPPORT` for a normal handoff or `TECHNICAL_ESCALATION` for a technical fallback.

For Technical Escalation of an existing business Request, Human Support receives the customer case and available business evidence/context, not only a technical incident record. The detailed minimum payload is defined in `technical_error_handling.md`.

Future-message routing is controlled by the active Human Support conversation/ticket state in Integration/Support, not by treating the closed Request owner as permanent routing state.

While Human Support conversation is active -> messages bypass Copilot.
After Support closes that conversation -> a later eligible message may start a new Copilot Request.

## 19. Clarification Limits

- one successful `USE_CASE_INPUT_INSUFFICIENT` clarification per Request;
- one successful `REQUIRED_INPUT_INSUFFICIENT` clarification per current `use_case_id`;
- no global clarification counter.

## 20. Support Draft

The source of truth is `scenarios.csv -> Support_Draft_Required`.

- Level 5 scenario `YES` -> Decision Result carries `support_draft_required = true` and Level 6 attempts to create a grounded draft.
- A draft uses the customer-facing language determined by the Language Policy and may use only accepted customer context, verified permitted OMS facts, and approved Knowledge available for the case.
- If a reliable grounded draft cannot be produced without speculation, omit the draft and continue the handoff with the available context/data. Draft creation must not block `HANDOFF_TO_SUPPORT`.
- `NO` -> context-only handoff.
- direct L1-L3 and error-fallback handoffs default to false.
- drafts are Human-Support-only and never auto-sent to the customer.

## 21. Error Category Boundary

- normal business outcome -> Levels 1-6;
- semantic/business-rule defect -> Semantic / Business Logic Error Handling;
- technical execution failure of a required operation -> Technical Error Handling;
- technical failure limited to optional enrichment -> omit/log optional enrichment and continue if the required path remains executable.

## 22. Pre-Activation Validation

Validate before activation:

- unique/stable Use Case and Scenario IDs;
- Use Case scope and Policy_Scope consistency;
- every Policy-based Use Case stays inside the applicable Policy scope;
- `Required_Customer_Input` and business-reference rules are coherent;
- no customer `item_id` dependency in the current MLP input contract;
- OMS field lists and conditional-rule syntax are valid against `docs/data/oms_data_contract.md`;
- scenario completeness and mutual exclusivity;
- allowed action x decision_reason pairs;
- `Restricted_Action_Safety = YES` has a valid `Restricted_Action_Decision_Reason`;
- valid closure reasons;
- valid `Support_Draft_Required` values.

## 23. Intentionally Not Fixed

- exact `AWAITING_CUSTOMER` TTL duration;
- exact `PROCESSING` timeout/retry count;
- exact same-channel correlation algorithm;
- exact SPF/DKIM/DMARC/provider-verification implementation;
- downstream Human Support workflow after accepted handoff, including the exact Support destination/queue/address;
- optional customer-facing acknowledgement that a handoff occurred;
- technical storage/queue/idempotency implementation;
- Webchat multi-message aggregation window;
- detailed operational recovery policy for `TECHNICAL_ERROR`.
