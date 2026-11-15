# API design (Week 5)

Team: Production Credit Risk System — Team 38

## 1. Where do the 164 features come from?

Our Week 2 pipeline creates 164 features using the main application dataset and six related historical tables. Many features require aggregating multiple records, such as an applicant's previous loans, credit history, and payment behavior.

Having the API caller send all 164 features would be impractical. The caller may only have the applicant's ID and updated application amounts, not the historical data needed to calculate the remaining features. It would also require the caller to reproduce our feature engineering logic correctly.

There are two approaches we considered:

**Option 1: Calculate features during each request.** The service could query the historical tables and calculate the required aggregates whenever a prediction is requested. This would support fresher data, but would increase response times, infrastructure complexity, and the risk of differences between training and serving calculations.

**Option 2: Use a precomputed feature store.** The service could retrieve features that were calculated beforehand using the same pipeline as training. This makes predictions faster and simplifies the API. The tradeoff is that the feature store must be refreshed when the underlying applicant data changes.

Although the original feature dataset contains 164 features, our final Week 3 model uses 20 selected features.

## 2. What we chose, and why

We chose a precomputed feature store keyed by `SK_ID_CURR`.

Our exported model bundle contains `model.joblib`, `model_info.json`, and `feature_store.parquet`. The feature store contains 5,000 applicant records and allows the service to retrieve the features for one applicant without processing all the historical tables again.

A prediction request requires an applicant ID (`SK_ID_CURR`) and can optionally include updated values for `AMT_INCOME_TOTAL`, `AMT_CREDIT`, and `AMT_ANNUITY`.

When a request arrives, `build_features()` looks up the applicant, copies their stored row, and replaces any amounts provided in the request. The original feature store is never modified.

If an amount changes, the service recalculates the applicable ratios:

- `CREDIT_INCOME_RATIO = AMT_CREDIT / AMT_INCOME_TOTAL`
- `ANNUITY_INCOME_RATIO = AMT_ANNUITY / AMT_INCOME_TOTAL`
- `CREDIT_GOODS_RATIO = AMT_CREDIT / AMT_GOODS_PRICE`
- `ANNUITY_CREDIT_RATIO = AMT_ANNUITY / AMT_CREDIT`

The function recalculates each ratio when its required columns are present. Zero or missing denominators produce NaN rather than infinity.

Finally, the function returns the 20 selected features in the exact order expected by the registered model.

This approach makes sense for our project because it keeps the API simple, avoids repeatedly calculating historical aggregates, and reuses features from the existing training pipeline.

## 3. What can go wrong

**Unknown applicant:** If an applicant's `SK_ID_CURR` is not in the feature store, the service raises `UnknownApplicant` and returns HTTP 404. It does not attempt a prediction using nonexistent data.

**Feature store and model mismatch:** If the feature store was generated using different data or feature engineering code from the registered model, predictions might be inaccurate or fail. We reduce this risk by exporting the feature store alongside the model, preserving the expected feature order, and running automated tests.

**Outdated applicant history:** An applicant's financial information may change after the feature store is generated. The API can accept updated income, credit, and annuity amounts, but changes to historical records require the feature store to be regenerated. Until then, the service uses the previously stored historical features.

**Invalid request values:** FastAPI and Pydantic reject missing required fields, negative or zero amounts, and unexpected fields with HTTP 422. These requests do not reach the prediction function.

## 4. Example requests

The following examples were tested against our exported model using the local FastAPI application.

### Example 1: Valid prediction

**POST /predict**

Request:

```json
{
  "SK_ID_CURR": 100021
}
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

The applicant's estimated default probability is 0.100, which exceeds the model threshold of 0.085. Therefore, the service returns `reject`.

### Example 2: Invalid income

**POST /predict**

Request:

```json
{
  "SK_ID_CURR": 100021,
  "AMT_INCOME_TOTAL": -1000
}
```

Response — HTTP 422:

```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "AMT_INCOME_TOTAL"],
      "msg": "Input should be greater than 0",
      "input": -1000,
      "ctx": {
        "gt": 0.0
      }
    }
  ]
}
```

Pydantic rejects the request because income must be greater than zero.

### Example 3: Unknown applicant

**POST /predict**

Request:

```json
{
  "SK_ID_CURR": 999999999
}
```

Response — HTTP 404:

```json
{
  "detail": "Applicant 999999999 not found"
}
```

The applicant does not exist in the feature store, so the service returns 404 without making a prediction.