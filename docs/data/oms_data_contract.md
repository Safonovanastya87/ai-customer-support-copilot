# OMS Data Contract - MLP V14.6

## 1. Purpose

This document defines the **normalized OMS interface used by the MLP**.

It defines:

- the OMS business fields that may cross the OMS/MLP boundary;
- field types and empty-value rules;
- closed status values used by the current MLP;
- date/time and monetary formats;
- order/item integrity rules;
- the authorization lookup boundary;
- the distinction between a valid but incomplete business result (`INSUFFICIENT`) and a technically invalid OMS payload.

This contract does **not** define the full internal OMS schema. The real OMS may contain additional fields and statuses. Only the normalized subset defined here may be exposed to the Copilot path.

`use_cases.csv` remains the source of truth for which fields are **required, conditional, optional, or not permitted** for each Use Case. This contract defines how those fields are represented and validated.

---

## 2. General Contract Rules

### 2.1 Normalized payload

The OMS adapter must normalize the source response before it reaches the MLP.

The normalized payload:

- contains only fields permitted by the current Use Case;
- uses the types and values defined in this contract;
- contains no customer/private OMS fields that are not permitted by the current Use Case;
- must not contain raw OMS-specific structures that are outside this contract.

Unknown or additional raw OMS fields must be removed by the adapter and must not be passed to the Copilot path.

### 2.2 Missing values

The normalized MLP contract uses **field omission** to represent an unavailable value.

Rules:

- JSON `null` is not used for business fields in the normalized payload;
- an optional field with no value is omitted;
- a currently required or activated conditional field with no value is omitted and causes the OMS Result to be `INSUFFICIENT`;
- empty strings and whitespace-only strings are not valid substitutes for missing values.

Example:

```json
{
  "order_id": "12345",
  "shipment_status": "SHIPPED"
}
```

If `estimated_delivery_date` is currently required for this Use Case and is absent, the payload is structurally valid but the OMS Result is `INSUFFICIENT`.

### 2.3 Identifiers are opaque strings

`order_id` and `item_id` are strings, not numbers.

They:

- must be non-empty after trimming;
- must not be converted numerically;
- may contain leading zeroes;
- are compared as exact normalized strings.

---

## 3. Authorization Lookup Contract

Authorization is performed before OMS business retrieval as defined in Level 3.

### Input

```text
verified_sender_email
order_id
```

### Result

Exactly one business result:

```text
MATCH
NO_MATCH
```

Rules:

- authorization lookup returns no order/business payload;
- `MATCH` allows Level 3 to set `authorization = PASSED` for that exact `order_id`;
- `NO_MATCH` is a normal authorization outcome, not a technical error;
- timeout, transport failure, malformed response, or inability to execute the lookup is Technical Error Handling.

The data-retrieval operation may run only after `authorization = PASSED` for the same `order_id`.

---

## 4. Normalized Order Payload

The normalized business payload has this logical shape. Fields are included only when permitted by the current Use Case.

```json
{
  "order_id": "12345",
  "shipment_status": "SHIPPED",
  "estimated_delivery_date": "2026-10-08",
  "delivered_at": "2026-10-08T14:35:00+02:00",
  "tracking_number": "TRACK-123",
  "carrier": "Example Carrier",
  "shipping_cost_paid": 4.99,
  "payment_method": "PAYPAL",
  "order_items": [
    {
      "item_id": "0001",
      "product_name": "Pyjama",
      "item_price": 39.99,
      "return_status": "NOT_STARTED",
      "refund_status": "NOT_STARTED"
    }
  ]
}
```

The example shows the complete logical field set. A real Use Case receives only its permitted projection.

---

## 5. Field Definitions

