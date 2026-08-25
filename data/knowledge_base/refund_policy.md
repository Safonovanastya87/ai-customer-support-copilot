# Refund Policy

## 1. Purpose

This policy defines the approved NordShop business information used by the Customer Support Copilot for refund-related customer requests.

It supports the frozen refund Use Cases covering:

- general refund information;
- refund rules for a specific case;
- refund status information;
- customer requests for refund-related actions.

Detailed routing behavior is defined in:

- `docs/product/scenarios.csv`;
- `docs/product/acceptance_criteria.csv`.

Operational order, item, return, and refund data are defined in:

- `docs/data/oms_data_contract.md`.

## 2. Scope

The standard NordShop MVP refund flow applies to withdrawal and return cases covered by the Returns Policy.

The Returns Policy is the source of truth for the modeled withdrawal-right scope and return eligibility assumptions.

Refunds based on other business processes, such as warranty, defect, damage, compensation, or other unsupported claims, are outside the refund MVP scope.

## 3. General Refund Rule

For a standard full withdrawal-based refund, NordShop refunds:

- the price of the goods covered by the withdrawal;
- the original NordShop Standard Delivery cost actually paid by the customer.

The Shipping Policy is the source of truth for the applicable Standard Delivery pricing and free-shipping rules.

The Copilot may explain the applicable refund rule but does not calculate or authorize the final refund amount.

## 4. Partial Returns and Partial Refunds

For partial returns permitted under the Returns Policy, the concrete treatment of the original Standard Delivery cost in an individual partial-return case, together with the final partial-refund calculation and approval, is handled by an authorized human employee.

The Copilot does not independently recalculate the original order's shipping charge or determine the final financial effect of a partial return.

The Copilot may provide:

- the applicable refund rules;
- verified order and item information;
- verified return and refund status information.

It must not determine the final partial-refund amount.

## 5. When a Refund May Be Released

NordShop follows the applicable statutory refund rule.

Physical receipt of the returned goods is not always required before repayment can be released.

Where applicable, repayment may be released when NordShop has received either:

- the returned goods; or
- acceptable proof of dispatch.

If a case requires an individual assessment of whether the available evidence is sufficient, that assessment remains under human control.

## 6. Repayment Period

NordShop repays without undue delay and no later than 14 days after receiving the withdrawal declaration, subject to the applicable statutory right to withhold repayment until the returned goods or acceptable proof of dispatch have been received.

NordShop does not introduce separate fictional statutory deadlines for refund processing.

## 7. NordShop Refund Initiation Target

Once a refund can be released under the applicable refund rules, NordShop targets initiation of the refund within:

**3 NordShop business days.**

For this internal service target, NordShop business days are Monday through Friday.

This is a NordShop internal service target.

Where an applicable statutory repayment obligation requires earlier action, the statutory requirement takes precedence; the internal target must not extend it.

The internal target is not:

- a statutory deadline;
- a guarantee that the refunded amount will already be visible in the customer's bank account;
- a replacement for the applicable statutory repayment rules.

## 8. Refund Payment Method

Refunds are made to the original payment method.

A different payment method is not the standard NordShop MVP path and may be used only where it has been explicitly agreed and does not cause additional cost to the customer.

The Copilot does not autonomously change the payment method.

## 9. Bank and Payment-Provider Processing Time

After NordShop has initiated a refund, the time until the refunded amount becomes visible to the customer may depend on the bank or payment provider.

NordShop does not promise a fixed bank-processing or payment-provider-processing time.

The Copilot may communicate the verified NordShop refund status but must not invent a date by which the money will become visible to the customer.

## 10. Value Reduction

A reduction in value may be legally relevant where the applicable statutory conditions are met.

The Copilot does not autonomously:

- assess the physical condition of returned goods;
- decide whether value reduction applies;
- calculate a deduction;
- determine the resulting refund amount.

These decisions remain under authorized human control.

## 11. Refund Rules for a Specific Case

A customer may ask how the refund rules apply to a specific purchase or return situation.

In such cases, the Copilot may combine:

- the applicable approved Refund Policy information;
- verified order information;
- verified item information;
- verified return information;
- verified refund information.

