import os
import json
import asyncio
import uvicorn
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from pipeline_runner import PipelineRunner

app = FastAPI(title="Docpilot Web UI")
executor = ThreadPoolExecutor(max_workers=4)

# In-memory task state
tasks = {}

def run_pipeline_background(task_id: str, loop: asyncio.AbstractEventLoop):
    task_info = tasks.get(task_id)
    if not task_info:
        return

    runner = task_info["runner"]
    queue = task_info["queue"]

    def progress_callback(event_type, data):
        loop.call_soon_threadsafe(queue.put_nowait, {"type": event_type, "data": data})

    try:
        result = runner.generate_document(progress_callback)
        loop.call_soon_threadsafe(queue.put_nowait, {"type": "complete", "data": result})
        task_info["status"] = "done"
        task_info["result"] = result
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        loop.call_soon_threadsafe(queue.put_nowait, {
            "type": "failed", 
            "data": {"message": str(e), "trace": err_msg}
        })
        task_info["status"] = "failed"

@app.get("/", response_class=HTMLResponse)
async def get_index():
    filepath = os.path.join("templates", "index.html")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>templates/index.html not found!</h3>"

@app.post("/api/generate")
async def start_generation(topic: str = Form(...), pages: int = Form(...)):
    task_id = f"task_{int(asyncio.get_event_loop().time())}"
    runner = PipelineRunner(topic, pages)
    queue = asyncio.Queue()

    tasks[task_id] = {
        "runner": runner,
        "queue": queue,
        "status": "pending",
        "result": None
    }

    loop = asyncio.get_running_loop()
    # Run outline generation inside executor thread to keep app responsive
    outline = await loop.run_in_executor(executor, runner.generate_outline)
    tasks[task_id]["status"] = "awaiting_approval"

    return {"task_id": task_id, "outline": outline}

@app.post("/api/feedback")
async def outline_feedback(task_id: str = Form(...), feedback: str = Form(...)):
    if task_id not in tasks:
        return {"error": "Invalid task ID"}

    runner = tasks[task_id]["runner"]
    loop = asyncio.get_running_loop()
    outline = await loop.run_in_executor(executor, runner.add_feedback, feedback)

    return {"outline": outline}

@app.post("/api/approve")
async def approve_outline(task_id: str = Form(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    if task_id not in tasks:
        return {"error": "Invalid task ID"}

    tasks[task_id]["status"] = "generating"
    loop = asyncio.get_running_loop()
    
    # Delegate the heavy generation & repair steps to background task
    background_tasks.add_task(run_pipeline_background, task_id, loop)

    return {"status": "generating"}

@app.get("/api/stream/{task_id}")
async def stream_progress(task_id: str):
    if task_id not in tasks:
        async def err_generator():
            yield f"data: {json.dumps({'type': 'error', 'message': 'Invalid task ID'})}\n\n"
        return StreamingResponse(err_generator(), media_type="text/event-stream")

    queue = tasks[task_id]["queue"]

    async def event_generator():
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
            if event["type"] in ["complete", "failed"]:
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/decide")
async def make_decision(task_id: str = Form(...), choice: str = Form(...)):
    if task_id not in tasks:
        return {"error": "Invalid task ID"}

    task_info = tasks[task_id]
    result = task_info.get("result")
    if not result:
        return {"error": "No generation result found"}

    filename = result["filename"]
    filepath = os.path.join("output", filename)

    if choice == "reject":
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                return {"status": "error", "message": f"Failed to delete file: {e}"}
        return {"status": "rejected"}
    else:
        return {"status": "accepted", "filename": filename}

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    safe_filename = os.path.basename(filename)
    filepath = os.path.join("output", safe_filename)
    if os.path.exists(filepath):
        return FileResponse(
            filepath, 
            filename=safe_filename, 
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    return {"error": "File not found"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
