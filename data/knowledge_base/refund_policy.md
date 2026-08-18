# NordShop Refund Policy

## 1. Scope

This policy defines the standard NordShop rules for determining and explaining refund eligibility and refund processing.

For the MVP, the standard refund flow covered by this policy is:

**a refund following a standard return under the NordShop Returns Policy**

Refund requests based on circumstances outside this standard return-based refund flow require human review unless another approved NordShop policy explicitly defines the applicable rule.

Examples outside the standard return-based refund flow include:

- disputed delivery;
- discretionary compensation;
- goodwill refunds;
- other exceptional refund requests not defined by this policy.

The processing targets defined below are internal NordShop service rules and must not be presented as statutory German refund periods.

---

## 2. Source of Operational Information

The Order Management System (OMS) is the authoritative source for operational return and refund information.

Relevant information may include:

- order identification;
- customer identification;
- purchased items;
- return status;
- return receipt date;
- refund status;
- refund initiation date.

Customer statements may provide additional context but do not replace verified OMS information.

Only information belonging to the correctly identified customer, order, and item may be used.

---

## 3. Relationship with Returns Policy

Return eligibility and refund eligibility represent different stages.

The NordShop Returns Policy determines whether an item may be returned under the standard return rules.

The Refund Policy determines whether the operational state of that return allows the standard refund process to proceed.

Being eligible to return an item does not mean that a refund:

- is already eligible for processing;
- has been initiated;
- has been completed.

The standard process is:

Return eligibility  
→ item returned by customer  
→ return received by NordShop  
→ NordShop refund processing  
→ refund initiated  
→ payment processing  
→ NordShop refund operation completed

---

## 4. Standard Refund Eligibility

For a standard return-based refund, refund processing may proceed when:

1. the relevant order can be identified;
2. the relevant item can be identified;
3. the return is associated with an eligible standard return;
4. NordShop has confirmed receipt of the returned item;
5. the required operational information is available;
6. no unresolved exception or discretionary decision is required.

If the returned item has not yet been confirmed as received, the system must not state that standard refund processing has started.

Actual refund execution remains a restricted human- or system-controlled business action.

---

## 5. Delivery-Related Refund Requests

A refund request based on a disputed delivery is not treated as a standard return-based refund.

If OMS reports the parcel as delivered but the customer reports that it was not received, the case must first be handled according to the NordShop Shipping Policy.

The system must not determine standard return-based refund eligibility solely from the OMS delivered status while receipt is disputed.

A refund, replacement, or compensation must not be promised as the automatic result of a delivered-but-not-received report.

---

## 6. NordShop Refund Processing Target

After receipt of the returned item has been confirmed, NordShop's internal target is to initiate the applicable standard refund within:

**2 business days**

During this period, the return may be reviewed and the refund prepared for initiation.

The system must not state that the refund has been initiated until this is confirmed by OMS.

If more than 2 business days have passed since confirmed return receipt and OMS still does not show the refund as initiated, and no approved information explains the delay, the case requires human review.

---

## 7. Payment Processing Estimate

After OMS confirms that the refund has been initiated, the amount typically becomes visible on the customer's original payment method within:

**3–5 business days**

This period represents an expected payment-processing time after refund initiation.

The actual time may depend on the payment provider or financial institution.

The system may communicate the standard estimate but must not guarantee an exact bank-account credit date unless an approved operational source provides one.

If more than 5 business days have passed since confirmed refund initiation and the customer reports that the funds are still not visible, and no approved information explains the delay, the case requires human review.

---

## 8. Business Day Definition

For the MVP, a business day is:

**Monday through Friday**

Saturdays and Sundays are not counted as business days.

Public holidays are not modeled separately.

The same definition is used for:

- the 2-business-day NordShop refund initiation target;
- the 3–5-business-day payment-processing estimate.

---

## 9. Refund Status

OMS is the authoritative source for the current NordShop refund status.

For the MVP, relevant states are:

- `NOT_INITIATED`;
- `INITIATED`;
- `COMPLETED`.

### NOT_INITIATED

NordShop has not yet confirmed initiation of the refund.

The system must not describe the refund as initiated or completed.

### INITIATED

NordShop has confirmed initiation of the refund.

The standard 3–5-business-day payment-processing estimate may be communicated.

### COMPLETED

`COMPLETED` means that NordShop has completed its refund operation.

It does not prove that the refunded amount is already visible in the customer's bank account or payment account.

The system must not state that the customer has already received the funds unless this is confirmed by an approved source.

---

## 10. Customer Requests to Issue a Refund

A customer may explicitly ask NordShop to issue, approve, or execute a refund.

Actual refund execution is a restricted business action.

The system may:

- evaluate standard return-based refund eligibility;
- explain the applicable Refund Policy;
- communicate verified return and refund status;
- explain the standard refund timeline.

The system must not autonomously:

- issue a refund;
- approve a refund;
- initiate a financial transaction.

A request requiring actual refund execution must remain with a human or authorized operational process.

---

## 11. Refund Amount

The MVP does not calculate a refund amount independently.

The system must not calculate, invent, estimate, or promise a refund amount unless the exact applicable amount is provided by an approved operational source.

This avoids unsupported assumptions involving:

- discounts;
- coupons;
- partial returns;
- shipping costs;
- fees;
- partial refunds;
- other order-specific adjustments.

If an exact refund amount is required but unavailable from an approved source, the case requires human handling.

---

## 12. Refund Exceptions

A refund case requires human review when:

1. the request falls outside the standard return-based refund flow;
2. the customer requests an exception to a return or refund rule;
3. a discretionary compensation decision is required;
4. the standard policy does not clearly resolve the case;
5. required operational information is unavailable;
6. the 2-business-day refund initiation target has been exceeded without sufficient explanation;
7. the 5-business-day payment-processing estimate has been exceeded and the customer reports that funds are not visible.

The system must not grant, approve, or promise a discretionary refund or compensation.

---

## 13. Missing Required Information

A reliable refund decision must not be made when information required to apply this policy is unavailable or unusable.

Examples include:

- the order cannot be identified;
- the relevant item cannot be identified;
- return receipt information is missing or unusable;
- current refund status is unavailable when required;
- refund initiation date is unavailable when required to evaluate processing time.

If required information can reasonably be supplied or corrected by the customer, clarification should be requested.

If required information is missing from an approved internal source, the case requires human handling.

Missing operational facts must not be invented, assumed, or inferred.

---

## 14. Cross-Policy Precedence

A downstream refund decision must not be made when it depends on an unresolved upstream operational condition.

The standard order of decision-making is:

Shipping condition  
→ Return eligibility  
→ Return completion / receipt  
→ Refund eligibility  
→ Refund processing

For example:

A delivered-but-not-received dispute must first be resolved under the Shipping Policy.

Only after the relevant upstream condition has been resolved may a standard return or return-based refund decision be made.

---

## 15. Standard MVP Rules

For the MVP:

- standard refunds are **return-based refunds governed by the Returns Policy**;
- refund processing starts after the returned item is confirmed as received;
- NordShop target from confirmed return receipt to refund initiation: **within 2 business days**;
- expected payment-processing time after confirmed refund initiation: **3–5 business days**;
- business days: **Monday through Friday**;
- public holidays: **not modeled separately**;
- `COMPLETED` means NordShop completed its refund operation, not necessarily that funds are already visible to the customer;
- refund execution is a restricted business action;
- exceptional refund decisions require human review;
- OMS is the authoritative operational source.