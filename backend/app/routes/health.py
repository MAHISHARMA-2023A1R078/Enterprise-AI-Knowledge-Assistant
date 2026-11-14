
from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Enterprise AI Knowledge Assistant backend is running"
    }


@router.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
