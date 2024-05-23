from fastapi import APIRouter
from .convert_router import router as convertfile

router = APIRouter()
router.include_router(convertfile, prefix="/convertfile")
