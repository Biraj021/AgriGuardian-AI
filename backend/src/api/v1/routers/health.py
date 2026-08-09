from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["health"]) 
def health():
    return {"status": "ok"}
