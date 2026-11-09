# CI and the quality gate (Week 4)

Team: Group 3. Report author: Yousef Qanadilo.

## The pipeline

Cloud Build project: `credit-risk-group3-513720`. Trigger: `pr-checks`, on pull requests targeting `main` (base-branch expression `^main$`). The required GitHub check is `pr-checks (credit-risk-group3-513720)`. The repository owner reported configuring branch protection to require a pull request and this check. Enforcement still needs the blocked-merge demonstration below.

The trigger reads `week1/cloudbuild.yaml`. Each step uses `python:3.11-slim` and `dir: week1`, because the Python project is inside that directory. Installation creates a shared virtual environment at `/workspace/.venv`; subsequent steps use its Python executable. Logs go to Cloud Logging, and the build has a 1,200-second timeout.

| Step | What it runs | Why it is there |
|---|---|---|
| install | Creates the virtual environment, upgrades pip, and runs `/workspace/.venv/bin/pip install --quiet -r requirements.txt` | Installs the project requirements on the fresh build machine. |
| lint | `/workspace/.venv/bin/python -m ruff check .` | Rejects code-style and static-analysis errors before testing. |
| test | `/workspace/.venv/bin/python -m pytest -q` | Runs the unit and other code tests. Real-data and model tests skip when their local data is absent: data and MLflow artifacts are not committed. Local testing is therefore still necessary. |
| gate | `/workspace/.venv/bin/python -m scripts.quality_gate` | Checks committed candidate metrics against the thresholds and the registered-model baseline; rejects stale metrics. |

A nonzero exit stops the build and makes the PR check fail. The service account selected for this trigger is `id-cloud-build-ci@credit-risk-group3-513720.iam.gserviceaccount.com`.

## Gate thresholds, and why

These comparisons use the committed `reports/gate_metrics.json`, `reports/final_model.json`, and `config/gate.yaml`. Candidate evaluation was recorded on November 4, 2026. Candidate validation AUC is 0.747122, with 95% interval [0.692884, 0.801362]. The registered baseline's validation AUC is approximately 0.745772, with 95% interval [0.692769, 0.799974]. These overlapping intervals do not establish that the candidate is better.

- **min_auc = 0.70.** The candidate's point estimate, 0.747122, exceeds this floor by 0.047122. The floor preserves ranking performance near the project's baseline level and catches substantial regressions. The gate compares the point estimate, not the confidence-interval lower bound; the candidate's lower bound is below 0.70, so passing is not proof that its population AUC exceeds the floor.
- **max_cost = 0.70.** Candidate cost per applicant is 0.533 at threshold 0.085, below the limit by 0.167. The same report gives costs of 0.810 for approving everyone, 0.919 for rejecting everyone, and 0.800 at threshold 0.5. A 0.70 ceiling requires improvement over those simple alternatives under the project's cost assumptions while allowing some deterioration from the current result. It is an operational tolerance, not a statistically derived confidence bound.
- **max_auc_drop = 0.02.** With registered AUC approximately 0.745772, the candidate must achieve at least 0.725772. Its 0.747122 point estimate clears this limit. This rule prevents accepting more than a two-percentage-point AUC loss relative to the registered model even when the absolute 0.70 floor would pass. The tolerance is a team guardrail, not a significance test; differences smaller than the reported uncertainty should not be described as proven improvements.
- **allow_failing_model_tests = 0.** The saved evaluation records two passed tests, zero failed tests, two expected failures, and zero skips. Zero permits no unexplained model-test failures. The two strict expected failures are documented gender-invariance and income-directionality findings in `docs/test_findings.md`; they remain unresolved behaviors, not successful tests. Cloud CI skips real-data/model tests, so the gate relies on the saved local evaluation for these counts.

Before checking the four rules, the gate compares the saved code fingerprint with the current model-building code and configuration. Changing fingerprinted inputs without rerunning `python run.py evaluate` makes the metrics stale and blocks the gate. A report's age alone is not the stale-metrics criterion. The fingerprint checks code consistency; it does not independently prove the identity of the locally loaded model or the quality of its data.

## Evidence

- **Green run:** [Cloud Build 860a335a-c0a5-480d-aa7a-26d303c79fb8](https://console.cloud.google.com/cloud-build/builds/860a335a-c0a5-480d-aa7a-26d303c79fb8?project=1007537952235), for [PR #2](https://github.com/shreemiii/Production-credit-risk-system/pull/2), commit `82dbc854a6c8f84da0f179bd06352d7c7580b527`. GitHub reported the Cloud Build check completed successfully on November 9, 2026.
- **Wednesday checker:** `python run.py check --stage wed` passed pipeline structure, threshold configuration, and the quality gate on the PR's code snapshot. This was the Wednesday checkpoint, not the full submission check.
- **Red run and exact gate message:** TODO: Soumith must complete Step 23 and provide the red Cloud Build link and its actual failure message. No red run was available when this draft was prepared.
- **Blocked merge and PR disposition:** TODO: Record the red PR link, evidence that branch protection blocked merging, and confirmation that it was closed without merging. At draft preparation, PR #2 was still open and no red demonstration PR existed.

This report remains a draft until the red-build evidence is supplied. The full submission checker must not be represented as passing while these items remain.
