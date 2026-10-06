# Level 4 - Deterministic Data Retrieval

**Baseline:** Architecture V14.6

## Input

- Request
- saved `use_case_id`
- Authorization Context, where applicable

Source and field requirements are read directly from the current Use Case in `use_cases.csv`.

Field types, enum values, empty-value semantics, order/item integrity, and the `SUFFICIENT` / `INSUFFICIENT` / invalid-payload boundary are defined in `docs/data/oms_data_contract.md`.

## Source and Field Rules

For the current MLP:

- any Shipping/Returns/Refund Policy listed in `Data_Sources` is REQUIRED;
- `OMS_Required_Fields` are required for a sufficient OMS result;
- `OMS_Conditional_Fields` become required only when their deterministic condition is true;
- `OMS_Optional_Fields` may enrich the handoff, but their absence does not make the required path insufficient;
- `NONE` means that the category is not used;
- fields not listed for the Use Case are outside the automated permitted retrieval contract.

Conditions in `OMS_Conditional_Fields` must be deterministic and documented in the Use Case definition. They are not decided ad hoc by the LLM.

## Knowledge Retrieval

For every Policy listed in the current Use Case `Data_Sources`:

- retrieve the approved Policy source;
- available and sufficient -> `knowledge_result.status = SUFFICIENT`;
- missing/insufficient/conflicting required Knowledge -> `knowledge_result.status = INSUFFICIENT`;
- technical inability to retrieve/validate the required Policy -> **Technical Error Handling**.

A Policy may only be used for a Use Case already admitted by the Level 2 Policy Scope Gate.

`UC-RF-03` is status-only and does not retrieve or apply the Refund Policy.

## OMS Retrieval

OMS retrieval is allowed only when Level 3 produced:

```text
 authorization = PASSED
```

for the same authorized `order_id`.

Rules:

- do not repeat authorization in Level 4;
- retrieve only the fields listed by the current Use Case;
- optional fields may be omitted if unavailable;
- a technical failure limited to optional enrichment does not trigger Technical Escalation while all required processing remains executable.

### Order-item collection rule

When the current Use Case permits item-level OMS fields:

- retrieve the permitted fields for all `order_items` belonging to the authorized `order_id`;
- each returned item keeps its OMS `item_id` as a record identifier;
- no customer-provided `item_id` is required;
- more than one returned item is a valid result and does not by itself make the OMS Result `INSUFFICIENT`;
- customer wording about a particular product may be preserved for Support context, but the MLP does not require unique automated item selection before handoff.

### Conditional field evaluation

Retrieve unconditional required fields first, then evaluate `OMS_Conditional_Fields`.

For `UC-SH-02`:

```text
estimated_delivery_date|required_if:shipment_status in {PROCESSING,SHIPPED}
```

If the condition is true and ETA is absent -> `oms_result.status = INSUFFICIENT`.

If `shipment_status = DELIVERED`, ETA is not required.

### OMS Result

- `SUFFICIENT` - all currently required OMS fields/record collections are present and valid.
- `INSUFFICIENT` - one or more currently required business fields/record collections are validly absent/incomplete.

A technically invalid OMS payload is handled through **Technical Error Handling**, not as normal business `INSUFFICIENT`.

## Retrieval Result

Contains, as applicable:

- `request_id`;
- `knowledge_result`;
- `oms_result`;
- optional enrichment already available for the handoff;
- optional-source issue metadata where optional enrichment was unavailable or unusable.

Each result retains relevant source/reference information and only permitted business fields.

Then go to **Level 5**.
