import time
from datetime import datetime
from typing import List

 

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from starlette_context import middleware, plugins, context

 

 

class Client(BaseModel):
    client: str
    port: int
    created: datetime = Field(default_factory=lambda: datetime.now(), eq=False)

 

 

app = FastAPI(title="IP:Port retriever")
db = []

 
app.add_middleware(
    middleware.ContextMiddleware,
    plugins=(
        plugins.ForwardedForPlugin(),
    ),
)
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

@app.get("/register2", summary="Test endpoint")
def default(
    *,
    n: int = Query(10, description="Number of seconds to stream data"),
    request: Request,
):
    """For any request to this endpoint, the client ipv4 and port will be registered."""
    headers = {"Content-Type": "application/json"}
    forwarded_for = context.data["X-Forwarded-For"]
    
    return {"hello": "world", "forwarded_for": forwarded_for, "port": context.data}
 

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


app2 = FastAPI(title="Auth")


 

@app2.get("/auth", summary="Test endpoint")
def default():
    headers = {"Content-Type": "text/plain"}
    return 'test'

#creates an access token test, returns json
@app.post("/auth/token", summary="Test endpoint")
def create_token(response: Response):
    response.headers["Content-Type"] = "application/json"
    return {"access_token": "test"}

@app.post("/api", summary="Reset database")
def reset(response: Response):
    response.headers["x-correlator"] = "235aw-aw33tbwa4t-waw4ue"
    return {"message": "Test api"}

#python -m uvicorn main:app --reload
