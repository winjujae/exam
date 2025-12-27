from fastapi import FastAPI
from routers import user, model, factory # 1. 각 파일 불러오기

app = FastAPI(
    title="제조 AI 통합 관리 시스템",
    description="통계 기반 수율 예측 및 공정 모니터링 API입니다.",
    version="2.0.0"
)

# 2. 각 라우터를 등록 (prefix로 주소를 구분하고, tags로 문서 그룹화)
app.include_router(user.router, prefix="/user", tags=["사용자 관리"])
app.include_router(model.router, prefix="/model", tags=["AI 예측 모델"])
app.include_router(factory.router, prefix="/factory", tags=["공장 실시간 정보"])

@app.get("/")
def home():
    return {"message": "제조 AI 시스템 서버가 가동 중입니다."}