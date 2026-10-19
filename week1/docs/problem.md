# Problem statement

Team: Production Credit Risk System (confirm member names before submission)

## 1. Who uses the model, and for what decision?
Underwriters use default-risk estimates when an application arrives to support approval, manual review, or rejection. Today, eligibility rules and human review guide decisions. The model supports rather than replaces human judgment.

## 2. The options
Approve low-risk eligible applications; refer borderline cases to a human underwriter; reject only when the verified evidence and applicable underwriting policies justify it. Referrals cost analyst time and delay applicants.

## 3. The cost of approving someone who defaults
In the assignment's simplified model, a wrong approval costs 10 relative units.

## 4. The cost of rejecting someone who would have repaid
Rejecting a good borrower costs 1 relative unit of lost business. Because wrong approvals cost ten times more, the lender should apply a more conservative threshold. In a simplified two-decision model with calibrated default probability p, the cost comparison is 10p versus 1-p; approving minimizes those costs when p is below 1/11. The actual threshold needs additional assumptions and validation.

## 5. Success metrics, and why
ROC-AUC measures ranking; PR-AUC is particularly helpful with rare defaults; KS measures score separation; expected cost measures business impact once thresholds are selected. With roughly 8% defaults, always predicting no default could earn roughly 92% accuracy while missing all defaults. We want results better than random ranking on held-out data, stable enough to guide real decisions.

## 6. Risks and sensitive features
CODE_GENDER and DAYS_BIRTH are sensitive; geography, income, and employment can be proxies. Errors can unfairly deny credit or expose borrowers to harmful debt. Review subgroup performance, explainability, and lending compliance before deployment.

## 7. Assumptions
TARGET is treated as an informative historical outcome; input features must be available at application time; the simplified 10:1 cost ratio approximates business costs; and the historical sample is relevant to future applicants. Distribution shift or sampling bias could invalidate the approach.
