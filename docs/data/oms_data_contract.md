# OMS Data Contract

## 1. Purpose

The Order Management System (OMS) is the verified operational source used by the NordShop Customer Support Copilot for order-specific information.

The MVP uses a simplified OMS data model that provides the operational information needed by the frozen Use Cases, Scenarios, Acceptance Criteria, and approved Knowledge Base policies for:

- Order Status;
- Shipping;
- Returns;
- Refunds.

The OMS stores verified operational data. It does not define product-routing behavior or business-policy rules.

Routing and handling decisions such as `ANSWER`, `CLARIFY`, `ESCALATE`, and `OUT_OF_SCOPE` are defined in:

- `docs/product/scenarios.csv`;
- `docs/product/acceptance_criteria.csv`.

Customer-reported information may provide context but does not overwrite verified OMS information.

## 2. Data Model Overview

The simplified MVP OMS contains two primary entities:

```text
orders
  |
  └── order_items
```

Order-level data represents:

- order identity;
- current shipment state;
- available delivery information;
- the original outbound shipping charge actually paid;
- the original payment method.

Item-level data represents:

- purchased item identity;
- the recorded item price;
- current return state;
- current refund state.

The MVP models:

- one shipment per order;
- one original payment method per order;
- at most one active modeled return process per order item;
- at most one active modeled refund process per order item.

These are MVP data-model simplifications and do not define broader NordShop business capabilities outside the frozen scope.

All monetary fields in the MVP OMS are represented in EUR.

## 3. Order Model

### `orders`

| Field | Type | Required | Description |
|---|---|---:|---|
| `order_id` | string | yes | Unique order identifier |
| `shipment_status` | enum | yes | Current verified shipment state |
| `estimated_delivery_date` | date | no | Current order-specific expected delivery date, if available |
| `delivered_at` | datetime | conditional | Confirmed delivery date and time |
| `tracking_number` | string | no | Shipment tracking identifier, if available |
| `carrier` | string | no | Carrier recorded for the specific outbound shipment, if available |
| `shipping_cost_paid` | decimal | yes | Original outbound Standard Delivery charge actually paid by the customer; may be `0.00` |
| `payment_method` | string | yes | Verified original payment method used for the order |

The OMS Data Contract does not reproduce the Shipping Policy pricing or free-shipping threshold. `shipping_cost_paid` stores the verified operational value actually recorded for the order.

The OMS Data Contract does not define refund payment-method rules. `payment_method` stores the verified original payment method; the applicable refund rule is defined in the Refund Policy.

### `shipment_status`

Allowed values:

- `PROCESSING`
- `SHIPPED`
- `DELIVERED`

The shipment status is verified OMS information and may be used when answering order-status and shipping-related requests.

For the MVP, `UC-OS-01` uses the verified `shipment_status` together with available delivery information as the current operational status of the order. Return and refund states are represented separately at item level and are not part of `UC-OS-01`. No separate `order_status` field is modeled.

## 4. Shipment Information

The MVP models one shipment per order.

Shipment information is stored at order level.

The OMS may provide:

- current `shipment_status`;
- `estimated_delivery_date`, when available;
- `tracking_number`, when available;
- `carrier`, when available;
- confirmed `delivered_at`, when the shipment is recorded as delivered.

### Delivery-state consistency

If:

```text
shipment_status = DELIVERED
```

then:

```text
delivered_at
```

must be present.

If:

```text
shipment_status = PROCESSING
```

or:

```text
shipment_status = SHIPPED
```

then `delivered_at` must be empty.

A missing `tracking_number`, `estimated_delivery_date`, or `carrier` is allowed.

Whether missing optional delivery information affects the final handling is defined by the frozen Scenarios and Acceptance Criteria rather than by this data contract.

The current processing date used when applying date-based Shipping Policy rules is application runtime context and is not stored as an OMS field.

The OMS Data Contract does not calculate or define the NordShop business-day calendar.

## 5. Order Item Model

### `order_items`

| Field | Type | Required | Description |
|---|---|---:|---|
| `item_id` | string | yes | Unique order-item identifier |
| `order_id` | string | yes | Foreign key to `orders.order_id` |
| `product_name` | string | yes | Product name used for support context |
| `item_price` | decimal | yes | Verified recorded price of the order item after applicable discounts |
| `return_status` | enum | yes | Current verified return state |
| `refund_status` | enum | yes | Current verified refund-processing state |

Each order item belongs to exactly one order.

The item-level model supports requests about:

- return rules for a specific purchased item;
- current return status;
- refund rules for a specific case;
- current refund status.

`item_price` is a verified factual value. The OMS Data Contract does not define or calculate a final refund amount.

## 6. Return Status Model

### `return_status`

Allowed values:

- `NONE`
- `DECLARED`
- `DISPATCHED`
- `RECEIVED`

Descriptions:

- `NONE` — no return process is currently represented for the item;
- `DECLARED` — a return or withdrawal-related state has been registered in the operational process;
- `DISPATCHED` — the returned item is recorded as dispatched back;
- `RECEIVED` — NordShop records the returned item as received.

`DECLARED` represents an OMS operational state. It does not mean that the Copilot itself registered or executed a withdrawal declaration.

The OMS return state is treated as verified operational information.

A customer statement about a return does not change `return_status`.

If customer-reported return information materially conflicts with the verified OMS state, handling is defined by the frozen Global Scenarios and Acceptance Criteria.

### Proof of dispatch boundary

The MVP OMS does not model a separate proof-of-dispatch document or evidentiary assessment field.

