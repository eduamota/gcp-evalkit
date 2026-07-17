# Research: AI.GENERATE Cost Anomaly — Expert Tips for Calendly

*Compiled: 2026-05-19*

---

## Summary for Slack Thread

Ian's analysis is spot-on. Here's the full picture and actionable next steps:

---

## 1. Cost Attribution Model (Confirming Ian's Finding)

**`AI.GENERATE` in BigQuery incurs TWO separate charges:**

| Charge Type | Where It Appears | What It Covers |
|---|---|---|
| BigQuery ML | `bytes_billed` / BQ compute | Data processed by the query (scanning rows) |
| Vertex AI (Gemini) | Separate Vertex AI line item | Token usage (input + output) for LLM inference |

**Key insight:** The Gemini inference cost does NOT appear in `bytes_billed`. It's billed as a Vertex AI SKU. For Gemini 2.0+ models, AI.GENERATE is billed at the **batch API rate** (cheaper than online, but still per-token).

This is why the anomaly alert pointed to a "BQ query" but the actual charge was Gemini inference — they're two different billing services triggered by the same SQL statement.

---

## 2. Tracing: Who Triggered It & Was It Intentional?

### BigQuery Side (INFORMATION_SCHEMA.JOBS)

```sql
SELECT
  job_id,
  user_email,
  query,
  creation_time,
  total_bytes_billed,
  state
FROM `project_id.region-us.INFORMATION_SCHEMA.JOBS`
WHERE
  creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND (query LIKE '%AI.GENERATE%' OR query LIKE '%AI.GENERATE_TEXT%')
ORDER BY creation_time DESC;
```

This gives you: **who** (`user_email`), **what** (the SQL text), **when**, and the `job_id`.

### Billing Export Side (Vertex AI costs)

In the detailed billing export table:
- Filter: `service.description = "Vertex AI"` (or "Cloud AI Platform")
- Look at `sku.description` for token-specific SKUs (e.g., "Gemini 2.0 Flash Input Tokens", "Gemini 2.0 Flash Output Tokens")
- Use `labels.key` / `labels.value` for any custom labels attached to the API calls
- Correlate by timestamp and project to match back to the BQ job

### DoiT Correlation

DoiT likely correlates via the BQ `job_id` that gets embedded as a label in the downstream Vertex AI billing record. BigQuery passes metadata when it calls Vertex AI on behalf of AI.GENERATE.

---

## 3. Guardrails: Quotas & Throughput Limits

### Vertex AI Token Quotas (Immediate — No Cost)

Vertex AI enforces **per-project, per-region** quotas:
- **Tokens Per Minute (TPM)** — limits total token throughput
- **Requests Per Minute (RPM)** — limits API call volume

**How to view/edit:**
1. Console → **IAM & Admin → Quotas & System Limits**
2. Filter by: `aiplatform.googleapis.com` and the specific model metric
3. Click the quota → **Edit Quota** → set a lower value

**Recommendation:** Lower the TPM quota on the project where AI.GENERATE runs. This won't prevent usage but will throttle it (queries get 429 errors and retry/fail rather than running unbounded).

### Standard PayGo Tiered Throughput

Vertex AI dynamically adjusts baseline throughput based on the org's rolling 30-day spend. Higher spend = higher tier = more capacity. This means a runaway job can actually *increase* your future capacity ceiling.

### BigQuery Custom Query Quotas

You can also set **custom query quotas** in BigQuery to limit bytes scanned per user/project/day. This won't directly cap Gemini token costs but limits how many rows can be fed to AI.GENERATE.

---

## 4. Spend Caps (Private Preview — Sign Up Now)

