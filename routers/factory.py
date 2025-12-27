from fastapi import APIRouter

router = APIRouter()

@router.get("/machines", summary="설비 리스트 조회")
def list_machines():
    return [
        {"id": "M-01", "name": "에칭 챔버", "status": "Stable"},
        {"id": "M-02", "name": "세정 장비", "status": "Maintenance"},
        {"id": "M-03", "name": "증착 장비", "status": "Stable"}
    ]

@router.get("/alerts", summary="이상 징후 로그")
def get_alerts():
    return [
        {"time": "2025-05-20 14:05", "msg": "M-02 설비 진동 수치 임계점 초과"},
        {"time": "2025-05-20 15:10", "msg": "라인 3번 온도 급상승"}
    ]