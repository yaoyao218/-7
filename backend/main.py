from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import router

app = FastAPI(title="Python Judge API", version="1.0.0")

# CORS middleware - allow all for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["judge"])

@app.get("/health")
def health():
    return {"status": "ok"}

app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/index.html")
@app.get("/")
def serve_frontend():
    return FileResponse("../frontend/index.html")