| Field | Type | Empty / missing rule | Notes |
|---|---|---|---|
| `order_id` | string | no empty/null | Exact authorized order reference. Required whenever OMS business data is retrieved. |
| `shipment_status` | enum string | no empty/null when present | Closed MLP enum defined below. |
| `estimated_delivery_date` | date string | omitted when unavailable | Format `YYYY-MM-DD`. Interpreted as local calendar date for the MLP; Level 5 compares it with `current_local_date` in `Europe/Berlin`. |
| `delivered_at` | date-time string | omitted when unavailable | RFC 3339 / ISO 8601 date-time with `Z` or explicit UTC offset. |
| `tracking_number` | string | omitted when unavailable; no empty string | Tracking reference only. |
| `carrier` | string | omitted when unavailable; no empty string | Carrier display/name value only. |
| `shipping_cost_paid` | decimal number | omitted when unavailable | EUR, value `>= 0`, maximum two decimal places. |
| `payment_method` | string | omitted when unavailable; no empty string | Coarse payment-method name only. Must not contain card/account numbers, secrets, tokens, or authentication data. |
| `order_items` | array of objects | omitted when no item-level fields are permitted/available | When item-level required fields are active, absence or an empty collection produces `INSUFFICIENT`. |
| `order_items[].item_id` | string | required for every returned item record; no empty/null | Structural identifier for an included OMS item record. Unique within one order payload. Not required from the customer. A returned item record without a valid `item_id` is a contract/data-integrity violation. |
| `order_items[].product_name` | string | if required and unavailable, omit -> `INSUFFICIENT`; if optional and unavailable, omit; if present, no empty/null | Non-empty product display name. Missing required `product_name` is incomplete business data, not a structural item-record failure. |
| `order_items[].item_price` | decimal number | omitted when unavailable | EUR, value `>= 0`, maximum two decimal places. |
| `order_items[].return_status` | enum string | omitted where optional; no empty/null when present | Closed MLP enum defined below. |
| `order_items[].refund_status` | enum string | omitted where optional; no empty/null when present | Closed MLP enum defined below. |

---

## 6. Closed Status Enums

Enum values are uppercase and case-sensitive.

### 6.1 `shipment_status`

Allowed values:

```text
PROCESSING
SHIPPED
DELIVERED
```

Meaning in the MLP:

- `PROCESSING` - order/shipment is being prepared and is not recorded as shipped or delivered;
- `SHIPPED` - shipment has been handed over for delivery / is in transit and is not recorded as delivered;
- `DELIVERED` - OMS records the shipment as delivered.

The current MLP deliberately models no additional shipment states.

`CANCELLED`, `RETURNED`, `FAILED`, or any other raw OMS value is **outside the current MLP contract**. Such a value must not be silently mapped to one of the three allowed states. If an unsupported value reaches a required normalized field, it is a contract-validation failure handled through Technical Error Handling.

### 6.2 `return_status`

Allowed values:

```text
NOT_STARTED
INITIATED
DISPATCHED
RECEIVED
COMPLETED
CANCELLED
```

Meaning:

- `NOT_STARTED` - no return process is currently recorded for the item;
- `INITIATED` - a return has been created/registered but is not recorded as dispatched;
- `DISPATCHED` - the return is recorded as handed over/sent back;
- `RECEIVED` - the returned item is recorded as received by Anas Shop;
- `COMPLETED` - the return process is recorded as completed;
- `CANCELLED` - a previously recorded return process is recorded as cancelled.

### 6.3 `refund_status`

Allowed values:

```text
NOT_STARTED
PENDING
PROCESSING
COMPLETED
FAILED
CANCELLED
```

Meaning:

- `NOT_STARTED` - no refund process is currently recorded for the item;
- `PENDING` - refund is recorded as waiting for a required processing/release step;
- `PROCESSING` - refund execution is recorded as in progress;
- `COMPLETED` - OMS records the refund as completed;
- `FAILED` - OMS records the refund attempt/process as failed;
- `CANCELLED` - a previously recorded refund process is recorded as cancelled.

`NOT_STARTED` is used instead of an empty string or `null` when OMS explicitly knows that no return/refund process has started for the item.

---

## 7. Order and Item Integrity Rules

### 7.1 Order correlation

For an OMS retrieval executed for authorized `order_id = X`:

```text
response.order_id must equal X
```

A different `order_id` is a contract/data-integrity violation and must use Technical Error Handling. The mismatching payload must not be treated as customer data for the current Request.

### 7.2 Item collection

When `order_items` is returned:

- every item belongs to the root `order_id`;
- `item_id` values must be unique within the response;
- item order in the array has no business meaning;
- the adapter must not duplicate an item;
- where the Use Case requires item-level fields, the adapter returns the complete item collection for the authorized order, projected to the permitted fields.

Multiple items are valid and do not by themselves make the result `INSUFFICIENT`.

### 7.3 Included item records

Whenever an `order_items` collection is included, each included record must contain a valid `item_id` so Support can distinguish the records. `item_id` is a structural identity requirement for an included item record, not an ordinary missing business-field case. An included item record without a valid `item_id` is a contract/data-integrity violation and uses Technical Error Handling.

By contrast, business fields such as `product_name`, `item_price`, `return_status`, or `refund_status` follow their per-Use-Case requiredness in `docs/product/use_cases.csv`: if a required business field is unavailable it is omitted and the OMS Result becomes `INSUFFICIENT`; if it is optional it may be omitted without making the required path insufficient.

