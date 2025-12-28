import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import os
import datetime

# 1. 초기 설정: 모델 파일과 데이터 로그 파일 경로
MODEL_PATH = "model.pkl"
LOG_PATH = "factory_logs.csv"

# --- [함수: 모델 로드 및 초기화] ---
def load_or_init_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    else:
        # 모델이 없으면 아주 기초적인 선형 회귀 모델 생성 (초기값)
        model = LinearRegression()
        # 가상의 초기 데이터로 학습
        X_init = np.array([[50, 50], [60, 40], [70, 30]])
        y_init = np.array([75, 80, 85])
        model.fit(X_init, y_init)
        joblib.dump(model, MODEL_PATH)
        return model

# --- [함수: 데이터 재학습 로직] ---
def retrain_model():
    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)
        if len(df) >= 5:  # 데이터가 최소 5건 이상 쌓였을 때 재학습 (테스트용)
            X = df[['temp', 'humid']]
            # 실무에서는 '실제 수율' 데이터가 필요하지만, 
            # 여기서는 MLOps 흐름을 위해 예측값에 노이즈를 섞어 실제값인 척 시뮬레이션합니다.
            y = df['pred'] + np.random.normal(0, 1, len(df)) 
            
            new_model = LinearRegression()
            new_model.fit(X, y)
            joblib.dump(new_model, MODEL_PATH)
            return True
    return False

# --- [UI 구성: 사이드바] ---
st.sidebar.header("📊 공정 파라미터 입력")
temp = st.sidebar.slider("온도 (Temperature)", 0, 100, 60)
humid = st.sidebar.slider("습도 (Humidity)", 0, 100, 40)
predict_btn = st.sidebar.button("수율 예측 실행")

# --- [메인 화면] ---
st.title("🏭 MLOps 자가 진화형 수율 예측 시스템")
model = load_or_init_model()

if predict_btn:
    # 1. 추론 (Inference)
    input_data = np.array([[temp, humid]])
    prediction = model.predict(input_data)[0]
    
    st.metric(label="예상 수율", value=f"{prediction:.2f} %")
    
    # 2. 데이터 로깅 (MLOps의 시작)
    new_log = pd.DataFrame({
        "timestamp": [datetime.datetime.now()],
        "temp": [temp],
        "humid": [humid],
        "pred": [prediction]
    })
    
    if not os.path.exists(LOG_PATH):
        new_log.to_csv(LOG_PATH, index=False)
    else:
        new_log.to_csv(LOG_PATH, mode='a', header=False, index=False)
    
    st.info("💡 입력 데이터가 로그에 기록되었습니다.")

# --- [MLOps 관리 섹션] ---
st.divider()
st.subheader("🛠️ 모델 관리 및 재학습")

if os.path.exists(LOG_PATH):
    logs = pd.read_csv(LOG_PATH)
    st.write(f"현재 수집된 데이터: **{len(logs)}** 건")
    
    if st.button("🔄 현재 데이터로 모델 재학습"):
        if retrain_model():
            st.success("✅ 재학습이 완료되었습니다! 모델이 업데이트되었습니다.")
            st.rerun() # 화면 새로고침하여 새 모델 반영
        else:
            st.warning("재학습을 위한 데이터가 부족합니다. (최소 5건 필요)")

    with st.expander("데이터 로그 보기"):
        st.dataframe(logs.tail(10))