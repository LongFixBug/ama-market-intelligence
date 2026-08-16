import os
import json
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AMA Market Intelligence API",
    description="Multi-Agent & GraphRAG Automated Market Analysis Backend",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session tracking for SSE streams
JOB_QUEUES: dict[str, asyncio.Queue] = {}

class AnalyzeRequest(BaseModel):
    topic: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AMA Market Intelligence Backend is Running 🚀"}

@app.get("/api/stream/{job_id}")
async def stream_agent_progress(job_id: str):
    """
    SSE stream endpoint sending real-time agent execution milestones to the frontend
    """
    queue = asyncio.Queue()
    JOB_QUEUES[job_id] = queue

    async def event_generator():
        try:
            while True:
                data = await queue.get()
                yield {
                    "event": "message",
                    "data": json.dumps(data, ensure_ascii=False)
                }
                if data.get("stage") == "completed" or data.get("stage") == "error":
                    break
        finally:
            JOB_QUEUES.pop(job_id, None)

    return EventSourceResponse(event_generator())

@app.post("/api/analyze/{job_id}")
async def trigger_analysis(job_id: str, req: AnalyzeRequest, bg_tasks: BackgroundTasks):
    """
    Triggers the Multi-Agent & GraphRAG pipeline in the background
    """
    async def task_runner():
        queue = JOB_QUEUES.get(job_id)
        
        async def event_callback(stage: str, message: str, report: dict = None):
            if queue:
                payload = {"stage": stage, "message": message}
                if report:
                    payload["report"] = report
                await queue.put(payload)

        try:
            # Import your agent pipeline here:
            from app.agents.market_crew import run_market_pipeline
            await run_market_pipeline(req.topic, event_callback)
        except Exception as e:
            if queue:
                await queue.put({"stage": "error", "message": f"Pipeline error: {str(e)}"})

    bg_tasks.add_task(task_runner)
    return {"status": "started", "job_id": job_id, "topic": req.topic}
