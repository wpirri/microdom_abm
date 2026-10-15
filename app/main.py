from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.log_utils import get_daily_logger
from app.worker import worker_loop
import asyncio

from app.routers import download, abm

app = FastAPI(
    title="Microservicio administración de sistema de domotica",
    version="1.0.0"
)

logger = get_daily_logger()

# Routers existentes
app.include_router(download.router)
app.include_router(abm.router)

# Archivos estáticos específicos
app.mount("/css", StaticFiles(directory="/app/html/css"), name="css")
app.mount("/js", StaticFiles(directory="/app/html/js"), name="js")
app.mount("/images", StaticFiles(directory="/app/html/images"), name="images")

BASE_DIR = Path("/app/html")  # Cambialo según tu mapeo real

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(worker_loop())

@app.post("/update_form.html")
def update_form():
    raise HTTPException(status_code=404, detail="Funcionalidad no implementada")

@app.get("/", response_class=HTMLResponse)
def index():
    file_path = BASE_DIR / "index.html"
    # Validar existencia
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path)

@app.get("/{filename}", response_class=HTMLResponse)
def root(filename: str):
    file_path = BASE_DIR / filename
    if filename == "m":
        file_path = BASE_DIR / "m" / "index.html"
    # Validar existencia
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path)

@app.get("/data/{filename}", response_class=HTMLResponse)
def root_data(filename: str):
    file_path = BASE_DIR / "data" / filename
    # Validar existencia
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path)

# Movil
@app.get("/m/", response_class=HTMLResponse)
def index():
    file_path = BASE_DIR / "m" / "index.html"
    # Validar existencia
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path)

@app.get("/m/{filename}", response_class=HTMLResponse)
def root(filename: str):
    file_path = BASE_DIR / "m" / filename
    # Validar existencia
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path)
        