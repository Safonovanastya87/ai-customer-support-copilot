# Semantic / Business Logic Error Handling - MLP V14.6

Used when the system is technically functioning but the documented business rules cannot produce one valid permitted outcome.

## Examples

- 0 Level 5 scenarios match;
- more than 1 Level 5 scenario matches;
- scenario resolves to a disallowed action or action/reason pair;
- required Use Case definition is missing, internally inconsistent, or semantically invalid;
- identification rules violate the Level 2 outcome contract;
- a Policy-based Use Case contradicts its declared Policy scope;
- required customer-input or OMS field rules are contradictory or invalid;
- a Use Case refers to a Policy/source that is not permitted for that Use Case;
- `Restricted_Action_Safety = YES` has no valid `Restricted_Action_Decision_Reason`;
- contradictory deterministic rules exist for the same valid input.

## Pre-Activation Validation

Validate:

- `use_cases.csv` structure and unique IDs;
- `scenarios.csv` structure, references, completeness, and mutual exclusivity;
- Use Case scope against the applicable Policy;
- data-source and required-input rules;
- permitted OMS field lists and conditional syntax against `docs/data/oms_data_contract.md`;
- restricted-action safety reason;
- allowed action/reason pairs and closure reasons from Supporting Rules;
- `Support_Draft_Required` values.

## Runtime Semantic Fallback

- stop automated business decision;
- do not arbitrarily choose a Use Case, scenario, or action;
- preserve Request, `message_refs`, accepted business-message references, current triggering message, attachments, already retrieved permitted data, and approved Knowledge references;
- record the semantic issue type and relevant Use Case/scenario/rule reference;
- build Decision Result:
  - `action = HANDOFF_TO_SUPPORT`
  - `decision_reason = BUSINESS_LOGIC_CONFIGURATION_ERROR`
  - `support_draft_required = false`
- execute handoff through Level 6.

Do not technically retry a deterministic semantic defect with unchanged input and unchanged rule set.

If the fallback handoff itself fails technically -> Technical Error Handling.