**Announced:** Google Cloud Next '26 (April 2026)
**Status:** Private Preview — sign up via [Google Form](https://docs.google.com/forms/d/12TIOZQq4FWb7LMZ_IFLBIM3sQPJipyNAkiw8pRw7d50/viewform)

**How it works:**
- Set a budget at the **project level**
- Works with: Google AI Studio, Agent Platform (Vertex AI), Cloud Run, Cloud Run Functions, Maps
- When budget is reached: **alerts first, then pauses API traffic**
- Resources stay intact — nothing is deleted
- To resume: simply suspend the Spend Cap

**This is the closest thing GCP has to a hard spending limit.** Traditional GCP budgets only alert — they don't enforce. Spend Caps actually stop the bleeding.

**Recommendation:** Sign up for the private preview immediately. This is exactly what Calendly needs for AI experimentation projects.

---

## 5. Repeatable Tracking Method: BQ Compute vs Gemini Inference

### Setup: Detailed Billing Export to BigQuery

1. **Enable "Detailed usage cost data"** export (not just standard) — this is mandatory for resource-level AI tracking
2. Use a **multi-region dataset (US or EU)** for retroactive backfill
3. Create BigQuery Views to shield reports from schema changes

### Query: Separate BQ vs Vertex AI Costs

```sql
-- Vertex AI / Gemini inference costs
SELECT
  invoice.month,
  project.id AS project_id,
  sku.description AS sku,
  SUM(cost) AS total_cost,
  SUM(usage.amount) AS total_usage
FROM `billing_project.billing_dataset.gcp_billing_export_resource_v1_XXXXXX`
WHERE service.description = 'Vertex AI'
  AND sku.description LIKE '%Gemini%Token%'
GROUP BY 1, 2, 3
ORDER BY total_cost DESC;

-- BigQuery compute costs (same period)
SELECT
  invoice.month,
  project.id AS project_id,
  sku.description AS sku,
  SUM(cost) AS total_cost
FROM `billing_project.billing_dataset.gcp_billing_export_resource_v1_XXXXXX`
WHERE service.description = 'BigQuery'
GROUP BY 1, 2, 3
ORDER BY total_cost DESC;
```

### Pro Tip: Custom Labels for Attribution

Vertex AI supports **custom metadata labels** on `generateContent` API calls:

```json
{
  "contents": { "role": "user", "parts": { "text": "..." } },
  "labels": {
    "team": "data-science",
    "use_case": "cost-anomaly-analysis",
    "triggered_by": "bigquery-ai-generate"
  }
}
```

These labels flow into the billing export under `labels.key` / `labels.value`. However, for AI.GENERATE specifically, BigQuery controls the Vertex AI call — so custom labels would need to be applied at the BQ connection or model level (limited today).

### Recommended Dashboard Dimensions

| Dimension | Source | Purpose |
|---|---|---|
| Service | `service.description` | BQ vs Vertex AI split |
| SKU | `sku.description` | Token type (input/output), model version |
| Project | `project.id` | Which project incurred cost |
| User | `INFORMATION_SCHEMA.JOBS.user_email` | Who ran the query |
| Job ID | `INFORMATION_SCHEMA.JOBS.job_id` | Correlate BQ job → Vertex AI cost |
| Time | `usage_start_time` | When the cost was incurred |

---

## 6. Immediate Action Items for Calendly

1. **Confirm the user** — Run the INFORMATION_SCHEMA query above to verify it was `jana.hilsenroth@calendly.com` and check if the query was intentional or exploratory
2. **Lower Vertex AI TPM quota** on the affected project — prevents unbounded token spend
3. **Set up a Budget Alert** on the project for Vertex AI service specifically (Console → Billing → Budgets)
4. **Sign up for Spend Caps private preview** — this is the real solution for hard enforcement
5. **Enable detailed billing export** if not already done — needed for ongoing tracking
6. **Create a saved query/dashboard** using the SQL above to monitor AI.GENERATE costs weekly

---

## References

- [Choose a text generation function (billing details)](https://docs.cloud.google.com/bigquery/docs/choose-text-generation-function)
- [Optimize AI function costs](https://docs.cloud.google.com/bigquery/docs/optimize-ai-functions)
- [Vertex AI Quotas](https://cloud.google.com/vertex-ai/generative-ai/docs/quotas)
- [Custom metadata labels for cost monitoring](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/add-labels-to-api-calls)
- [Spend Caps announcement (Next '26)](https://cloud.google.com/blog/topics/cost-management/introducing-spend-caps-ai-cost-visibility-next26)
- [Spend Caps private preview signup](https://docs.google.com/forms/d/12TIOZQq4FWb7LMZ_IFLBIM3sQPJipyNAkiw8pRw7d50/viewform)
- [GCP Billing Export: Tracking AI Costs](https://discuss.google.dev/t/gcp-billing-export-to-bigquery-quick-guide-to-tracking-ai-costs/318584)
- [Standard PayGo throughput tiers](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/standard-paygo)
