# Credit-risk scoring API

Team: Production Credit Risk System — Team 38

**Live base URL:** (https://credit-risk-api-1007537952235.us-central1.run.app)

**Local Docker URL:** http://127.0.0.1:8080

**Interactive documentation:** `<base URL>/docs`

The service uses FastAPI to serve a registered credit-risk
model. It supports health checks, model metadata retrieval,
and individual applicant credit-risk predictions.

## Endpoints

### Health check

**GET /health**

Checks whether the service is running and the model is loaded.

Request:

```bash
curl http://127.0.0.1:8080/health
```

Response — HTTP 200:

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_version": "1"
}
```

### Model information

**GET /model-info**

Returns the registered model's name, version, threshold, feature count, validation AUC, data version, and export time.

Request:

```bash
curl http://127.0.0.1:8080/model-info
```

Response — HTTP 200:

```json
{
  "name": "credit-risk",
  "version": "1",
  "threshold": 0.085,
  "n_features": 20,
  "valid_auc": 0.7457717056919088,
  "data_version": "9fb9955ad0ed",
  "exported": "2026-11-14T03:29:06+00:00"
}
```

### Credit-risk prediction

**POST /predict**

Returns the applicant's estimated default probability and a decision. If probability is at least the model threshold, the decision is reject; otherwise it is approve. The request must contain SK_ID_CURR and may optionally contain positive AMT_INCOME_TOTAL, AMT_CREDIT, and AMT_ANNUITY values.

Request:

```bash
curl -X POST http://127.0.0.1:8080/predict \
  -H 'Content-Type: application/json' \
  -d '{"SK_ID_CURR":100021}'
```

Response — HTTP 200:

```json
{
  "SK_ID_CURR": 100021,
  "probability": 0.1,
  "decision": "reject",
  "threshold": 0.085,
  "model_version": "1"
}
```

## Errors

### Invalid input

**POST /predict**

Pydantic rejects invalid fields before prediction. The following request fails because income is negative.

Request:

```bash
curl -X POST http://127.0.0.1:8080/predict \
  -H 'Content-Type: application/json' \
  -d '{"SK_ID_CURR":100021,"AMT_INCOME_TOTAL":-1000}'
```

Response — HTTP 422:

```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": [
        "body",
        "AMT_INCOME_TOTAL"
      ],
      "msg": "Input should be greater than 0",
      "input": -1000,
      "ctx": {
        "gt": 0.0
      }
    }
  ]
}
```

### Unknown applicant

**POST /predict**

If the applicant ID is absent from the feature store, the service returns HTTP 404 without performing a prediction.

Request:

```bash
curl -X POST http://127.0.0.1:8080/predict \
  -H 'Content-Type: application/json' \
  -d '{"SK_ID_CURR":999999999}'
```

Response — HTTP 404:

```json
{
  "detail": "Applicant 999999999 not found"
}
```


## Response times

**Measurement environment:** Google Cloud Run (us-central1)

**Live service URL:** https://credit-risk-api-1007537952235.us-central1.run.app

We tested the deployed API by sending 100 prediction requests.

| Metric | Result |
|---|---:|
| Successful timed requests | 100 |
| First request | 604 ms |
| p50 latency | 67 ms |
| p95 latency | 76 ms |
| Maximum latency | 84 ms |
| Errors | 0 |

The first request took longer than the others and may have included
a cold start. The p50 shows the typical response time, while the p95
shows the response time within which 95% of requests completed.

All 100 timed requests were successful, with no errors.


## Online or batch scoring?

Online scoring evaluates one applicant when a request arrives
and returns a decision immediately. Batch scoring processes
many applicants together, often on a scheduled basis.

Online scoring is appropriate when someone submits a credit
application and expects a timely response. Batch scoring is
more appropriate for periodically reviewing existing accounts
or generating risk reports for large groups of applicants.

Online scoring requires an available service and can incur
additional infrastructure costs. Batch scoring can process
large volumes efficiently but does not provide immediate
decisions between scheduled runs.

Our credit decision API uses online scoring because individual
loan applications need timely results. The precomputed feature
store helps reduce the work required for each online prediction.
