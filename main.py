from fastapi import FastAPI, HTTPException
import uvicorn
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable, List
from pydantic import BaseModel

# Importing your existing components
from src.gorzdrav.async_client import AsyncGorzdrav
from src.gorzdrav.exceptions import GorzdravExceptionBase
import src.gorzdrav.models as models
from src.config import Config

app = FastAPI(title="Gorzdrav API Proxy", version="0.1.0")


class ClientPool:
    """Async client pool with request queue management"""
    def __init__(self, pool_size: int = Config.POOL_SIZE, maxsize=Config.QUEUE_MAXSIZE):
        self.pool_size = pool_size
        self.request_queue = asyncio.Queue(maxsize=maxsize)
        self.worker_tasks: List[asyncio.Task] = []
        self.clients: List[AsyncGorzdrav] = []
        
    async def initialize(self):
        """Initialize client pool and workers"""
        print(f"🚀 Initializing client pool with {self.pool_size} workers")
        self.clients = [AsyncGorzdrav() for _ in range(self.pool_size)]
        self.worker_tasks = [
            asyncio.create_task(self._process_queue(i)) 
            for i in range(self.pool_size)
        ]
    
    async def _process_queue(self, worker_id: int):
        """Worker process for handling queue items"""
        print(f"👷 Worker {worker_id} started")
        client = self.clients[worker_id]
        async with client:
            while True:
                try:
                    # Get request from queue
                    task_data = await self.request_queue.get()
                    
                    # Process request with current client
                    result = await task_data["handler"](client)
                    task_data["future"].set_result(result)
                except GorzdravExceptionBase as e:
                    task_data["future"].set_exception(e)
                except Exception as e:
                    task_data["future"].set_exception(e)
                finally:
                    self.request_queue.task_done()
    
    async def submit_request(self, handler: Callable[[AsyncGorzdrav], Awaitable[Any]]) -> Any:
        """Submit a request to the processing queue"""
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        
        await self.request_queue.put({
            "handler": handler,
            "future": future
        })
        
        return await future
    
    async def shutdown(self):
        """Shutdown the client pool"""
        print("🛑 Shutting down client pool")
        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()
        # Wait for tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)


# Initialize client pool
pool = ClientPool()


# ===== FastAPI Event Handlers =====
@app.on_event("startup")
async def startup_event():
    await pool.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    await pool.shutdown()


# ===== Common Response Models =====
class ErrorResponse(BaseModel):
    error: str
    code: Optional[int] = None
    detail: Optional[str] = None


# ===== API Endpoints =====
@app.get("/districts", 
         response_model=List[models.ApiDistrict],
         responses={400: {"model": ErrorResponse}})
async def get_districts():
    """Get all available districts"""
    async def handler(client: AsyncGorzdrav):
        return await client.get_districts()
        
    try:
        return await pool.submit_request(handler)
    except GorzdravExceptionBase as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "API Error", "code": e.errorCode, "detail": e.message}
        )


@app.get("/lpus", 
         response_model=List[models.ApiLPU],
         responses={400: {"model": ErrorResponse}})
async def get_lpus(district_id: Optional[str] = None):
    """Get medical institutions (LPUs) with optional district filter"""
    async def handler(client: AsyncGorzdrav):
        return await client.get_lpus(district_id)
    
    try:
        return await pool.submit_request(handler)
    except GorzdravExceptionBase as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "API Error", "code": e.errorCode, "detail": e.message}
        )


@app.get("/specialties", 
         response_model=List[models.ApiSpecialty],
         responses={400: {"model": ErrorResponse}})
async def get_specialties(lpu_id: int):
    """Get specialties for a specific medical institution"""
    async def handler(client: AsyncGorzdrav):
        return await client.get_specialties(lpu_id)
    
    try:
        return await pool.submit_request(handler)
    except GorzdravExceptionBase as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "API Error", "code": e.errorCode, "detail": e.message}
        )


@app.get("/doctors", 
         response_model=List[models.ApiDoctor],
         responses={400: {"model": ErrorResponse}})
async def get_doctors(lpu_id: int, specialty_id: str):
    """Get doctors by specialty in a medical institution"""
    async def handler(client: AsyncGorzdrav):
        return await client.get_doctors(lpu_id, specialty_id)
    
    try:
        return await pool.submit_request(handler)
    except GorzdravExceptionBase as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "API Error", "code": e.errorCode, "detail": e.message}
        )


@app.get("/appointments", 
         response_model=List[models.ApiAppointment],
         responses={400: {"model": ErrorResponse}})
async def get_appointments(lpu_id: int, doctor_id: str):
    """Get available appointments for a doctor"""
    async def handler(client: AsyncGorzdrav):
        return await client.get_appointments(lpu_id, doctor_id)
    
    try:
        return await pool.submit_request(handler)
    except GorzdravExceptionBase as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "API Error", "code": e.errorCode, "detail": e.message}
        )


class ParseUrlResponse(BaseModel):
    valid: bool
    result: Optional[models.LinkParsingResult] = None
    error: Optional[str] = None


@app.get("/parse-url", 
         response_model=ParseUrlResponse,
         responses={400: {"model": ErrorResponse}})
async def parse_gorzdrav_url(url: str):
    """Parse Gorzdrav appointment URL for identifiers"""
    try:
        result =    (url)
        if result is None:
            return {
                "valid": False,
                "error": "URL does not contain valid Gorzdrav appointment parameters"
            }
        return {"valid": True, "result": result}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "Parsing Error", "detail": str(e)}
        )


if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=Config.HOST,
        port=Config.PORT,
        workers=Config.SERVER_WORKERS,
        loop="uvloop",
        http="httptools"
    )