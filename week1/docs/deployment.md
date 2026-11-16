<!-- PROVIDED: copy this file to docs/deployment.md and fill in every placeholder.
     The check reads the service address from this file and calls it. -->


# Deployment (Week 5)

Team: Production Credit Risk System — Team 38

| Setting | Value |
|---|---|
| Service URL | https://credit-risk-api-1007537952235.us-central1.run.app |
| Project ID / Region | credit-risk-group3-513720 / us-central1 |
| Image | us-central1-docker.pkg.dev/credit-risk-group3-513720/credit-risk/api:v1 |
| Model bucket | gs://credit-risk-models-group3-513720 (private) |
| Model version served | 1 |
| Instances | Minimum 0, maximum 2 |
| Memory / CPU | 1 GiB / 1 CPU |
| Service account | credit-risk-api@credit-risk-group3-513720.iam.gserviceaccount.com |
| Bucket access | Storage Object Viewer for the service account |

## How to deploy a new model

1. Register the new model and run `python run.py export`.
2. Upload `model.joblib`, `model_info.json`, and `feature_store.parquet` directly into the private Cloud Storage bucket.
3. Build and deploy the updated Docker image using the steps in `docs/deploy_cloud_run.md`.
4. Verify `/health`, `/model-info`, and `/predict` on the live Cloud Run service.
5. Run the Wednesday and final project checks.

The model files are stored in Cloud Storage and are never committed to GitHub.


## How to deploy a new model

TODO: The steps your team follows when a new model is registered (export, upload the bundle,
redeploy or restart the service), so that someone else on the team could do it.
