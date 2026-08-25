# Shipping Policy

## 1. Purpose

This policy defines the approved NordShop business information used by the Customer Support Copilot for shipping- and delivery-related customer requests.

It supports the frozen Shipping Use Cases covering:

- general shipping information;
- delivery-delay questions for a specific order;
- delivered-but-not-received reports.

Detailed routing behavior is defined in:

- `docs/product/scenarios.csv`;
- `docs/product/acceptance_criteria.csv`.

Operational order, shipment, and delivery data are defined in:

- `docs/data/oms_data_contract.md`.

## 2. Scope

This policy applies to NordShop MVP orders delivered within Germany.

The policy covers:

- standard delivery options;
- shipping costs and free-shipping threshold;
- available carrier selection;
- standard delivery target;
- order-specific delivery information;
- delivery delays;
- delivered-but-not-received situations;
- tracking information.

NordShop offers only Standard Delivery in the MVP.

Express, premium, same-day, international, and other special delivery services are not part of the MVP.

Direct carrier-system investigation and carrier-side operational details are outside the MVP.

## 3. Delivery Area

NordShop delivers MVP orders only within Germany.

International delivery is not offered in the MVP.

## 4. Delivery Method

NordShop offers one delivery service level:

**Standard Delivery**

No express or premium delivery option is offered in the MVP.

## 5. Shipping Costs

Standard Delivery costs:

- **€4.99** when the order value is below **€30.00**;
- **free of charge** when the order value is **€30.00 or more**.

For the purpose of this rule:

> **Order value = total price of the ordered items after discounts, excluding shipping costs.**

The Copilot must not invent alternative shipping prices, thresholds, surcharges, or promotional shipping rules.

## 6. Carrier Selection

NordShop may offer several carriers for Standard Delivery.

For example, available options may include carriers such as DHL or Hermes.

The customer may select one of the carrier options offered by NordShop during checkout.

The available carrier options may vary.

The Shipping Policy does not define a permanently fixed carrier list.

The carrier selected for the original outbound delivery does not determine the carrier used for a later return. Return-carrier rules are defined in the Returns Policy.

The Copilot must not claim that a specific carrier is available for a specific order unless that information is provided by an approved source.

## 7. Standard NordShop Delivery Target

NordShop's standard delivery target is:

**3 NordShop business days after the order date.**

For this internal target:

- the order date is day 0;
- the next NordShop business day is day 1;
- NordShop business days are Monday through Friday.

The standard delivery target is an internal NordShop service target.

It is not:

- a guaranteed delivery date;
- an order-specific estimated delivery date;
- a statutory delivery deadline.

## 8. Order-Specific Estimated Delivery Date

For a specific order, OMS may provide:

`estimated_delivery_date`

This value represents the current verified operational delivery expectation for that order.

The order-specific estimated delivery date is separate from the general 3-business-day NordShop delivery target.

It may be earlier than, equal to, or later than the standard target.

For a specific-order delivery question, the OMS estimated delivery date is the relevant verified delivery expectation when it is available.

The Copilot must not derive or invent a new order-specific delivery date from:

- the order date;
- the general 3-business-day target;
- customer statements;
- general shipping assumptions;
- unverified carrier information.

## 9. Delivery Delay

For the standard NordShop MVP delay flow, the verified order-specific `estimated_delivery_date` is used to assess whether the shipment is still within its expected delivery window.

This rule applies when OMS does not show the shipment as `DELIVERED`.

### Estimated delivery date has not passed

If the current processing date is on or before the verified `estimated_delivery_date`, the shipment is still within its current order-specific expected delivery window.

The Copilot may communicate the verified shipment information and the available estimated delivery date.

It must not:

- describe the shipment as overdue;
- invent a delay reason;
- invent a revised delivery date;
- promise delivery on an unsupported date.

### Estimated delivery date has passed

If the current processing date is after the verified `estimated_delivery_date` and OMS does not show the shipment as `DELIVERED`, NordShop treats the case as requiring human delivery investigation.

The Copilot may preserve and communicate the verified shipment context.

It must not invent:

- the cause of the delay;
- a revised delivery date;
- carrier investigation results;
- cancellation approval;
- replacement approval;
- refund approval;
- compensation.

### Estimated delivery date unavailable

`estimated_delivery_date` is optional in the OMS data model.

If the customer reports a specific delivery delay and the verified estimated delivery date is unavailable, the Copilot must not create an ETA or determine that the shipment is overdue from the general delivery target alone.

The applicable handling for insufficient verified information is defined in the frozen Scenarios and Acceptance Criteria.

