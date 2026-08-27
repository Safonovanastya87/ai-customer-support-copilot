# NordShop Customer Support Copilot — Solution Architecture

## 1. Purpose

This document defines the high-level solution architecture for the NordShop Customer Support Copilot MVP.

It translates the frozen product and requirements baseline into a technical processing model without introducing new business functionality, business rules, runtime information sources, or business actions.

The architecture is intentionally hybrid: AI is used where natural-language understanding or generation is required, while deterministic application logic is preferred for explicit rules, routing, validation, and structured operational processing.

---

## 2. Architecture Principles

The MVP follows these principles:

- use AI for natural-language understanding and response generation;
- use deterministic application logic for explicit business rules and structured decisions where feasible;
- use only approved runtime information sources;
- keep customer-reported information distinguishable from authoritative OMS information;
- retrieve approved business knowledge instead of relying on model memory;
- minimize unnecessary model calls, tokens, latency, and cost;
- validate runtime results against the frozen Copilot Output Contract;
- keep technical failures separate from business Scenarios and Actions;
- preserve the human-in-the-loop operating model;
- do not autonomously execute restricted operational or financial actions.

---

## 3. System Context

### 3.1 User

The Copilot is used by an authorized NordShop support employee.

The Copilot is not a public customer-facing chatbot and does not autonomously send customer communications.

### 3.2 Runtime Information Sources

The MVP uses only the following approved runtime information sources:

1. **Customer Request** — the request text and customer-provided information contained in the current request.
2. **Approved Knowledge Base** — the approved Shipping, Returns, and Refund policies.
3. **OMS** — verified operational order and item information defined by the OMS Data Contract.

### 3.3 High-Level Boundary

```text
Customer Request
        |
        v
+-----------------------------+
| NordShop Support Copilot    |
|                             |
| Analyze                     |
| Retrieve                    |
| Decide                      |
| Draft                       |
| Validate                    |
+-------------+---------------+
              |
              v
       Copilot Result
              |
              v
      Support Employee
              |
              v
   Human business process
```

Any business execution performed after review by the support employee is outside the Copilot MVP boundary.

---

## 4. Main Components

The MVP contains the following logical components.

### 4.1 Request Processing

Receives the Customer Request and initializes the processing context for one request.

Responsibilities include:

- accepting the current request;
- passing the request to language and intent analysis;
- maintaining request-level processing state;
- keeping information from unrelated requests isolated.

### 4.2 Language, Intent, and Use Case Analysis

Uses AI-assisted closed-set classification against the frozen catalog of 13 MVP Use Cases.

The classifier distinguishes:

- supported request with a reliably identified Use Case;
- ambiguous intent;
- clearly unsupported request;
- unsupported language.

The model is not allowed to invent new Use Case IDs.

Deterministic application logic validates the classification result and maps global classification outcomes to the corresponding frozen Scenario and Action:

- ambiguous intent → `SC-G01` → `CLARIFY`;
- clearly unsupported request → `SC-G02` → `OUT_OF_SCOPE`;
- unsupported language → `SC-G03` → `CLARIFY`.

For `SC-G03`, `use_case_id` handling follows the frozen Copilot Output Contract: it may remain `null` if processing stops before a supported Use Case is reliably identified, or retain the supported Use Case if it had already been identified reliably.

For supported requests, the identified Use Case continues to downstream processing.

### 4.3 Source Selection / Retrieval Routing

Source selection is deterministic and driven by the identified Use Case.

The application determines whether the request requires:

- Approved Knowledge Base information;
- OMS information;
- both;
- neither for the applicable handling branch.

Knowledge retrieval is restricted to the applicable approved policy domain.

OMS retrieval is performed only for Use Cases that require order-specific operational facts and only after the required customer reference can be resolved.

### 4.4 Reference Resolution

For Use Cases requiring OMS information, the application resolves the required order or item reference before operational retrieval.

The MVP uses references already defined by the OMS Data Contract, including:

