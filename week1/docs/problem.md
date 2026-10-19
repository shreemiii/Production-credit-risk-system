# Problem statement

Team: Production Credit Risk System (team member names to confirm before submission)

## 1. Who uses the model, and for what decision?
Loan underwriting analysts use the estimated probability of repayment difficulty when reviewing new applications. At application time, the score supports a decision to approve, refer for manual review, or reject. Without the model, staff would rely on established underwriting rules and manual evaluation. The score informs, but does not independently determine, a lending decision.

## 2. The options
Low-risk applications may proceed to approval subject to eligibility checks; borderline applications go to an underwriter for document verification and judgment; high-risk applications may be rejected with appropriate review and adverse-action procedures. Referral has staff-time costs and delays the applicant, so the review band must balance those costs against avoidable defaults.

## 3. The cost of approving someone who defaults
An approved applicant who defaults costs the lender **10 relative cost units** in the assignment's simplified loss model, reflecting lost principal, servicing, and collection costs.

## 4. The cost of rejecting someone who would have repaid
Rejecting a would-be repayer costs **1 relative unit** of lost lending opportunity. The 10:1 ratio makes false approvals more expensive than false rejections. In a simplified two-action comparison without review costs, approve when 10p < 1(1-p), or p < 1/11 (~9.1%); actual thresholds also depend on calibration, revenues, constraints, and review costs. Threshold optimization belongs to a later week.

## 5. Success metrics, and why
Use ROC-AUC for ranking across thresholds, PR-AUC for identifying rare defaults, and KS for class separation; track expected business cost once decisions and their costs are specified. Accuracy alone is misleading: when approximately 8% default, predicting no defaults gives about 92% accuracy while catching none. The baseline should outperform random ranking (ROC-AUC 0.5 and PR-AUC near prevalence), with stable metrics on unseen applicants. Business usefulness also requires acceptable cost and fairness, not just a high AUC.

## 6. Risks and sensitive features
CODE_GENDER and DAYS_BIRTH (age) describe sensitive characteristics; REGION_RATING_CLIENT and geographic, employment, and income variables may proxy for protected status. False rejections may exclude qualified applicants; false approvals may expose borrowers to harmful debt and the lender to losses. Audit group performance and applicable lending-law requirements before deployment. Sensitive variables require careful governance, not an assumption that simply deleting them guarantees fairness.

## 7. Assumptions
We assume the historical TARGET reasonably represents future repayment difficulty, that application-time features are available before the decision, that the 10:1 costs are useful approximations, and that sampled applicants resemble future applicants. The largest concern is distribution shift or selection bias: historical lender applicants and approved loans may differ from future populations. Any such mismatch requires additional validation before deployment.
