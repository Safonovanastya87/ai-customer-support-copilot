# Level 6 — Final Action Execution and Request Finalization

**Baseline:** Architecture V14.6

## Input

- Request
- current triggering message reference, where applicable
- current-cycle Decision Result
- Retrieval Result / Runtime context, where applicable

Level 6 executes the Decision Result. It does not re-evaluate business logic.

## HANDOFF_TO_SUPPORT

If `Decision Result.support_draft_required = true`:

- attempt to build a grounded draft using only accepted customer context, verified permitted OMS facts, and approved Knowledge available for the case;
- use the customer-facing language determined by the Language Policy;
- the draft is for Human Support review only;
- it is never sent automatically to the customer in this MLP;
- it must not attribute execution of a restricted action, investigation, refund, or return to Copilot, and must not claim completion without supporting verified case data; a permitted verified OMS status such as `return_status = COMPLETED` or `refund_status = COMPLETED` may be stated as an OMS status fact;
- if a reliable grounded draft cannot be produced without speculation, omit the draft and continue the handoff with the available context/data; this alone must not block or change `HANDOFF_TO_SUPPORT`.

Send to Human Support:

- Request;
- ordered relevant business messages referenced by `accepted_business_message_refs`;
- any additional handoff-relevant customer messages referenced by `message_refs`, including the current triggering message when it is not part of the accepted business subset;
- support draft, when successfully produced;
- relevant permitted OMS/business fields already retrieved;
- relevant approved Knowledge source/context already retrieved;
- attachment references from `attachment_refs`, unchanged;
- `decision_reason` and relevant Decision Result context.

Customer message references preserve the original message metadata, including `received_at`, channel, and attachment references. Attachments are forwarded unchanged and are never analyzed by Copilot.

After the Support boundary accepts the handoff:

- `owner = HUMAN_SUPPORT`;
- store returned `support_handoff_reference`, where provided;
- `Request = CLOSED`;
- `closure_reason = HANDED_TO_SUPPORT`.

The closed Request records the handoff. It is **not** the permanent routing authority for future conversation messages. Integration routes future messages according to the active Human Support conversation/ticket state. While that Support conversation is active, messages bypass Copilot. Once Support closes it, later messages may start a new Copilot Request.

## CLARIFY

- use `Decision Result.context.expected_customer_input`;
- do not ask for fields outside that contract;
- apply Language Policy;
- send to customer.

After successful delivery:

- append clarification-history record:
  - `decision_reason`
  - `use_case_id`, where applicable
  - `expected_customer_input`
  - `delivered_at`
- store active clarification context;
- `Request = AWAITING_CUSTOMER`.

## COMMUNICATION_ONLY_RESPONSE

- send optional approved static/courtesy response;
- failure of this optional response alone does not trigger business technical escalation;
- Request remains `AWAITING_CUSTOMER`;
- active clarification remains active;
- clarification TTL is not reset or extended.

## OUT_OF_SCOPE_RESPONSE

After successful approved static response:

- `Request = CLOSED`;
- `closure_reason = UNSUPPORTED_BY_ANAS_SHOP`.

## CHANNEL_REDIRECTION

Used only for a Webchat Use Case that requires OMS/private processing and is **not** a restricted-action safety case.

- instruct the customer to send the business inquiry by Email;
- make clear that the Webchat Request is not transferred/continued in Email;
- after successful delivery:
  - `Request = CLOSED`
  - `closure_reason = CHANNEL_REDIRECTION`
- a later Email message starts a new Request.

No cross-channel Request correlation exists in the MLP.

## ACCESS_EMAIL_INSTRUCTION

Send a neutral instruction:

- ask the customer to check the supplied order/reference number;
- ask them to resend the business inquiry from the email address authorized for that order/reference;
- if that email cannot be used, ask to be connected to Human Support and briefly repeat the inquiry;
- do not reveal whether a specific order exists;
- do not reveal which email address is stored/authorized.

After successful delivery:

- `Request = CLOSED`;
- `closure_reason = ACCESS_EMAIL_INSTRUCTION`.

This action is not used when the current Use Case has `Restricted_Action_Safety = YES` in `use_cases.csv`; those cases hand off to Support using that Use Case's `Restricted_Action_Decision_Reason` instead.

## AWAITING_CUSTOMER TTL expiry

Clarification TTL expiry is a lifecycle timer outcome, not a new Decision Result action. Apply the serialized TTL race rule from `supporting_rules.md`.

If the Request is still `AWAITING_CUSTOMER` for the same active clarification when TTL expiry commits:

- `Request = CLOSED`;
- `closure_reason = CUSTOMER_NO_RESPONSE`;
- do not hand off to Human Support solely because `Restricted_Action_Safety = YES`.

## Finalization

Whenever `Request = CLOSED`:

- deactivate `active_clarification`;
- retain clarification history;
- persist lifecycle/audit context.

Message-only no-Request paths may end before Level 6.