The Copilot provides rules and verified facts for employee assessment.

It does not make the final individual legal, financial, or discretionary decision.

## 12. Refund Amounts

The Copilot does not determine or authorize the final refund amount.

It may communicate verified factual order or item values when those values are available from an approved source and are relevant to the request.

It must not present its own calculation as the final refund amount.

## 13. Refund Status

The current status of a specific refund is operational information.

Refund status must be taken from the verified Order Management System (OMS).

The Copilot may communicate the verified refund status recorded in OMS and may provide relevant Refund Policy information where appropriate.

Customer statements about refund progress do not overwrite or replace verified OMS information.

If customer-reported refund information materially conflicts with verified OMS information, the expected handling is defined in the frozen Global Scenarios and Acceptance Criteria.

## 14. Refund Actions

Refund-related business actions remain under authorized human control.

The Copilot does not autonomously:

- approve a refund;
- initiate a refund;
- issue or execute a refund;
- modify a refund;
- change a verified refund status;
- change the refund payment method;
- perform a financial transaction.

If a customer asks NordShop to perform such an action, the request is handled according to the applicable frozen Scenario and Acceptance Criteria.

The Copilot must not claim that a refund-related action has been completed unless the authoritative process shows that it occurred.

## 15. Relationship to Shipping and Returns

Shipping, returns, and refunds are related but separate business concepts.

The Shipping Policy is the source of truth for:

- outbound Standard Delivery;
- outbound shipping pricing;
- the free-shipping threshold.

The Returns Policy is the source of truth for:

- the modeled withdrawal-right scope;
- withdrawal declarations;
- physical return rules;
- the return procedure;
- return shipping.

This Refund Policy is the source of truth for:

- repayment rules;
- treatment of the original outbound Standard Delivery cost;
- refund timing;
- refund payment method;
- refund-related financial boundaries.

A completed physical return must not automatically be described as a completed refund unless verified refund information supports that statement.

## 16. Customer-Reported and Verified Information

The Copilot must distinguish between:

- information reported by the customer;
- verified operational information from OMS.

Example:

```text
Customer Request:
"I still have not received my refund."

OMS:
refund_status = COMPLETED
```

The customer statement remains customer-reported information.

The OMS value remains the verified operational status.

Neither should silently overwrite the other.

The expected handling of a material conflict is defined in the frozen Global Scenarios and Acceptance Criteria.

## 17. Missing Information

The Refund Policy must not be supplemented with invented business rules, deadlines, amounts, or outcomes.

If a refund-related request requires approved policy information that is not available, the Copilot follows the handling defined in the frozen Scenarios and Acceptance Criteria.

If a specific refund request requires verified operational information, that information must come from OMS.

Customer-provided information must not be treated as a substitute for unavailable verified OMS data.

## 18. Policy Boundaries

This policy defines:

- the standard NordShop refund scope;
- the standard refund components;
- partial-refund business boundaries;
- the standard statutory repayment rule used by the MVP;
- the NordShop internal refund-initiation target;
- the refund payment method;
- the distinction between NordShop processing time and bank/payment-provider processing time;
- high-level boundaries for value reduction and refund amounts;
- business constraints around refund-related actions.

This policy does not define:

- OMS entities or field schemas;
- customer-intent classification;
- language handling;
- routing logic;
- `ANSWER`, `CLARIFY`, `ESCALATE`, or `OUT_OF_SCOPE` conditions;
- technical architecture;
- statutory deadline calculators;
- legal-calendar engines;
- automated legal interpretation;
- detailed statutory exception logic.

Those concerns are defined in the appropriate product, data, or technical documentation, or remain under human handling.

## 19. Related Documentation

### Product

- `docs/product/discovery.md`
- `docs/product/use_cases.csv`
- `docs/product/scenarios.csv`
- `docs/product/acceptance_criteria.csv`

### Data

- `docs/data/oms_data_contract.md`

### Knowledge Base

- `data/knowledge_base/shipping_policy.md`
- `data/knowledge_base/returns_policy.md`
- `data/knowledge_base/refund_policy.md`
