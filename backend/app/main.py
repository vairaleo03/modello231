from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import audio, transcriptions, summaries, onedrive
from app.routers.websocket_manager import router as websocket_router, websocket_manager
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI() 

# ⭐ CORS SEMPLICE MA EFFICACE
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # ⭐ Esponi headers personalizzati
)

# ⭐ MIDDLEWARE SEMPLICE SOLO PER HEADERS
@app.middleware("http")
async def debug_headers_middleware(request, call_next):
    logger.debug(f"🔍 {request.method} {request.url.path}")
    logger.debug(f"🔍 Authorization: {request.headers.get('Authorization', 'None')[:30]}...")
    logger.debug(f"🔍 Custom headers: X-OneDrive-User-ID={request.headers.get('X-OneDrive-User-ID', 'None')}")
    
    response = await call_next(request)
    
    logger.debug(f"📤 Response: {response.status_code}")
    return response

app.include_router(audio.router)
app.include_router(transcriptions.router)
app.include_router(summaries.router)
app.include_router(onedrive.router)
app.include_router(websocket_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "auth_method": "headers_only"}

logger.info("🚀 Modello231 App - Header-based Auth")