- `order_id`;
- `item_id` where item-level identification is required.

Missing, ambiguous, or unmatched required references follow:

`SC-G04` → `CLARIFY`.

Reference resolution in this MVP is not customer identity management. The architecture does not introduce customer account matching, `customer_id`, authentication, or ownership verification flows that are not part of the frozen requirements.

### 4.5 Knowledge Retrieval

Approved business knowledge is retrieved from the Knowledge Base for the current Use Case.

The MVP will use a lightweight RAG-based implementation as a deliberate technical learning and validation objective.

Conceptually:

```text
Approved Policy Documents
        |
        v
Document Loading
        |
        v
Chunking
        |
        v
Embeddings
        |
        v
Vector Store
        |
        v
Similarity Retrieval
        |
        v
Relevant Approved Knowledge
```

The use of RAG is a technical implementation choice for the MVP and does not change the product requirements or add a new runtime information source.

The detailed RAG design, including chunking, embeddings, retrieval strategy, and evaluation, is defined later in the AI / RAG Design stage.

### 4.6 OMS Access Layer

OMS information is accessed through a dedicated abstraction rather than being embedded directly in business decision logic.

Conceptually:

```text
Business Processing
        |
        v
OMS Access Layer
        |
        v
OMS Data Source
```

For the learning MVP, the operational data source is represented by controlled seed data based on the frozen OMS Data Contract.

The architecture keeps OMS access separate so that the underlying implementation can later be replaced by another compatible OMS access mechanism, such as an OMS API, without changing the business decision model or introducing a new runtime information source.

If a reference is successfully resolved but required authoritative information is unavailable, the frozen missing-information handling applies:

`SC-G05` → `ESCALATE`.

Missing optional information does not trigger `SC-G05` when sufficient approved or verified information remains available to answer the request.

A technical OMS access failure is not `SC-G05`; it is a technical failure.

### 4.7 Semantic Fact Extraction

AI-based processing may be used to interpret relevant meaning contained in free-form customer language, for example:

- the request intent;
- a customer-reported operational fact;
- whether the customer is asking for information, describing a situation, making a withdrawal declaration, or requesting a human-controlled action.

The AI component produces structured semantic information for downstream processing.

It does not independently invent business rules or unrestricted actions.

### 4.8 Scenario and Business Decision Engine

The Scenario and Business Decision Engine selects the applicable frozen Scenario and Action using the available structured inputs.

Inputs may include:

- identified Use Case;
- classification outcome;
- customer semantic facts;
- reference-resolution status;
- retrieved approved policy knowledge;
- verified OMS facts;
- runtime context required by an existing rule.

AI may assist in interpreting customer language, while deterministic application logic is preferred for explicit business rules and structured conditions.

Global Scenarios are applied at defined processing checkpoints rather than through a separate parallel classifier.

The following frozen distinctions are preserved:

- a material conflict between customer-reported operational information and corresponding verified OMS information follows `SC-G06` → `ESCALATE`;
- `UC-SH-03` remains a dedicated Use Case and uses `SC-SH-03` for the Delivered-but-Not-Received case rather than being reduced to the generic `SC-G06` conflict branch;
- a request to perform, register, initiate, approve, modify, or execute a human-controlled withdrawal-, return-, or refund-related action under `UC-RT-04` or `UC-RF-04` follows `SC-G07` → `ESCALATE`;
- an actual withdrawal declaration contained in the customer request under `UC-RT-04` remains the dedicated `SC-RT-04` branch and is not treated as the `SC-G07` action-request branch.

Exactly one applied Scenario and one allowed Action are produced for each normally processed request.

The allowed Actions remain exactly:

- `ANSWER`;
- `CLARIFY`;
- `ESCALATE`;
- `OUT_OF_SCOPE`.

### 4.9 Response Generation

Response generation is an AI-based language-generation step performed only after the applicable Scenario and Action have been determined.

The model receives only the context required for the current response, which may include:

