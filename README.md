# GenAI Agent Evaluation Notebooks

Collection of Jupyter notebooks demonstrating evaluation techniques for generative AI agents using Google Vertex AI and various frameworks.

## Overview

This repository contains three notebooks that showcase different approaches to evaluating AI agents:

1. **Agent_Evaluation.ipynb** - Comparing OpenAI and Gemini agents using LangChain
2. **Basic_EvalKit_Sample.ipynb** - RAG evaluation with reference-free and referenced metrics
3. **Basic_Agent_Evaluation.ipynb** - Direct comparison of Gemini and OpenAI using native SDKs

## Prerequisites

```bash
pip install "google-cloud-aiplatform>=1.66.0" \
            "langchain>=0.2" \
            "langchain-openai" \
            "langchain-google-vertexai" \
            "google-genai" \
            "openai" \
            pandas
```

### Required Setup

- **Google Cloud Project**: Active GCP project with Vertex AI API enabled
- **OpenAI API Key**: For OpenAI model comparisons
- **Authentication**: Run `gcloud auth application-default login` or use Colab authentication

## Notebooks

### 1. Agent_Evaluation.ipynb

**Purpose**: Compare OpenAI GPT-4 and Gemini agents using LangChain framework with Vertex AI evaluation.

**Key Features**:
- LangChain integration for both OpenAI and Gemini
- Simple customer support agent implementation
- Side-by-side evaluation using Vertex AI metrics
- Visualization with radar and bar plots

**Metrics Used**:
- `question_answering_quality` (LLM-as-judge)
- `groundedness` (LLM-as-judge)
- `rouge` (computation-based)
- `exact_match` (computation-based)

**Use Case**: When you want to compare different LLM providers using a unified LangChain interface.

### 2. Basic_EvalKit_Sample.ipynb

**Purpose**: Comprehensive RAG evaluation demonstrating both reference-free and referenced evaluation approaches.

**Key Features**:
- Reference-free evaluation (no golden answers needed)
- Referenced evaluation (with golden answers)
- Custom metric definitions using PointwiseMetric
- Comparison of good vs poor RAG responses
- Interactive visualizations with radar and bar plots

**Metrics Used**:

*Reference-Free*:
- `question_answering_quality`
- `relevance`
- `helpfulness`
- `groundedness`
- `safety`
- `instruction_following`

*Referenced*:
- `question_answering_correctness`
- `rouge`
- `bleu`
- `exact_match`

**Use Case**: When you need comprehensive evaluation of RAG systems with both automated and reference-based metrics.

### 3. Basic_Agent_Evaluation.ipynb

**Purpose**: Direct comparison of Gemini and OpenAI using native SDKs without framework abstractions.

**Key Features**:
- Direct API calls to Gemini (via google-genai SDK)
- Direct API calls to OpenAI (via openai SDK)
- Minimal dependencies and overhead
- Vertex AI evaluation integration
- SQuAD-style dataset format

**Metrics Used**:
- `question_answering_quality`
- `groundedness`
- `rouge`
- `exact_match`

**Use Case**: When you want direct control over API calls without framework abstractions, or need to evaluate models using their native SDKs.

## Quick Start

### 1. Configure Your Environment

```python
# Set your GCP project ID
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-openai-key"
```

### 2. Authenticate (for Colab)

```python
from google.colab import auth
auth.authenticate_user()
```

### 3. Run Evaluation

Each notebook follows a similar pattern:

1. **Setup**: Initialize clients and define test data
2. **Generate Responses**: Call both models with the same prompts
3. **Create Datasets**: Format responses for Vertex AI evaluation
4. **Run Evaluation**: Execute EvalTask for each model
5. **Visualize Results**: Compare metrics using plots

## Evaluation Metrics Explained

### LLM-as-Judge Metrics

These metrics use Gemini as a judge to evaluate responses:

- **question_answering_quality**: Overall quality of the answer (1-5 scale)
- **groundedness**: Whether the response is grounded in the provided context (0-1)
- **relevance**: How relevant the answer is to the question (0-5)
- **helpfulness**: How helpful the response is to the user (0-5)
- **safety**: Whether the response is safe and appropriate (0-1)
- **instruction_following**: How well the response follows instructions (1-5)

### Computation-Based Metrics

These metrics use algorithmic comparison:

- **rouge**: Overlap of n-grams between response and reference (0-1)
- **bleu**: Precision-based metric for text similarity (0-1)
- **exact_match**: Binary match between response and reference (0-1)

### Custom Metrics

You can define custom metrics using `PointwiseMetric`:

```python
from vertexai.evaluation import PointwiseMetric

custom_metric = PointwiseMetric(
    metric="custom_metric_name",
    metric_prompt_template="Your evaluation prompt: {response}"
)
```

## Vertex AI Experiments

All evaluations are tracked in Vertex AI Experiments, allowing you to:

- Compare multiple runs side-by-side
- Track metrics over time
- Export results to BigQuery
- Share results with team members

Access your experiments at:
```
https://console.cloud.google.com/vertex-ai/experiments
```

## Visualization

All notebooks include visualization utilities:

```python
from vertexai.preview.evaluation import notebook_utils

# Radar plot for comparing multiple metrics
notebook_utils.display_radar_plot(results, metrics=["quality", "groundedness"])

# Bar plot for detailed comparison
notebook_utils.display_bar_plot(results, metrics=["rouge", "exact_match"])

# Detailed results table
notebook_utils.display_eval_result(title="Model A", eval_result=result_a)
```

## Best Practices

1. **Start Small**: Begin with 3-5 test cases to validate your setup
2. **Use Reference-Free First**: Start with reference-free metrics to quickly assess quality
3. **Add References Later**: Create golden answers for critical use cases
4. **Track Experiments**: Use consistent experiment names to track progress
5. **Iterate on Prompts**: Use evaluation results to improve your prompts
6. **Monitor Costs**: LLM-as-judge metrics incur API costs

## Common Use Cases

### Comparing LLM Providers
Use **Agent_Evaluation.ipynb** or **Basic_Agent_Evaluation.ipynb** to compare OpenAI vs Gemini on your specific use case.

### RAG System Evaluation
Use **Basic_EvalKit_Sample.ipynb** to evaluate retrieval quality, answer accuracy, and groundedness.

### Prompt Engineering
Run evaluations after each prompt iteration to measure improvement objectively.

### Production Monitoring
Integrate evaluation metrics into your CI/CD pipeline to catch regressions.

## Troubleshooting

### "Missing required input `prompt` column"
Ensure your dataset has a `prompt` column. Vertex AI expects this specific column name.

### Authentication Errors
Run `gcloud auth application-default login` or use Colab's `auth.authenticate_user()`.

### API Rate Limits
Reduce batch size or add delays between API calls if you hit rate limits.

### Metric Computation Failures
Check that your dataset has all required columns (`prompt`, `response`, `reference` for referenced metrics).

## Resources

- [Vertex AI Evaluation Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/models/evaluate-models)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Google GenAI SDK Documentation](https://ai.google.dev/gemini-api/docs)

## Contributing

Feel free to submit issues or pull requests to improve these notebooks.

## License

MIT License - See LICENSE file for details
