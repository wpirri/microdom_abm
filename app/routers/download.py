from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pathlib import Path
from app.log_utils import get_daily_logger

logger = get_daily_logger()

router = APIRouter()

# Directorio donde estarán los archivos a descargar
BASE_DIR = Path("/app/download")  # Cambialo según tu mapeo real

@router.get("/download/{filename}")
def download_file(filename: str, request: Request):
    file_path = BASE_DIR / filename
    raddr = request.client.host

    # Validar existencia
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    logger.info(f"[Download] Raddr: {raddr} Archivo: {file_path}")

    # FastAPI detecta el tipo MIME automáticamente
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