- Customer Request;
- identified Use Case;
- applied Scenario;
- selected Action;
- relevant approved knowledge;
- relevant verified OMS facts;
- response-generation instructions.

Response generation must not change the selected Use Case, Scenario, or Action.

The generated draft must not introduce unsupported:

- business facts;
- operational facts;
- actions;
- promises;
- remedies;
- completion claims.

For unsupported-language handling, the frozen requirement applies: the clarification is produced in German and asks the customer to submit the request in German or English.

### 4.10 Output Assembly

The final business result is assembled by the application from validated processing outputs rather than being freely generated by the language model.

The result follows the frozen Copilot Output Contract and contains:

- `use_case_id`;
- `scenario_id`;
- `action`;
- `supporting_information`;
- `response_draft`.

Responsibility is separated conceptually as follows:

```text
use_case_id            <- classification / application logic
scenario_id            <- decision engine
action                 <- decision engine
supporting_information <- application from approved runtime sources
response_draft         <- AI response generation where applicable
```

Supporting information keeps Customer Request, Knowledge Base, and OMS information distinguishable according to the Output Contract.

### 4.11 Output Validation

Every final Copilot result is validated before it is presented to the support employee.

Validation has two levels.

#### Schema Validation

Checks that:

- required fields are present;
- field types are valid;
- nullable fields follow the contract;
- enum values are valid;
- collections have the required structure.

#### Business Consistency Validation

Checks relevant frozen relationships, such as:

- Use Case IDs are valid where present;
- Scenario IDs are valid;
- Action values are from the frozen set;
- Scenario / Action combinations are consistent with the frozen requirements;
- applicable Use Case / Scenario relationships are valid.

Application-side validation remains required even if structured or schema-constrained LLM output is used later.

---

## 5. End-to-End Request Processing Flow

```text
Customer Request
        |
        v
Language / Intent / Use Case Analysis
        |
        +--> Ambiguous intent ---------> SC-G01 / CLARIFY
        |
        +--> Out of scope -------------> SC-G02 / OUT_OF_SCOPE
        |
        +--> Unsupported language -----> SC-G03 / CLARIFY
        |
        v
Supported Use Case
        |
        v
Deterministic Source Selection
        |
        v
Reference required?
        |
        +--> Missing / ambiguous / unmatched
        |        -> SC-G04 / CLARIFY
        |
        v
Reference resolved / not required
        |
        +-----------------------+
        |                       |
        v                       v
RAG Knowledge Retrieval     OMS Access
        |                       |
        +-----------+-----------+
                    |
                    v
       Structured / Grounded Facts
                    |
                    +--> Required authoritative information unavailable
                    |        -> SC-G05 / ESCALATE
                    |
                    +--> Material Customer-vs-OMS conflict
                    |        -> SC-G06 / ESCALATE
                    |           (UC-SH-03 keeps its dedicated SC-SH-03 branch)
                    |
                    +--> Human-controlled action request
                    |        -> SC-G07 / ESCALATE
                    |           (UC-RT-04 / UC-RF-04 action-request branch)
                    |
                    +--> Actual withdrawal declaration
                    |        -> SC-RT-04 / ESCALATE
                    |
                    v
       Scenario / Business Decision
                    |
                    v
           scenario_id + action
                    |
                    v
          AI Response Generation
                    |
                    v
             Output Assembly
                    |
                    v
      Schema + Business Validation
                    |
                    v
             Copilot Result
                    |
                    v
           Support Employee
```

Missing optional information does not by itself trigger `SC-G05` when sufficient verified or approved information remains available.

Technical error handling, observability, request isolation, and data minimization apply across the processing pipeline.

---

## 6. AI and Deterministic Responsibility Split

The architecture intentionally separates tasks according to their nature.

### AI-Oriented Responsibilities

AI is used primarily for:

- understanding natural-language requests;
- closed-set Use Case classification;
- interpreting relevant semantic facts in customer language;
- generating natural-language response drafts;
- later, embedding-based knowledge retrieval as part of the lightweight RAG implementation.

