# app_st.py
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.title("🏭 제조 공정 수율 예측 대시보드")
st.write("설비 데이터를 입력하면 AI 모델이 수율을 예측합니다.")

# 1. 사이드바에서 입력 받기
st.sidebar.header("입력 파라미터")
temp = st.sidebar.slider("온도 (Temperature)", 0.0, 100.0, 50.0)
humid = st.sidebar.slider("습도 (Humidity)", 0.0, 100.0, 50.0)

# 2. 버튼을 누르면 FastAPI 호출
if st.button("예측 시작"):
    # FastAPI 주소 (WSL 사용 시 127.0.0.1)
    url = "http://127.0.0.1:8000/predict"
    data = {"temperature": temp, "humidity": humid}
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        prediction = result["prediction"]
        
        # 3. 결과 화면에 표시
        st.success(f"예상 수율: {prediction} {result['unit']}")
        
        # 4. 통계학 전공자다운 시각화 추가
        st.subheader("예측 분석 그래프")
        df = pd.DataFrame({
            "항목": ["기준 수율", "예측 수율"],
            "값": [90.0, prediction]
        })
        
        fig, ax = plt.subplots()
        ax.bar(df["항목"], df["값"], color=['gray', 'skyblue'])
        ax.set_ylim(0, 110)
        st.pyplot(fig)
    else:
        st.error("FastAPI 서버와 통신에 실패했습니다.")