import time
from datetime import datetime
from typing import List

 

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

 

 

class Client(BaseModel):
    client: str
    port: int
    created: datetime = Field(default_factory=lambda: datetime.now(), eq=False)

 

 

app = FastAPI(title="IP:Port retriever")
db = []

 

 

def get_request_info(request: Request):
    if request.client:
        client = Client(client=request.client.host, port=request.client.port)
        db.append(client)
        return f"Client: {request.client.host}:{request.client.port}\n".encode("utf-8")
    else:
        return b"No client detected\n"

 

 

def streamer(times: int, text: bytes):
    yield f"Streaming data for {times} seconds\n"
    for _ in range(times):
        time.sleep(1)
        yield text
    yield f"\nOpen /clients/last to see the last client that connected to this server"

 

 

@app.get("/test", summary="Test endpoint")
def default(
    *,
    n: int = Query(10, description="Number of seconds to stream data"),
    request: Request,
):
    """For any request to this endpoint, the client ipv4 and port will be registered."""
    headers = {"Content-Type": "text/event-stream"}
    text = get_request_info(request)
    return StreamingResponse(streamer(n, text), headers=headers)


@app.get("/register", summary="Test endpoint")
def default(
    *,
    n: int = Query(10, description="Number of seconds to stream data"),
    request: Request,
):
    """For any request to this endpoint, the client ipv4 and port will be registered."""
    headers = {"Content-Type": "application/json"}
    text = get_request_info(request)
    return db[-1]

 

 

@app.get("/clients", response_model=List[Client], summary="Get list of clients")
def get_data():
    """Returns all the clients"""
    return db

 

 

@app.get(
    "/clients/last",
    response_model=Client,
    summary="Get last client",
    responses={404: {"description": "No clients registered"}},
)
def get_last():
    """Returns the last client"""
    if db:
        return db[-1]
    else:
        raise HTTPException(status_code=404, detail="No clients registered")

 

 

@app.post("/reset", summary="Reset database")
def reset():
    """Resets the database."""
    db.clear()
    return {"message": "Database cleared"}
