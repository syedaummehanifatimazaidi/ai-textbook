from fastapi import APIRouter, Response
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check called")
    return {
        "status": "ok",
        "service": "robotics-textbook-api",
    }

@router.get("/ready", response_model=dict)
async def readiness_check():
    """Readiness check endpoint for K8s/orchestration"""
    logger.debug("Readiness check called")
    return {
        "status": "ready",
        "service": "robotics-textbook-api",
    }
