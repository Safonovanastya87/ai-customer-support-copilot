# Product Success Metrics

The metrics are divided into four groups:

1. Business & Customer Impact
2. Agent Adoption & Productivity
3. AI Quality & Safety
4. Technical & Operational Metrics


## 1. Business & Customer Impact

### 1. Average Handling Time (AHT)

Average time required by a support agent to handle one customer request.

Purpose:
Measure whether the Copilot reduces the amount of time agents spend
searching for information and preparing responses.

Comparison:
Baseline without Copilot vs. pilot with Copilot.


### 2. Requests per Agent Hour

Average number of customer requests handled by one support agent per hour.

Purpose:
Measure whether agent productivity increases when using the Copilot.


### 3. First Contact Resolution (FCR)

Percentage of customer requests resolved without requiring an additional
customer interaction.

Purpose:
Ensure that faster responses do not reduce the actual quality
of customer support.


### 4. Customer Satisfaction (CSAT)

Customer feedback collected after a support interaction.

Example:

"How satisfied are you with the resolution of your request?"

Purpose:
Measure the customer-facing impact of the Copilot-assisted support process.


## 2. Agent Adoption & Productivity

### 5. AI Suggestion Acceptance Rate

Percentage of AI-generated responses that agents use.

Possible outcomes:

- accepted without changes
- accepted with changes
- rejected

Purpose:
Measure whether AI-generated suggestions are practically useful
to support employees.


### 6. AI Response Edit Rate

Measure how often and how extensively agents modify AI-generated responses.

Possible measurements:

- no edit
- minor edit
- major edit
- complete rewrite

Purpose:
Identify situations where AI responses require substantial human correction.


### 7. AI Suggestion Rejection Rate

Percentage of generated suggestions that agents decide not to use.

Purpose:
Identify low-quality or inappropriate AI responses and problematic use cases.


## 3. AI Quality & Safety

### 8. Answer Correctness / Policy Compliance

Measures whether the generated answer:

- follows company policies;
- uses correct order information;
- does not contradict business rules;
- does not invent facts.

Purpose:
Ensure that an answer is factually and operationally correct.


### 9. Groundedness

Measures whether claims in the generated answer are supported by
the retrieved company information or operational data.

Purpose:
Detect hallucinated or unsupported statements.


### 10. Response Relevance

Measures whether the generated response actually addresses
the customer's request.

Purpose:
Prevent technically correct but irrelevant answers.


### 11. Response Completeness

Measures whether the answer contains all information required
to correctly address the customer's request.

Purpose:
Detect answers that are correct but omit important information.


### 12. Correct Escalation / Abstention

Measures whether the system correctly recognizes cases where it should
not provide a definitive answer.

Examples:

- insufficient information
- ambiguous request
- unsupported topic
- missing policy
- business-critical case

Two important error types:

False Answer:
AI answers although escalation or clarification was required.

False Escalation:
AI escalates although enough information was available.


### 13. Source / Citation Correctness

Measures whether the sources shown to the support employee
actually support the generated answer.

Purpose:
Ensure that displayed references are trustworthy and useful.


## 4. Technical & Operational Metrics

### 14. Response Latency

Time between submitting a customer request and receiving
the AI-generated suggestion.

Purpose:
Ensure that the Copilot is fast enough to improve agent productivity.


### 15. System Error Rate

Percentage of requests that fail because of technical errors.

Examples:

- LLM API failure
- Order API failure
- retrieval failure
- database error


### 16. Cost per AI Request

Average cost of generating one AI-assisted response.

Possible components:

- LLM input tokens
- LLM output tokens
- embedding usage
- infrastructure cost

Purpose:
Evaluate whether the solution remains economically viable at scale.