### Deterministic Responsibilities

Application logic is preferred for:

- validating classification outputs;
- source routing by Use Case;
- reference lookup and resolution;
- OMS retrieval;
- explicit structured business conditions;
- Scenario and Action constraints;
- assembling the final business result;
- schema validation;
- business-consistency validation;
- technical error handling.

This hybrid approach improves reproducibility, testability, observability, cost efficiency, and control.

---

## 7. Human-in-the-Loop Boundary

The Copilot operates as an internal support assistant.

It produces a validated business result and, where appropriate, a response draft for review by an authorized support employee.

The employee remains responsible for:

- reviewing the result;
- reviewing supporting information;
- reviewing the response draft and deciding whether and how it is used in the human support workflow;
- performing any required human-controlled operational or financial action;
- sending or otherwise completing customer communication through the relevant human workflow.

The Copilot does not autonomously:

- send customer communications;
- initiate or approve refunds;
- register or execute restricted return or withdrawal actions;
- perform financial approvals;
- claim that a human investigation or restricted action has been completed when it has not been executed by the responsible workflow.

---

## 8. Technical Error Handling

Technical failures are separate from business Scenarios and Actions.

Examples include:

- AI service timeout or invalid model response;
- RAG retrieval failure;
- OMS access failure;
- unexpected processing exception;
- response-generation failure;
- output-validation failure.

A technical failure must not introduce new business Action values such as `SYSTEM_ERROR`, `FAILED`, or `RETRY` into the Copilot Output Contract.

Technical failures are recorded and handled by the application as technical processing failures and are measured separately from expected business outcomes such as `CLARIFY`, `ESCALATE`, or `OUT_OF_SCOPE`.

---

## 9. Observability

The solution must provide sufficient observability to understand major processing outcomes and diagnose failures without requiring model chain-of-thought.

Relevant observable information may include, where needed and permitted:

- request identifier;
- detected language;
- classification status;
- selected Use Case;
- selected runtime sources;
- reference-resolution result;
- retrieved knowledge identifiers or chunks;
- applied Scenario;
- selected Action;
- output-validation result;
- technical processing status;
- technical error category;
- processing timings.

Observability supports troubleshooting, quality evaluation, and defined product metrics.

The exact logging schema, monitoring technology, retention rules, and infrastructure are implementation concerns and are not defined by this architecture document.

---

## 10. Data Protection and Isolation

The architecture follows the frozen Non-Functional Requirements for customer personal data, request isolation, data minimization, and internal-use boundaries.

Customer content and operational information must be processed only to the extent required for supported request handling and must not be unnecessarily duplicated across technical artifacts.

Information from one processed customer request must not appear in the result of an unrelated request.

Observability and evaluation data must follow the same data-minimization principle.

---

## 11. Architecture Boundaries

This high-level architecture does not define:

- a specific LLM provider or model;
- prompt wording;
- embedding model;
- vector database technology;
- RAG framework;
- exact chunk size or overlap;
- API framework;
- database technology;
- deployment platform;
- authentication implementation;
- monitoring platform;
- retry strategy;
- UI technology;
- autonomous business-action integrations.

These decisions belong to later Solution and Validation Design activities or Implementation.

The architecture also does not introduce new:

- business rules;
- Use Cases;
- Scenarios;
- Actions;
- OMS fields;
- runtime information sources.

---

## 12. Related Documentation

This architecture is based on the frozen project documentation:

- `docs/product/discovery.md`
- `docs/product/success_metrics.md`
- `docs/product/use_cases.csv`
- `docs/product/scenarios.csv`
- `docs/product/acceptance_criteria.csv`
- `docs/product/non_functional_requirements.md`
- `docs/data/oms_data_contract.md`
- `docs/technical/copilot_output_contract.md`
- `data/knowledge_base/shipping_policy.md`
- `data/knowledge_base/returns_policy.md`
- `data/knowledge_base/refund_policy.md`

The architecture must remain consistent with these sources throughout later design and implementation.
