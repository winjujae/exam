from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/login", summary="엔지니어 로그인")
def login(user: UserLogin):
    # 실제로는 DB 확인 로직이 들어갑니다.
    return {"message": f"{user.username}님, 환영합니다. 공장 관리 시스템에 접속되었습니다."}

@router.get("/me", summary="내 정보 조회")
def get_my_info():
    return {"id": "stat_user_01", "role": "ML Engineer", "dept": "Data Intelligence"}