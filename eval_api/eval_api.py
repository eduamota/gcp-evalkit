"""
FastAPI backend for async evaluation
"""

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from vertexai.evaluation import EvalTask, PointwiseMetric
import vertexai
import os
import json
from pathlib import Path
import pandas as pd
from google.auth import default

app = FastAPI()

# Initialize with explicit credentials
credentials, project = default()
vertexai.init(
    project=os.getenv("GCP_PROJECT_ID", project), 
    location="us-central1",
    credentials=credentials
)

# Evaluation storage file
EVAL_FILE = Path("evaluations.json")

def load_evaluations():
    if EVAL_FILE.exists():
        return json.loads(EVAL_FILE.read_text())
    return {}

def save_evaluations(evaluations):
    EVAL_FILE.write_text(json.dumps(evaluations, indent=2))

# Store evaluations
evaluations = load_evaluations()

class ChatEvaluation(BaseModel):
    conversation_id: str
    query: str
    response: str

class EvalStatus(BaseModel):
    status: str
    results: dict = None

def run_evaluation(conv_id: str, query: str, response: str):
    """Background task to evaluate conversation"""
    try:
        dataset = pd.DataFrame([{"prompt": query, "response": response}])
        
        quality_metric = PointwiseMetric(
            metric="response_quality",
            metric_prompt_template="Rate response quality 1-5: {response}"
        )
        
        eval_task = EvalTask(
            dataset=dataset,
            metrics=["coherence", "fluency", quality_metric]
        )
        
        results = eval_task.evaluate()
        
        # Convert results to JSON-safe format
        summary = {}
        for key, value in results.summary_metrics.items():
            if pd.isna(value):
                summary[key] = None
            elif isinstance(value, (pd.Series, pd.DataFrame)):
                summary[key] = value.to_dict()
            else:
                summary[key] = float(value) if hasattr(value, '__float__') else value
        
        evaluations[conv_id] = {
            "status": "completed",
            "results": summary
        }
        save_evaluations(evaluations)
    except Exception as e:
        evaluations[conv_id] = {
            "status": "failed",
            "error": str(e)
        }
        save_evaluations(evaluations)

@app.post("/evaluate")
async def evaluate_chat(eval_data: ChatEvaluation, background_tasks: BackgroundTasks):
    """Trigger async evaluation"""
    evaluations[eval_data.conversation_id] = {"status": "processing"}
    save_evaluations(evaluations)
    background_tasks.add_task(
        run_evaluation,
        eval_data.conversation_id,
        eval_data.query,
        eval_data.response
    )
    return {"message": "Evaluation started", "conversation_id": eval_data.conversation_id}

@app.get("/evaluation/{conversation_id}")
async def get_evaluation(conversation_id: str):
    """Get evaluation status/results"""
    return evaluations.get(conversation_id, {"status": "not_found"})

@app.get("/health")
async def health():
    return {"status": "healthy"}
