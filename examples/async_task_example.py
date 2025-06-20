# Async Task Processing Example
# Demonstrates handling long-running tasks with status tracking

import asyncio
import uuid
from typing import Dict, Any
from mcp_framework import FastMCPWrapper, ConfigLoader

# Task storage (in production, use a database)
tasks: Dict[str, Dict[str, Any]] = {}

server = FastMCPWrapper(
    name="async-task-server",
    config=ConfigLoader().load_env()
)

async def simulate_long_task(task_id: str, task_type: str, params: Dict[str, Any]):
    """Simulate a long-running task"""
    tasks[task_id]["status"] = "running"
    tasks[task_id]["progress"] = 0
    
    # Simulate work with progress updates
    for i in range(10):
        await asyncio.sleep(1)  # Simulate work
        tasks[task_id]["progress"] = (i + 1) * 10
        
        if tasks[task_id].get("cancelled"):
            tasks[task_id]["status"] = "cancelled"
            return
    
    # Simulate task completion
    tasks[task_id]["status"] = "completed"
    tasks[task_id]["progress"] = 100
    tasks[task_id]["result"] = f"Task {task_type} completed with params: {params}"

@server.tool()
async def start_task(task_type: str, params: Dict[str, Any] = None) -> str:
    """Start a long-running task"""
    task_id = str(uuid.uuid4())
    params = params or {}
    
    tasks[task_id] = {
        "id": task_id,
        "type": task_type,
        "status": "queued",
        "progress": 0,
        "params": params,
        "created_at": asyncio.get_event_loop().time()
    }
    
    # Start task in background
    asyncio.create_task(simulate_long_task(task_id, task_type, params))
    
    return task_id

@server.tool()
def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get task status and progress"""
    if task_id not in tasks:
        raise ValueError(f"Task {task_id} not found")
    
    return tasks[task_id]

@server.tool()
def list_tasks(status: str = None) -> Dict[str, Any]:
    """List all tasks, optionally filtered by status"""
    filtered_tasks = []
    
    for task in tasks.values():
        if status is None or task["status"] == status:
            filtered_tasks.append(task)
    
    return {
        "tasks": filtered_tasks,
        "total": len(filtered_tasks)
    }

@server.tool()
def cancel_task(task_id: str) -> Dict[str, Any]:
    """Cancel a running task"""
    if task_id not in tasks:
        raise ValueError(f"Task {task_id} not found")
    
    if tasks[task_id]["status"] in ["completed", "cancelled"]:
        return {"message": f"Task {task_id} already {tasks[task_id]['status']}"}
    
    tasks[task_id]["cancelled"] = True
    return {"message": f"Task {task_id} cancellation requested"}

@server.resource("task://{task_id}")
def task_resource(task_id: str) -> Dict[str, Any]:
    """Resource endpoint for task information"""
    return get_task_status(task_id)

if __name__ == "__main__":
    server.run()
