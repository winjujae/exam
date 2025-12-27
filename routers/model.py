from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter()

class YieldInput(BaseModel):
    temp: float    # 온도
    press: float   # 압력
    speed: float   # 생산 속도

@router.post("/predict-yield", summary="수율 예측")
def predict_yield(data: YieldInput):
    """
    입력된 공정 변수를 바탕으로 예상 수율(Yield)을 계산합니다.
    통계적 회귀 모델이 이 안에서 작동합니다.
    """
    # 통계적 로직 흉내 (실제로는 여기서 model.predict 실행)
    base_yield = 95.0
    loss = (data.temp * 0.01) + (data.press * 0.05)
    predicted_yield = base_yield - loss + random.uniform(-0.5, 0.5)
    
    return {
        "predicted_yield": round(predicted_yield, 2),
        "unit": "percent",
        "risk_level": "LOW" if predicted_yield > 90 else "HIGH"
    }