# Level 1 — Request Resolution, Message Classification and Continuation Routing

**Baseline:** Architecture V14.6

## Precondition

The Channel / Integration Layer:

- filters technical inbound events;
- routes messages belonging to an active Human Support conversation outside Copilot;
- resolves at most one non-terminal Copilot Request within the **same channel-local correlation scope**;
- serializes inbound customer messages and lifecycle timer events for that scope;
- stores inbound customer messages durably so a message reference can resolve the original message metadata and attachments.

The MLP does **not** correlate Copilot Requests across Email and Webchat.

If a message arrives while a Copilot Request is `PROCESSING`, it is queued and does not enter Level 1 concurrently. A normal Copilot-owned Request visible to Level 1 is therefore either `NONE` or `AWAITING_CUSTOMER`.

A Request in `TECHNICAL_ERROR` does not enter Levels 1–6.

## Message-reference rule

Whenever a Request is created or an inbound customer message is associated with an existing Request:

- append the immutable customer message reference to ordered `message_refs`;
- append any attachment references to `attachment_refs` unchanged;
- append the message reference to `accepted_business_message_refs` only when its content is accepted as business-relevant input for the current logical case.

Each individual `message_ref`, `accepted_business_message_ref`, and `attachment_ref` is stored at most once per Request, even when a branch below repeats the instruction to retain it.

This preserves original customer evidence without copying full transcripts into the Request.

## Message-type rule

Classification is evaluated in this order:

1. explicit `HUMAN AGENT REQUEST`;
2. presence of any actionable or contextual business content;
3. otherwise `COMMUNICATION ONLY`.

`COMMUNICATION ONLY` means that the message contains **no business-relevant content** and does not provide information relevant to the current Request or active clarification.

Examples:

- `Danke!` -> Communication Only.
- `Danke, aber wo ist meine Bestellung?` -> Actionable / Contextual.
- During clarification, `Danke, die Nummer ist 12345` -> Actionable / Contextual continuation.

## Request = NONE

### BASIC MESSAGE CHECK

If the standalone customer text is understandable enough to classify or continue:

- continue to Message Type.

If it is not understandable and there are **no attachments**:

- send the approved static message according to Language Policy;
- no Request is created;
- optional/no-Request delivery-failure rule applies;
- end.

If it is not understandable but the message contains one or more attachments:

- create Request;
- `owner = COPILOT`;
- `request_channel = current channel`;
- `state = PROCESSING`;
- append current message reference to `message_refs`;
- store attachment references in `attachment_refs` without analyzing the attachment;
- do not add the message to `accepted_business_message_refs` unless business text was actually accepted;
- go to **Level 2**, where insufficient textual intent may result in `CLARIFY`.

### HUMAN AGENT REQUEST

- create Request;
- `owner = COPILOT`;
- `request_channel = current channel`;
- `state = PROCESSING`;
- append current message reference to `message_refs`;
- retain any attachment references unchanged;
- build Decision Result:
  - `action = HANDOFF_TO_SUPPORT`
  - `decision_reason = HUMAN_REQUESTED`
  - `support_draft_required = false`
- go to **Level 6**.

### COMMUNICATION ONLY

- send approved static/courtesy response where applicable;
- no Request is created;
- end.

### ACTIONABLE / CONTEXTUAL CONTENT

- create Request;
- `owner = COPILOT`;
- `request_channel = current channel`;
- `state = PROCESSING`;
- append current message reference to `message_refs`;
- append current message reference to ordered `accepted_business_message_refs`;
- store any attachment references unchanged in `attachment_refs`;
- go to **Level 2**.

## Request = AWAITING_CUSTOMER

Append the current inbound message reference to `message_refs` and retain any attachment references before classifying it.

Interpret the current message against:

- current Request;
- active `CLARIFY`;
- `expected_customer_input`;
- accepted business-message context.

### Message not interpretable in current context

Reuse **only the understandability test** from the BASIC MESSAGE CHECK defined under `Request = NONE`. Do not execute the `Request = NONE` branch side effects here: do not create a new Request and do not take the no-Request static-response path.

If that understandability test fails:

- `state = PROCESSING`;
- build Decision Result:
  - `action = HANDOFF_TO_SUPPORT`
  - `decision_reason = UNINTERPRETABLE_IN_CONTEXT`
  - `support_draft_required = false`
- include active clarification context where applicable;
- go to **Level 6**.

Otherwise continue to Message Type.

### HUMAN AGENT REQUEST

- `state = PROCESSING`;
- build Decision Result:
  - `action = HANDOFF_TO_SUPPORT`
  - `decision_reason = HUMAN_REQUESTED`
  - `support_draft_required = false`
- go to **Level 6**.

### COMMUNICATION ONLY

- build Decision Result:
  - `action = COMMUNICATION_ONLY_RESPONSE`
  - `decision_reason = COMMUNICATION_ONLY`
- Request remains `AWAITING_CUSTOMER`;
- go to **Level 6**.

### ACTIONABLE / CONTEXTUAL CONTENT

Check `SAME LOGICAL CASE / CONTINUATION?`

If **YES**:

- append current message reference to `accepted_business_message_refs`;
- accept new business input;
- resolve active clarification;
- retain clarification history;
- `state = PROCESSING`;
- go to **Level 2**.

If **NO**:

- do not add the new independent issue to `accepted_business_message_refs`;
- keep its reference in `message_refs` for the handoff/audit context;
- `state = PROCESSING`;
- build Decision Result:
  - `action = HANDOFF_TO_SUPPORT`
  - `decision_reason = MULTIPLE_ISSUES`
  - `support_draft_required = false`
- go to **Level 6**.
