import os
import sys
import json
import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure root workspace is in sys.path so backend can import ml module
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

env_path = os.path.join(root_dir, "backend/.env")
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
else:
    load_dotenv(override=True)

app = FastAPI(
    title="AMA Market Intelligence API Gateway",
    description="Backend API Gateway for Multi-Agent Market Analysis",
    version="1.0.0",
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session tracking for SSE streams
JOB_QUEUES: dict[str, asyncio.Queue] = {}

class AnalyzeRequest(BaseModel):
    topic: str

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "AMA Backend API Gateway",
        "version": "1.0.0",
    }

@app.get("/api/stream/{job_id}")
async def stream_agent_progress(job_id: str):
    """
    SSE stream endpoint: Pushes real-time agent execution milestones to the frontend client
    """
    if job_id not in JOB_QUEUES:
        JOB_QUEUES[job_id] = asyncio.Queue()
    
    queue = JOB_QUEUES[job_id]

    async def event_generator():
        try:
            while True:
                data = await queue.get()
                yield {
                    "event": "message",
                    "data": json.dumps(data, ensure_ascii=False),
                }
                if data.get("stage") == "completed" or data.get("stage") == "error":
                    break
        finally:
            JOB_QUEUES.pop(job_id, None)

    return EventSourceResponse(event_generator())

@app.post("/api/analyze/{job_id}")
async def trigger_analysis(job_id: str, req: AnalyzeRequest, bg_tasks: BackgroundTasks):
    """
    Triggers the Multi-Agent pipeline in background and pushes to SSE queue
    """
    if job_id not in JOB_QUEUES:
        JOB_QUEUES[job_id] = asyncio.Queue()
    
    queue = JOB_QUEUES[job_id]

    async def task_runner():
        async def event_callback(stage: str, message: str, report: dict = None):
            payload = {"stage": stage, "message": message}
            if report:
                payload["report"] = report
            await queue.put(payload)

        try:
            # Force reload .env to get any updated model / keys
            if os.path.exists(env_path):
                load_dotenv(env_path, override=True)
            from ml.pipelines.market_analysis_pipeline import execute_market_pipeline
            await execute_market_pipeline(req.topic, event_callback)
        except Exception as e:
            print(f"[Pipeline Error] {e}")
            await queue.put({"stage": "error", "message": f"Pipeline error: {str(e)}"})

    bg_tasks.add_task(task_runner)
    return {"status": "started", "job_id": job_id, "topic": req.topic}

@app.post("/api/analyze-direct")
async def analyze_direct(req: AnalyzeRequest):
    """
    Synchronous direct endpoint returning final report in < 15s
    """
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)

    from ml.pipelines.market_analysis_pipeline import execute_market_pipeline

    async def dummy_callback(stage: str, message: str, report: dict = None):
        pass

    report = await execute_market_pipeline(req.topic, dummy_callback)
    return report
