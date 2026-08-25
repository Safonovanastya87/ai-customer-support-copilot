# Product Success Metrics

The NordShop Customer Support Copilot is evaluated across four metric groups:

1. Business & Customer Impact
2. Agent Adoption & Productivity
3. AI Quality & Safety
4. Technical & Operational Performance

Exact target values are not defined during the discovery phase.

Targets should be established after measuring the baseline and collecting pilot data.

Operational definitions, calculation rules, denominators, and measurement instrumentation should be fixed before pilot evaluation so that baseline and pilot results are comparable.

## 1. Business & Customer Impact

### 1. Average Handling Time (AHT)

Average time required by a support employee to handle one customer request.

**Purpose**

Measure whether the Copilot reduces the time spent understanding requests, retrieving relevant information, determining the appropriate handling path, and preparing responses.

**Comparison**

Baseline without Copilot vs. pilot with Copilot.

### 2. Requests per Agent Hour

Average number of customer requests handled by one support employee per hour.

**Purpose**

Measure whether support productivity increases when using the Copilot.

### 3. First Contact Resolution (FCR)

Percentage of customer requests resolved without requiring an additional customer interaction.

**Purpose**

Ensure that reduced handling time does not come at the cost of incomplete or ineffective handling.

Correctly escalated or out-of-scope requests should be evaluated according to their intended workflow rather than automatically treated as Copilot quality failures solely because the customer issue is not resolved by the Copilot-assisted interaction.

### 4. Customer Satisfaction (CSAT)

Customer feedback collected after a support interaction.

**Purpose**

Measure the customer-facing impact of the Copilot-assisted support process.

## 2. Agent Adoption & Productivity

### 5. AI Suggestion Utilization

Measures how support employees use AI-generated response drafts when a draft is produced.

Possible outcomes include:

- accepted without changes;
- accepted with changes;
- rejected.

**Purpose**

Measure whether AI-generated suggestions are practically useful to support employees.

The metric may be reported as acceptance rate, unchanged acceptance rate, edited acceptance rate, and rejection rate.

### 6. AI Response Edit Level

Measures the extent to which support employees modify accepted AI-generated drafts.

Possible levels include:

- no edit;
- minor edit;
- major edit;
- complete rewrite.

**Purpose**

Identify cases in which generated responses require substantial human correction.

## 3. AI Quality & Safety

### 7. Answer Correctness / Policy Compliance

Measures whether the Copilot result is consistent with the applicable approved policy information, verified OMS information, and the defined product requirements.

**Purpose**

Measure whether generated results are factually and operationally correct within the supported MVP scope.

Evaluation should be based on the frozen Use Cases, Scenarios, Acceptance Criteria, approved Knowledge Base policies, and applicable verified OMS information rather than on additional undocumented rules.

### 8. Groundedness

Measures whether factual, operational, and policy claims in the generated result are supported by information actually available to the Copilot.

Relevant support may come from:

- Customer Request;
- Approved Knowledge Base;
- Order Management System.

Customer-reported information must remain distinguishable from verified system information.

**Purpose**

Detect hallucinated, inferred, or unsupported statements.

### 9. Response Relevance

Measures whether the generated result addresses the customer's identified request.

**Purpose**

Prevent responses that may be factually correct but do not address the actual customer need.

### 10. Response Completeness

Measures whether the generated result contains the information required to handle the identified request correctly.

Completeness does not require unavailable, unsupported, or human-only information to be invented or supplied.

**Purpose**

Detect responses that omit information required for correct handling.

### 11. Correct Action / Routing

Measures whether the Copilot assigns the action expected by the applicable frozen Scenario and Acceptance Criteria.

Supported actions are:

- `ANSWER`;
- `CLARIFY`;
- `ESCALATE`;
- `OUT_OF_SCOPE`.

**Purpose**

Measure whether the Copilot chooses the correct handling path for supported, ambiguous, human-handled, and unsupported requests.

Examples of routing errors include:

- assigning `ANSWER` when clarification or escalation is required;
- assigning `CLARIFY` when sufficient information is already available;
- assigning `ESCALATE` when the request can be answered reliably;
- assigning `OUT_OF_SCOPE` to a supported request;
- processing an unsupported request as though it were supported.

### 12. Supporting Information Correctness

Measures whether supporting information presented to the support employee:

- is relevant to the generated result;
- supports the generated claims;
- is consistent with the correct approved policy or verified OMS information where applicable;
- keeps customer-reported information distinguishable from verified operational information.

**Purpose**

Ensure that the supporting information provided for human review is relevant, grounded, and trustworthy.

This metric does not require the MVP to expose technical retrieval metadata or implement a separate source-citation feature.

## 4. Technical & Operational Performance

### 13. Response Latency

Time between submitting a customer request and receiving the Copilot result.

**Purpose**

Ensure that the system is fast enough to support the intended productivity improvement.

### 14. System Error Rate

Percentage of requests affected by technical failures that prevent normal processing or reliable access to required system capabilities.

Examples include:

- LLM API failure;
- OMS technical access failure;
- Knowledge Base retrieval failure;
- application error;
- database error.

Expected business outcomes such as `CLARIFY`, `ESCALATE`, or `OUT_OF_SCOPE` are not technical system errors when they are produced because the applicable business or product condition requires that outcome.

A technical failure remains a technical error for this metric even if the product handles the failure safely, for example by returning or routing the case to `ESCALATE`.

Missing or insufficient business data without a technical malfunction is evaluated through the applicable product behavior and is not automatically counted as a technical system error.

**Purpose**

Measure the technical reliability of the Copilot separately from expected business-routing outcomes.

### 15. Cost per AI Request

Average technical cost of processing one AI-assisted customer request.

Possible components include:

- LLM input tokens;
- LLM output tokens;
- embedding usage;
- retrieval infrastructure;
- application infrastructure.

**Purpose**

Evaluate whether the solution remains economically viable as usage grows.

## 5. Primary MVP Metrics

The primary candidates for evaluating MVP success are:

- Average Handling Time;
- Requests per Agent Hour;
- First Contact Resolution;
- Customer Satisfaction;
- AI Suggestion Utilization;
- Answer Correctness / Policy Compliance;
- Correct Action / Routing;
- Supporting Information Correctness.

The remaining metrics provide diagnostic, quality, safety, and operational context.

Final KPI targets should be defined only after baseline measurement and pilot observation.
