# NordShop Shipping Policy

## 1. Scope

This policy defines the standard NordShop rules for handling customer requests related to:

- shipment status;
- expected delivery;
- delivery delays;
- tracking information;
- delivered-but-not-received cases.

The policy applies to orders that can be identified in the NordShop Order Management System (OMS).

The delivery targets and escalation thresholds defined below are internal NordShop service rules for the MVP and must not be presented as statutory German delivery periods or legal entitlements.

---

## 2. Source of Operational Information

The Order Management System (OMS) is the authoritative source for current operational order and shipment information.

Relevant information may include:

- order identification;
- customer identification;
- shipment status;
- estimated delivery date;
- delivery date;
- tracking number.

Customer statements are treated as reported customer context and do not replace verified operational information stored in OMS.

If a customer statement conflicts with OMS regarding a current operational shipment fact, the OMS value remains the authoritative operational fact while the customer's statement is preserved as additional context.

---

## 3. Standard Delivery Target

NordShop's standard delivery target is:

**2–5 business days**

This is an internal NordShop service target.

For a specific order, the `estimated_delivery_date` stored in OMS is the applicable operational delivery estimate.

The order-specific estimated delivery date takes precedence over the general 2–5-business-day delivery target when answering an order-specific request.

---

## 4. Business Day Definition

For the MVP, a business day is:

**Monday through Friday**

Saturdays and Sundays are not counted as business days.

Public holidays are not modeled separately in the MVP.

This definition is used consistently for all business-day calculations in this policy.

---

## 5. Expected Delivery Date

An order is not considered overdue while the current date is on or before the `estimated_delivery_date` stored in OMS.

If the customer reports a delay before the estimated delivery date has passed:

- the current shipment status may be provided;
- the estimated delivery date may be communicated;
- the shipment must not be classified as overdue solely because the customer expected it earlier.

No investigation or remedy should be presented as necessary solely because the estimated delivery date has not yet been reached.

---

## 6. Delayed Shipments

A shipment is considered delayed when:

- the `estimated_delivery_date` has passed; and
- the parcel has not been delivered.

### 6.1 NordShop Grace Period

As an internal NordShop customer-support rule, a grace period of:

**2 business days**

applies after the estimated delivery date.

During the grace period:

- the customer may be informed that the shipment is delayed;
- the current verified shipment information should be provided when available;
- the remaining waiting period may be explained;
- standard shipment investigation is not yet required;
- no investigation, refund, replacement, or other remedy may be presented as already initiated or approved unless confirmed by an approved source.

### 6.2 Delay Beyond the Grace Period

If the parcel remains undelivered after the 2-business-day grace period, the case requires human investigation.

Relevant verified shipment information should be made available to the support employee.

The system must not claim that an investigation, refund, replacement, compensation, or other remedy has already been initiated, approved, or completed unless confirmed by an approved source.

---

## 7. Delivered but Not Received

If OMS reports the parcel as delivered but the customer states that the parcel was not received, the case requires human investigation.

Both facts must be preserved:

- OMS reports the parcel as delivered;
- the customer reports that the parcel was not received.

The customer statement must not be rejected solely because OMS shows a delivered status.

At the same time, the customer statement does not replace the OMS operational status.

The system must not:

- state that the customer personally received the parcel;
- promise or approve a refund;
- promise or approve a replacement;
- claim that an investigation has already been initiated unless confirmed by an approved source.

A delivered-but-not-received dispute must be resolved before downstream standard return or return-based refund eligibility is determined.

---

## 8. Tracking Information

If a tracking number is available in OMS, it may be included in the customer-facing response.

If no tracking number is available:

- no tracking number may be invented or inferred;
- the absence of a tracking number alone does not require human investigation;
- other verified shipment information may still be provided when sufficient to answer the request.

A missing tracking number must not be treated as proof that the shipment has not been sent.

---

## 9. Missing or Unavailable Shipment Information

A reliable order-specific answer must not be produced when information required to resolve the request is unavailable or unusable.

Examples include:

- OMS cannot be accessed;
- the required lookup fails;
- the supplied order cannot be matched;
- a required shipment field is missing or unusable.

If the missing information can reasonably be supplied or corrected by the customer, clarification should be requested.

If required internal operational information is unavailable, the case requires human handling.

Missing operational facts must not be invented, assumed, or inferred.

---

## 10. Human Investigation Rules

A shipping-related case requires human investigation when:

1. the shipment remains undelivered after the 2-business-day grace period;
2. OMS reports the parcel as delivered but the customer reports that it was not received;
3. required internal shipment information is unavailable or unusable and a reliable answer cannot be produced;
4. the Shipping Policy does not provide a reliable rule for resolving the case.

Further investigation, discretionary decisions, or business actions remain with a human support employee.

---

## 11. Policy Boundaries

The Shipping Policy determines how shipment-related operational situations are handled.

If an unresolved shipping condition affects a downstream return or refund decision, the shipping condition must be resolved first.

For example:

- a delivered-but-not-received dispute must not be treated as a normal confirmed delivery for return eligibility;
- a refund must not be determined solely because OMS shows `DELIVERED` while receipt is disputed by the customer.

---

## 12. Standard MVP Rules

For the MVP:

- standard NordShop delivery target: **2–5 business days**;
- delayed-shipment grace period: **2 business days**;
- business days: **Monday through Friday**;
- public holidays: **not modeled separately**;
- OMS is the authoritative operational source;
- delivered-but-not-received cases require human investigation.