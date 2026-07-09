from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status": "Healthy",
        "service": "LeadScout AI"
    }