`return_status = DISPATCHED` means only that the operational return state is recorded as dispatched.

Whether a particular proof of dispatch is acceptable for refund-release purposes is a human-controlled assessment under the Refund Policy and must not be inferred solely from the enum value.

## 7. Refund Status Model

### `refund_status`

Allowed values:

- `NOT_INITIATED`
- `INITIATED`
- `COMPLETED`

Descriptions:

- `NOT_INITIATED` — no refund process is currently recorded as initiated;
- `INITIATED` — the refund process is recorded as initiated;
- `COMPLETED` — NordShop records the refund process as completed.

The OMS refund state is treated as verified operational information.

`COMPLETED` describes the OMS operational state only. It does not guarantee that the refunded amount is already visible in the customer's bank or payment-provider account.

Customer-reported information remains separate from the OMS state.

If customer-reported refund information materially conflicts with the verified OMS state, handling is defined by the frozen Global Scenarios and Acceptance Criteria.

## 8. Record Identification

Order- and item-specific processing requires identification of the relevant OMS record.

Supported identifiers include:

- `order_id`;
- `item_id`, where item-level information is required.

Because return and refund state are modeled at item level, `item_id` is required when a specific item-level return or refund cannot be identified unambiguously from the available request context.

If a required customer-provided reference is missing, ambiguous, or cannot be matched, the handling behavior is defined in the frozen Global Scenarios and Acceptance Criteria.

The data contract itself defines only the available OMS identifiers and relationships.

## 9. Missing and Optional Data

The OMS must not be supplemented with invented operational values.

Required fields must be present according to this contract.

Optional fields may be absent.

Examples of optional OMS information include:

- `tracking_number`;
- `estimated_delivery_date`;
- `carrier`.

The absence of optional information does not make an OMS record invalid.

Whether missing information is sufficient to answer a request or requires human handling is defined by the frozen Scenarios and Acceptance Criteria.

## 10. OMS and Customer-Reported Information

The MVP keeps customer-reported information and verified OMS information separate.

Example:

```text
Customer Request:
"My parcel has not arrived."

OMS:
shipment_status = DELIVERED
```

The customer statement remains customer-reported information.

The OMS state remains verified operational information.

The Copilot must not silently overwrite one with the other.

The expected handling of such a conflict is defined in the frozen product Scenarios and Acceptance Criteria.

The same separation applies to:

- order and shipment information;
- delivery information;
- return information;
- refund information.

## 11. Data Integrity Rules

The following structural relationship applies:

```text
orders.order_id
    ↓
order_items.order_id
```

Each `order_items.order_id` must reference an existing `orders.order_id`.

The following shipment-status consistency rules apply:

```text
shipment_status = DELIVERED
    → delivered_at is present
```

```text
shipment_status = PROCESSING or SHIPPED
    → delivered_at is empty
```

Monetary fields must not contain negative values:

- `shipping_cost_paid >= 0`;
- `item_price >= 0`.

No shipping-price threshold, refund formula, legal, statutory, or routing rule is defined by the OMS Data Contract.

## 12. Policy-to-Data Coverage

The OMS contains only the verified operational values needed for order-specific processing within the frozen MVP.

### Shipping

Supported operational facts include:

- shipment status;
- order-specific estimated delivery date;
- confirmed delivery timestamp;
- tracking number when available;
- outbound carrier when available.

General shipping prices, delivery area, carrier-selection rules, and the standard delivery target remain in the Shipping Policy. The optional `carrier` field represents only the verified carrier recorded for a specific outbound shipment; it does not provide carrier-side tracking events or investigation data.

### Returns

Supported operational facts include:

- purchased-item identity;
- item context;
- current return status.

The return procedure, prepaid label / QR option, return-carrier instructions, packaging rules, and proof-of-dispatch guidance remain in the Returns Policy or the applicable human operational process. They are not modeled as OMS fields for the frozen MVP.

### Refunds

Supported operational facts include:

- item price;
- original outbound shipping cost actually paid;
- original payment method;
- current return status;
- current refund status.

Final refund calculations, value-reduction decisions, evidence sufficiency, authorization, and payment execution remain outside the OMS Data Contract.

The MVP OMS does not model the dates needed to calculate or determine individual statutory refund-deadline compliance, such as a withdrawal-declaration date or separate return/refund processing timestamps. If such verified dates are required for an individual case and are unavailable, the applicable missing-information handling is defined by the frozen Scenarios and Acceptance Criteria. Final legal assessment remains under human control.

## 13. Data Contract Boundaries

The OMS Data Contract defines:

- operational entities;
- operational fields;
- field types;
- required and optional data;
- allowed status values;
- structural consistency rules.

The OMS Data Contract does not define:

- customer intent classification;
- language handling;
- business scope;
- `ANSWER`, `CLARIFY`, `ESCALATE`, or `OUT_OF_SCOPE` decisions;
- policy rules;
- legal interpretation;
- statutory deadline calculation;
- human authorization rules;
- response-generation behavior;
- final refund calculations;
- return-label or QR-code generation;
- carrier-side tracking events or investigations.

Those concerns are defined in the appropriate product, knowledge-base, application, or human operational process.

## 14. Related Documentation

### Product

- [Product Discovery](../product/discovery.md)
- [Use Cases](../product/use_cases.csv)
- [Scenarios](../product/scenarios.csv)
- [Acceptance Criteria](../product/acceptance_criteria.csv)

### Knowledge Base

- `data/knowledge_base/shipping_policy.md`
- `data/knowledge_base/returns_policy.md`
- `data/knowledge_base/refund_policy.md`
