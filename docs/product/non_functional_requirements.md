# Non-Functional Requirements

## 1. Purpose

This document defines the non-functional requirements for the NordShop Customer Support Copilot MVP.

Functional behavior is defined in the frozen:

- Use Cases;
- Scenarios;
- Acceptance Criteria;
- approved Knowledge Base policies;
- OMS Data Contract.

This document does not redefine business rules, routing conditions, or operational data structures.

## 2. AI Reliability and Groundedness

### NFR-REL-01 — Grounded factual output

Factual, operational, and business-policy statements produced by the Copilot must be grounded in information available from the approved runtime sources:

- Customer Request;
- Approved Knowledge Base;
- Order Management System.

The Copilot must not present unsupported assumptions as facts.

### NFR-REL-02 — No invented information

The Copilot must not invent unavailable:

- business rules;
- OMS values;
- dates;
- statuses;
- tracking information;
- carrier information;
- refund amounts;
- business decisions;
- completed actions.

Missing or insufficient information must be handled according to the applicable frozen Scenarios and Acceptance Criteria.

### NFR-REL-03 — Information-source distinction

Customer-reported information and verified OMS information must remain distinguishable in the Copilot result.

The Copilot must not:

- silently replace verified OMS information with customer-reported information;
- present customer-reported operational information as verified OMS fact;
- present generated assumptions as approved Knowledge Base information.

### NFR-REL-04 — Structured output conformance

Every successfully produced Copilot result must conform to the approved Copilot Output Contract.

The implementation must not introduce additional action values or incompatible output structures without an approved contract change.

## 3. Human Oversight and Action Safety

### NFR-HITL-01 — Human review

The Copilot must operate as an internal decision-support system.

A support employee remains responsible for reviewing the Copilot result before any customer-facing response is communicated.

### NFR-HITL-02 — No autonomous restricted actions

The Copilot must not autonomously execute business or financial actions that are defined as human-controlled in the frozen product requirements and approved policies.

### NFR-HITL-03 — No false action completion

The Copilot must not claim that a restricted business action has been:

- performed;
- registered;
- initiated;
- approved;
- modified;
- executed;
- completed

unless the authoritative operational process confirms that the action occurred.

## 4. Data Protection and Isolation

### NFR-DATA-01 — Request isolation

Information provided or retrieved for one processed customer request must not appear in the result of an unrelated request.

### NFR-DATA-02 — Data minimization

Application logging, telemetry, and evaluation data must be limited to information required for:

- system operation;
- troubleshooting;
- quality evaluation;
- defined product metrics.

Customer content and operational information must not be duplicated unnecessarily across technical artifacts.

### NFR-DATA-03 — Internal-use boundary

The Copilot and the operational information processed by it are intended for authorized NordShop support workflows.

The Copilot must not operate as a public customer-facing system.

## 5. Technical Reliability

### NFR-TECH-01 — Technical failures remain distinguishable

Technical failures that prevent reliable access to required capabilities must remain distinguishable from valid business-routing outcomes.

Expected outcomes such as:

- `CLARIFY`;
- `ESCALATE`;
- `OUT_OF_SCOPE`

must not automatically be classified as technical failures when they result from the applicable product or business condition.

### NFR-TECH-02 — No fabricated technical fallback

If a required technical dependency is unavailable or fails, the Copilot must not replace unavailable OMS or Knowledge Base information with generated assumptions.

Detailed application-level technical error handling is defined during solution design.

### NFR-TECH-03 — Valid successful output

A request reported by the application as successfully processed must return a structurally valid result conforming to the Copilot Output Contract.

## 6. Performance and Operational Measurement

### NFR-PERF-01 — Response latency measurement

Copilot response latency must be measurable.

No fixed MVP response-latency threshold is defined during the requirements phase.

Numerical targets are established after baseline measurement and pilot observation.

### NFR-PERF-02 — Technical error measurement

Technical processing failures must be measurable independently from expected business-routing outcomes.

### NFR-PERF-03 — Usage and cost measurement

The implementation must provide sufficient operational measurement to support the applicable frozen Success Metrics, including where relevant:

- response latency;
- technical error rate;
- AI suggestion utilization;
- technical cost per AI request.

The detailed instrumentation design is defined during solution design.

## 7. Observability and Evaluation

### NFR-OBS-01 — Result traceability

For evaluation and troubleshooting, a Copilot result must provide sufficient structured information to determine:

- the selected handling action;
- the applicable Scenario;
- the supported Use Case when one has been reliably identified.

This requirement does not require exposure of private model reasoning or chain-of-thought.

### NFR-OBS-02 — Quality evaluation support

The implementation must support evaluation against the frozen Success Metrics and Acceptance Criteria.

Evaluation must not depend on undocumented business rules.

### NFR-OBS-03 — Business and technical outcomes remain separate

Operational reporting must allow valid business-routing outcomes to be distinguished from technical processing failures.

## 8. Performance and Quality Targets

Exact numerical targets for:

- response latency;
- technical error rate;
- cost;
- adoption;
- quality;
- customer impact

are not defined in this requirements phase.

Where numerical targets are required, they are established after baseline measurement and pilot observation in accordance with the frozen Success Metrics.

## 9. Requirement Boundaries

These Non-Functional Requirements do not define:

- business-policy rules;
- customer-intent classification;
- routing conditions;
- OMS entities or fields;
- Copilot output-field structure;
- final prompt design;
- model or LLM provider selection;
- retrieval architecture;
- deployment architecture;
- detailed access-control implementation;
- monitoring technology;
- numerical KPI targets that have not yet been established.

Those concerns belong to the applicable product, data, technical, solution-design, implementation, or operational documentation.

## 10. Related Documentation

### Product

- [Product Discovery](discovery.md)
- [Success Metrics](success_metrics.md)
- [Use Cases](use_cases.csv)
- [Scenarios](scenarios.csv)
- [Acceptance Criteria](acceptance_criteria.csv)

### Data

- [OMS Data Contract](../data/oms_data_contract.md)

### Technical

- [Copilot Output Contract](../technical/copilot_output_contract.md)

### Knowledge Base

- `data/knowledge_base/shipping_policy.md`
- `data/knowledge_base/returns_policy.md`
- `data/knowledge_base/refund_policy.md`