# Returns Policy

## 1. Purpose

This policy defines the approved NordShop business information used by the Customer Support Copilot for withdrawal- and return-related customer requests.

It supports the frozen Returns Use Cases covering:

- general withdrawal and return rules;
- withdrawal and return rules for a specific purchased item;
- withdrawal and return procedure;
- withdrawal declarations and requests for return-related actions;
- return status questions.

Detailed routing behavior is defined in:

- `docs/product/scenarios.csv`;
- `docs/product/acceptance_criteria.csv`.

Operational order, item, shipment, and return data are defined in:

- `docs/data/oms_data_contract.md`.

Refund-specific repayment rules are defined in:

- `data/knowledge_base/refund_policy.md`.

## 2. Scope

The standard NordShop MVP withdrawal and return flow applies to the products represented in the MVP.

For the MVP, all modeled products are assumed to fall within the standard withdrawal-right flow.

Product categories subject to special statutory withdrawal exceptions are not modeled in the MVP data.

Business processes outside the supported withdrawal and return Use Cases are not covered by this policy.

## 3. Standard Withdrawal Right

For products represented in the NordShop MVP, the standard withdrawal period is:

**14 days.**

For the standard post-delivery case, the withdrawal period begins after the customer receives the goods in accordance with the applicable statutory withdrawal rules.

The MVP does not implement automated legal interpretation for special or exceptional withdrawal situations.

Cases requiring individual legal assessment remain under human handling.

## 4. Withdrawal Declaration

A withdrawal is made through an unequivocal declaration communicating the customer's decision to withdraw.

The customer does not have to provide a reason.

The withdrawal declaration and the physical return of the goods are separate events.

The customer may therefore declare withdrawal before the physical return is completed.

The Copilot must not treat the physical return of an item as a substitute for a withdrawal declaration where a declaration is required.

## 5. Withdrawal Channels

For applicable online contracts, NordShop provides an online withdrawal function.

A customer may also communicate an unequivocal withdrawal declaration through another communication channel accepted by NordShop.

A customer support request may itself contain an unequivocal withdrawal declaration.

Example:

> "Hiermit widerrufe ich meine Bestellung."

The Copilot may recognize that the customer has communicated a withdrawal declaration.

The customer must not be instructed to make the same declaration again merely because the current message has not yet been represented in OMS.

The Copilot does not autonomously register or execute the withdrawal.

Requests requiring NordShop to register, perform, or otherwise execute a withdrawal or return-related business action are handled according to the frozen Scenarios and Acceptance Criteria.

## 6. Standard Return Period

Following a valid withdrawal declaration, the goods must be returned without undue delay and no later than:

**14 days after the withdrawal declaration.**

Withdrawal declaration, return dispatch, and physical receipt by NordShop are separate events.

Timely dispatch within the applicable return period is sufficient for the standard modeled return flow.

The Copilot must not invent a different return deadline.

## 7. Partial Returns

NordShop allows customers to return individual items from an order.

A partial return does not require all items in the order to be returned.

The Copilot may provide:

- the applicable withdrawal and return rules;
- verified information about the relevant order and item;
- verified return-status information.

The concrete financial consequences of a partial return, including the final partial-refund amount, are handled under the Refund Policy and remain under authorized human control where an individual calculation or decision is required.

## 8. Return Shipping Cost

For the standard NordShop MVP withdrawal flow, return shipping is free to the customer when the NordShop return method is used.

NordShop provides a prepaid return option.

The customer does not pay the return-shipping cost when using this NordShop return method.

This is a NordShop company policy and must not be presented as a general statutory rule applying to every online purchase in Germany.

## 9. Return Label and Digital Return Option

NordShop provides the customer with a prepaid return label or an equivalent digital return option, such as a QR code.

The MVP does not require a specific carrier to be fixed in the policy.

The applicable carrier and available handover locations are provided through the NordShop return instructions associated with the return label or digital return option.

The carrier used for the original outbound delivery does not determine the carrier used for the return. The applicable return carrier is the carrier specified in the NordShop return instructions.

The Copilot must not invent a carrier, label, QR code, or return location that is not supported by the approved NordShop return information.

## 10. Return Handover

The customer hands the return parcel over at:

- a parcel shop;
- a service point; or
- another drop-off location

specified in the NordShop return instructions.

Home pickup is not modeled as part of the standard MVP return procedure.

## 11. Packaging

The customer must package the goods securely for return transport.

Original packaging is not required.

No additional special packaging requirements are modeled for the standard MVP return flow unless they are explicitly provided in approved NordShop return information.

## 12. Documents Inside the Parcel

No additional document is required inside the return parcel.

