from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from config import FRONTEND_URL
from routes import router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Manually handle OPTIONS preflight request
@app.options("/{full_path:path}")
async def preflight_handler(full_path: str, response: Response):
    response.headers["Access-Control-Allow-Origin"] = FRONTEND_URL
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include your routes (in routes.py)
app.include_router(router)