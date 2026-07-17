# Calendly — Current Task

*Updated: 2026-05-19*

---

## Active Work: Review AI Cost Anomaly Conversation

**Request from:** Jonathan Payne + Stephanie Foukaris (#internal-calendly)  
**Date:** May 19, 2026  
**Status:** Pending review

### Context
Jonathan flagged an AI conversation in a cost anomaly discussion between **Noah** and **Ian** (new FinOps FTE at Calendly). Stephanie asked Eduardo for tips to help them.

### What's Needed
- Review the AI conversation thread in #internal-calendly
- Provide expert input/tips on how they're using AI for cost anomaly analysis
- Respond in the Slack thread

### The Issue
Calendly had a cost anomaly — a spike attributed to **Gemini/LLM charges** that traced back to a **BigQuery job using `AI.GENERATE`**.

The confusion: the initiating action is a BQ query, but the cost shows up as **Gemini inference spend**, not in `bytes_billed`. The anomaly alert pointed to a "BQ query" but the actual charge was AI inference.

### Thread Details (Noah + Ian in #calendly-com)
1. **Noah Abramson** flagged the cost spike to Stephanie Wu
2. **Stephanie Wu** thought it was a query she ran but canceled (it kept running)
3. **Ian Stainbrook** (new FinOps FTE) investigated:
   - Cost was Gemini LLM calls, not BQ Analysis
   - BQ job contained `AI.GENERATE` — explains why Gemini spend is tied to a BQ job
   - Actual user: `jana.hilsenroth@calendly.com`, not Stephanie
   - `AI.GENERATE` is tricky: cost doesn't appear in `bytes_billed`, shows downstream as Gemini cost
   - DoiT likely correlates via BQ job ID embedded in Gemini billing labels
4. **Noah** asked about quotas they can apply to the project
5. **Ian** found token throughput limits + mentioned GCP **Spend Caps** (private preview) for budget enforcement/auto-pause

### Tips to Provide
1. Confirm attribution model: `AI.GENERATE` in BQ → cost lands as Gemini inference, not BQ bytes_billed
2. Use BQ job ID + SQL text + user_email to identify who triggered and whether intentional
3. Guardrails: quota/token throughput limits, Spend Caps (private preview), budget alerts
4. If this usage grows, define a repeatable tracking method to distinguish BQ compute cost vs downstream Gemini inference cost vs responsible user/project

---

## Broader Engagement: Accelerator Proposal + MLOps

**KB Task:** `task-calendly-gcp-map`  
**Scope:** Prepare accelerator proposal + MLOps implementation (GCP)

### Background
- Calendly is a GCP customer
- Existing project work: Agent evaluation framework (see `Agent_Evaluation.ipynb`, `eval_api/`)
- Accelerator scoping in progress

---

## Links
- Slack thread: #internal-calendly (Jonathan Payne's post)
- KB task: `task-calendly-gcp-map`
