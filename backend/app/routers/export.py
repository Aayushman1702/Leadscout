import os

from fastapi import APIRouter, HTTPException
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from app.exporters.excel_exporter import create_businesses_excel
from app.schemas.export import ExportRequest

router = APIRouter()


@router.post("/export")
async def export_businesses(data: ExportRequest):
    if not data.businesses:
        raise HTTPException(status_code=400, detail="No businesses selected for export")

    file_path, filename = create_businesses_excel(data.businesses)
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
        background=BackgroundTask(os.remove, file_path),
    )
