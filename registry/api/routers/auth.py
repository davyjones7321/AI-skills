from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
def login():
    return {"message": "Login logic pending GitHub OAuth implementation"}

@router.get("/callback")
def callback():
    return {"message": "Callback logic pending GitHub OAuth implementation"}
