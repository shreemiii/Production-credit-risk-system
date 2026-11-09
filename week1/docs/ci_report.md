# CI and the quality gate (Week 4)

Team: Group 3. Report author: Yousef Qanadilo.

## The pipeline

Cloud Build project: `credit-risk-group3-513720`. Trigger: `pr-checks`, on pull requests targeting `main` (base-branch expression `^main$`). The required GitHub check is `pr-checks (credit-risk-group3-513720)`. GitHub's main-branch metadata confirms protection is enabled and this Cloud Build check is required for everyone. The deliberate red PR is reported as blocked from merging.

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
- **Red run:** [Cloud Build 38a500a3-4c17-43d6-90bc-d40a29ac3ea4](https://console.cloud.google.com/cloud-build/builds/38a500a3-4c17-43d6-90bc-d40a29ac3ea4?project=1007537952235), for [PR #4](https://github.com/shreemiii/Production-credit-risk-system/pull/4), commit `06f334002c5747c7d4730e9ce099e1f7c5cf1de0`. GitHub reports failure, completed November 9, 2026 at 17:16:39 UTC. The sole change raises `min_auc` from 0.70 to 0.99. With the saved candidate AUC of 0.747122, the gate's AUC rule produces `validation AUC 0.747 is below the floor 0.990`. This message is derived from the committed code and metrics; the GitHub check summary confirms build failure but does not expose the detailed Cloud Build log. `config/gate.yaml` is excluded from the code fingerprint, so this change tests the AUC floor rather than stale-metrics detection. The demonstration tightens the acceptance rule; it does not retrain or degrade the model.
- **Blocked merge and PR disposition:** Green PR #2 was merged on November 9, 2026. For red PR #4, GitHub reports `mergeable: true` (no merge conflict), `mergeable_state: blocked`, and `merged: false`; main requires the failing Cloud Build check. This provides evidence that the required check blocks the merge. PR #4 is still open at verification time. Soumith must close it without merging to finish Step 23; this report does not claim that closure has happened.

Both build links and the blocked-merge evidence are now recorded. Remaining Step 23 follow-up: inspect the detailed red build log and close PR #4 without merging. Step 25's full submission checks and the final week4 tag remain separate team tasks.
