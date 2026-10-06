# Level 3 - Required Input and Authorization

**Baseline:** Architecture V14.6

## Input

- Request
- saved `use_case_id`

Required customer input, data sources, and restricted-action safety are read from the current Use Case in `use_cases.csv`.

## Required Input Check

Evaluate the deterministic customer-provided input declared in `Required_Customer_Input`.

In the current MLP:

- `order_id` is the customer-provided business reference required before OMS/private processing;
- customer-provided `item_id` is not required;
- if the customer names or describes an item, that text is preserved as business context but is not converted into a mandatory internal item selector.

If required customer input is missing or ambiguous, identify all currently detectable missing/ambiguous input.

If no successful clarification with `decision_reason = REQUIRED_INPUT_INSUFFICIENT` exists for the current `use_case_id`:

- build Decision Result:
  - `action = CLARIFY`
  - `decision_reason = REQUIRED_INPUT_INSUFFICIENT`
  - `context.expected_customer_input = all currently detectable missing/ambiguous required input`
- go to **Level 6**.

Otherwise:

- build Decision Result:
  - `action = HANDOFF_TO_SUPPORT`
  - `decision_reason = CLARIFICATION_LIMIT`
  - `support_draft_required = false`
- go to **Level 6**.

## Business Reference Contract

For all Use Cases whose `Data_Sources` includes `Order Management System`:

- authorization business reference = `order_id`;
- authorization is bound to the order, not to an individual order item;
- after successful authorization, Level 4 may retrieve only the OMS fields permitted by the current Use Case for the authorized order and its items;
- `item_id` remains an OMS record field but is not required from the customer.

## OMS / Private Processing

If `Data_Sources` does not include `Order Management System` -> go to **Level 4**.

If OMS/private processing is required:

- use verified sender identity supplied by Integration/Security;
- perform authorization lookup only;
- do not expose order/business payload to the model during authorization.

### Technical failure

If authorization lookup cannot execute -> **Technical Error Handling**.

### Sender + order_id match

- `authorization = PASSED` bound to that `order_id`;
- go to **Level 4**.

### No match

If the current Use Case has `Restricted_Action_Safety = YES`:

- do not retrieve OMS/private data;
- preserve customer message references and attachments;
- build `HANDOFF_TO_SUPPORT` using the Use Case's `Restricted_Action_Decision_Reason`;
- `support_draft_required = false`;
- go to **Level 6**.

Otherwise:

- build Decision Result:
  - `action = ACCESS_EMAIL_INSTRUCTION`
  - `decision_reason = AUTHORIZATION_NOT_PASSED`
- go to **Level 6**.

A completed no-match is a normal business outcome. It must not be used for a technical authorization failure.