## 10. Delivered but Not Received

A customer may report that a parcel was not received even though OMS records the shipment as `DELIVERED`.

Both pieces of information must remain distinct:

- OMS records the shipment as delivered;
- the customer reports non-receipt.

NordShop treats this as a delivery dispute requiring human handling.

The Copilot must not:

- overwrite the verified OMS delivery status with the customer's statement;
- dismiss the customer's report solely because OMS shows `DELIVERED`;
- determine responsibility for the disputed delivery;
- claim that the parcel was lost;
- invent where or to whom the parcel was delivered;
- promise a replacement, cancellation, refund, or compensation.

Detailed routing is defined in the frozen Scenarios and Acceptance Criteria.

## 11. Tracking Information

A tracking number may be available for a specific order.

If available in OMS, it may be used as verified operational information.

A missing tracking number alone:

- does not mean that the order was not shipped;
- does not make the shipment information invalid;
- does not by itself require human investigation if sufficient verified information remains available.

The Copilot must not invent:

- tracking numbers;
- tracking links;
- parcel locations;
- scan events;
- delivery attempts.

## 12. Carrier Information for a Specific Order

General carrier options may be described from this policy.

Specific carrier-side operational information must not be invented or inferred.

Direct carrier-system integration is outside the MVP.

The Copilot must not invent:

- carrier delay reasons;
- current parcel locations;
- delivery-attempt details;
- depot or parcel-shop information;
- carrier investigation results;
- revised carrier ETAs.

If carrier-side information is required to resolve a case, it must be obtained through the appropriate human or operational process.

## 13. Shipping Information for a Specific Order

Order-specific shipping and delivery information must come from verified OMS data.

Depending on the request and available fields, relevant information may include:

- current shipment status;
- order-specific estimated delivery date;
- confirmed delivery information;
- tracking number, if available.

Customer statements may provide context but do not replace verified OMS operational information.

## 14. Customer-Reported and Verified Information

The Copilot must distinguish between:

- information reported by the customer;
- verified operational information from OMS.

Example:

```text
Customer Request:
"My parcel has not arrived."

OMS:
shipment_status = DELIVERED
```

The customer statement remains customer-reported information.

The OMS value remains the verified operational status.

Neither should silently overwrite the other.

The expected handling of a material conflict is defined in the frozen Global Scenarios and Acceptance Criteria.

## 15. Restricted Shipping-Related Actions

The Copilot provides decision support and response drafts.

It does not autonomously:

- cancel or modify an order;
- approve a replacement;
- approve or initiate a refund;
- determine compensation;
- perform a financial transaction;
- initiate or complete a carrier investigation;
- modify verified OMS information;
- claim that a restricted action has been completed when it has not.

Requests requiring such actions are handled according to the applicable frozen Scenario and Acceptance Criteria.

## 16. Relationship to Returns and Refunds

Shipping, returns, and refunds are related but separate business concepts.

This Shipping Policy defines:

- outbound delivery area;
- outbound delivery method;
- outbound shipping cost;
- free-shipping threshold;
- general carrier selection;
- delivery targets;
- delivery and tracking information;
- delivery-delay business rules.

The Returns Policy is the source of truth for the physical return process, return shipping, and the return carrier.

The Refund Policy is the source of truth for repayment rules, including treatment of the original Standard Delivery cost.

The three types of information must remain distinct even when they relate to the same order.

## 17. Missing Information

This policy must not be supplemented with invented shipping rules or operational facts.

If a shipping request requires approved policy information that is not available, the Copilot follows the handling defined in the frozen Scenarios and Acceptance Criteria.

If a specific-order request requires verified operational information, that information must come from OMS.

Missing optional information, such as a tracking number, does not by itself make the entire request unanswerable when sufficient verified information remains available.

## 18. Policy Boundaries

This policy defines:

- delivery within Germany;
- Standard Delivery as the only MVP delivery service level;
- shipping price and free-shipping threshold;
- the definition of order value used for that threshold;
- general carrier-selection rules;
- NordShop's standard delivery target;
- the role of the order-specific estimated delivery date;
- the business interpretation of a delivery delay;
- the treatment of delivered-but-not-received reports;
- approved boundaries for tracking and carrier information.

This policy does not define:

- OMS entities or field schemas;
- customer-intent classification;
- language handling;
- detailed routing logic;
- `ANSWER`, `CLARIFY`, `ESCALATE`, or `OUT_OF_SCOPE` conditions;
- technical architecture;
- customer identification mechanisms;
- return or refund business rules.

Those concerns are defined in the appropriate product, data, or knowledge-base documents.

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