The return is identified through the NordShop return label or digital return option and the associated return information.

The customer is not required to include a separate return form, invoice, or written withdrawal declaration inside the parcel for the standard MVP flow.

## 13. Proof of Dispatch

The customer should retain the proof of dispatch until the return and refund process has been completed.

Return dispatch and physical receipt are separate events.

Acceptable proof of dispatch may be relevant to subsequent refund processing under the Refund Policy.

For Copilot processing, verified return progress is represented through the operational return information available in OMS.

A customer statement such as:

> "I already sent it back."

does not by itself replace verified OMS return information.

## 14. Standard Return Procedure

For a standard NordShop return:

1. The customer submits an unequivocal withdrawal declaration through the NordShop online withdrawal function or another accepted communication channel.
2. NordShop provides the customer with the return instructions and a prepaid return label or equivalent digital return option.
3. The customer packages the relevant item or items securely for return transport. Original packaging is not required.
4. No additional document is required inside the parcel.
5. The customer hands the parcel over at a parcel shop, service point, or other drop-off location specified in the NordShop return instructions.
6. The customer retains the proof of dispatch until the return and refund process has been completed.
7. NordShop processes the return and records the verified return status in OMS.
8. Refund handling follows the separate Refund Policy.

The Copilot may explain this approved procedure.

It must not invent additional return steps, addresses, carrier information, packaging requirements, or operational instructions.

## 15. Return Rules for a Specific Purchased Item

A customer may ask how the withdrawal or return rules apply to a specific purchased item.

In such cases, the Copilot may combine:

- the applicable approved Returns Policy information;
- verified order information;
- verified item information;
- verified shipment or delivery information where relevant;
- verified return-status information.

The Copilot provides approved rules and verified facts for employee assessment.

It does not make the final individual legal or discretionary business decision.

## 16. Return Status

The current status of a specific return is operational information.

Return status must be taken from the verified Order Management System (OMS).

The Copilot may communicate the verified return status recorded in OMS.

Customer statements about return progress do not overwrite or replace verified OMS information.

If customer-reported return information materially conflicts with verified OMS information, the expected handling is defined in the frozen Global Scenarios and Acceptance Criteria.

## 17. Relationship to Refunds

Returns and refunds are related but separate business concepts.

The Returns Policy defines:

- the standard withdrawal right;
- withdrawal declarations;
- the standard return period;
- partial-return support;
- free return shipping;
- the prepaid return method;
- packaging and handover rules;
- the standard return procedure.

The Refund Policy is the source of truth for:

- what is repaid;
- treatment of the original outbound Standard Delivery cost;
- the statutory repayment period;
- when repayment may be released;
- the NordShop refund-initiation target;
- the refund payment method;
- financial decision boundaries.

A return being dispatched or received must not automatically be described as a completed refund unless verified refund information supports that statement.

## 18. Restricted Actions

The Copilot provides decision support and response drafts.

It does not autonomously:

- register or execute a withdrawal;
- perform a return-related business action;
- modify an order;
- approve a discretionary exception;
- determine a final refund amount;
- approve or execute a refund;
- modify verified OMS information;
- claim that a restricted action has been completed when it has not.

Requests requiring such actions are handled according to the applicable frozen Scenario and Acceptance Criteria.

## 19. Customer-Reported and Verified Information

The Copilot must distinguish between:

- information reported by the customer;
- verified operational information from OMS.

Example:

```text
Customer Request:
"I already sent the item back."

OMS:
return_status = NONE
```

The customer statement remains customer-reported information.

The OMS value remains the verified operational status.

Neither should silently overwrite the other.

The expected handling of a material conflict is defined in the frozen Global Scenarios and Acceptance Criteria.

## 20. Missing Information

This policy must not be supplemented with invented business rules or operational return instructions.

If a return-related request requires approved policy information that is not available, the Copilot follows the handling defined in the frozen Scenarios and Acceptance Criteria.

If a specific order, item, or return request requires verified operational information, that information must come from OMS.

Customer-provided information must not be treated as a substitute for unavailable verified OMS data.

## 21. Policy Boundaries

This policy defines:

- the standard NordShop withdrawal right for the modeled MVP;
- the withdrawal declaration rule and supported channels;
- the standard return period;
- partial-return support;
- free return shipping;
- prepaid return-label and digital-return options;
- return handover and packaging rules;
- proof-of-dispatch guidance;
- the standard return procedure;
- high-level business constraints around withdrawal and return actions.

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
- detailed statutory exception logic;
- final refund calculations.

Those concerns are defined in the appropriate product, data, refund-policy, or technical documentation, or remain under human handling.

## 22. Related Documentation

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