If all item-level business fields are optional for the current Use Case, the entire `order_items` collection may be omitted without making the required OMS path insufficient.

---

## 8. Conditional Field Rule

The current MLP has one OMS conditional rule:

```text
UC-SH-02:
estimated_delivery_date required if shipment_status in {PROCESSING, SHIPPED}
```

Therefore:

- `PROCESSING` + valid ETA -> required OMS data can be `SUFFICIENT`;
- `SHIPPED` + valid ETA -> required OMS data can be `SUFFICIENT`;
- `PROCESSING` or `SHIPPED` + ETA omitted -> `INSUFFICIENT`;
- `DELIVERED` -> ETA is not required.

A present ETA with invalid format is a payload-validation failure rather than normal `INSUFFICIENT`.

---

## 9. `SUFFICIENT` vs `INSUFFICIENT` vs Technical Error

### 9.1 `SUFFICIENT`

The normalized payload is valid and every field/collection currently required by `use_cases.csv`, including activated conditional fields, is available.

Optional fields may be absent.

### 9.2 `INSUFFICIENT`

The OMS operation completed normally and the normalized payload is structurally valid, but required business information is validly unavailable/incomplete.

Examples:

- required field is omitted;
- activated conditional ETA is omitted;
- required `order_items` collection is absent or empty;
- one or more required item-level **business fields** (for example required `product_name`) are omitted from an otherwise valid item record;
- OMS explicitly returns no business record after a successful authorized lookup in a valid no-data result.

`INSUFFICIENT` is a normal business retrieval result and proceeds through the global insufficient scenario.

### 9.3 Technical Error / contract violation

Use Technical Error Handling when required OMS processing cannot produce a valid normalized payload.

Examples:

- timeout, connection error, non-success technical response;
- malformed JSON / non-parseable payload;
- wrong JSON type;
- required string returned as `""` or whitespace only;
- JSON `null` in a returned business field;
- invalid date/date-time format;
- negative or invalid monetary value;
- unknown value in a **required** closed enum;
- `shipment_status = CANCELLED` in a required normalized field;
- returned `order_id` differs from the authorized/requested `order_id`;
- duplicate `item_id` values;
- an included `order_items` record has a missing, empty, null, or otherwise invalid `item_id`;
- non-array `order_items`;
- normalized payload contains prohibited/unpermitted private fields because projection/data minimization failed.

### 9.4 Invalid optional enrichment

If a validation problem is isolated to an **optional** field and the required path remains fully valid:

- omit the invalid optional field;
- record optional-source issue metadata;
- continue the normal required path;
- do not trigger Technical Escalation solely because of that optional enrichment.

Example:

For `UC-RF-02`, `refund_status` is optional. If a raw unsupported refund status cannot be normalized, that optional field may be omitted and logged while the required order/item data remains usable.

For `UC-RF-03`, `refund_status` is required. The same unsupported value is therefore a required payload-validation failure and uses Technical Error Handling.

---

## 10. Data Minimization and Security Boundary

The MLP must not receive OMS data beyond the current Use Case permission set.

In particular, this contract does not permit retrieval of customer profile data such as:

- customer name unless separately introduced by an approved contract change;
- postal address;
- full payment instrument details;
- bank/card account numbers;
- authentication data;
- internal notes unrelated to the current Use Case;
- unrelated orders.

The adapter is responsible for projection before the business payload reaches the Copilot path.

Authorization results and OMS business data are separate operations. A `NO_MATCH` authorization result never returns private order data.

---

## 11. Current MLP Use-Case Relationship

The following Use Cases currently use OMS:

```text
UC-OS-01
UC-SH-02
UC-SH-03
UC-RT-02
UC-RT-03
UC-RT-04
UC-RF-02
UC-RF-03
UC-RF-04
```

Field requiredness and permission are defined in `docs/product/use_cases.csv`.

Knowledge-only Use Cases do not call OMS:

```text
UC-SH-01
UC-RT-01
UC-RF-01
```

---

## 12. Change Rule

A new OMS field, status value, relationship rule, or data type is not automatically available to the MLP.

Changing this contract requires checking at least:

- `product/use_cases.csv` field permissions and requiredness;
- `product/scenarios.csv` scenario completeness/mutual exclusivity where the new value can affect scenario matching;
- Level 4 retrieval/validation behavior;
- Technical Error Handling boundary;
- applicable Policy scope where business rules depend on the new data.

No raw OMS value may be silently coerced merely to make an existing scenario match.
