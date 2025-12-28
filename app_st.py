import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from streamlit_gsheets import GSheetsConnection
import joblib
import os
import datetime
import matplotlib.pyplot as plt

# --- [1. 기본 설정 및 경로] ---
MODEL_PATH = "model.pkl"
PREV_MODEL_PATH = "model_prev.pkl"
# 사용자님의 구글 시트 주소
SHEET_URL = "https://docs.google.com/spreadsheets/d/1EAO3rxueFdQ47atsKhIKET75yyioOFaXaY8c0Mofl-8/edit?gid=0#gid=0"

# --- [2. 모델 초기화 함수] ---
def load_or_init_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    else:
        # 모델이 없으면 기본 모델 생성
        model = LinearRegression()
        X_init = np.array([[50, 50], [60, 40], [70, 30]])
        y_init = np.array([75, 80, 85])
        model.fit(X_init, y_init)
        joblib.dump(model, MODEL_PATH)
        return model

# --- [3. 모델 지표 계산 함수] ---
def calculate_metrics(model, X, y):
    preds = model.predict(X)
    r2 = r2_score(y, preds)
    mse = mean_squared_error(y, preds)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y, preds)
    return {"R2": r2, "MSE": mse, "RMSE": rmse, "MAE": mae}

# --- [4. 재학습 및 시뮬레이션 로직] ---
def retrain_and_compare():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
    
    if df is not None and len(df) >= 10:
        X = df[['temp', 'humid']]
        # 실제 환경을 가정한 정답 데이터 시뮬레이션 (예측값 + 노이즈)
        y = df['pred'] + np.random.normal(0, 1, len(df)) 
        
        current_model = joblib.load(MODEL_PATH)
        joblib.dump(current_model, PREV_MODEL_PATH) 
        old_metrics = calculate_metrics(current_model, X, y)
        
        new_model = LinearRegression()
        new_model.fit(X, y)
        new_metrics = calculate_metrics(new_model, X, y)
        
        joblib.dump(new_model, "model_temp.pkl")
        return old_metrics, new_metrics
    return None, None

# --- [5. UI 구성: 메인 및 사이드바] ---
st.title("🏭 MLOps 자가 진화형 수율 예측 시스템")
model = load_or_init_model()
conn = st.connection("gsheets", type=GSheetsConnection)

# 사이드바 입력창
st.sidebar.header("📥 데이터 주입 (Prediction & Logging)")
temp = st.sidebar.slider("현재 온도", 0, 100, 50)
humid = st.sidebar.slider("현재 습도", 0, 100, 50)
predict_btn = st.sidebar.button("수율 예측 및 시트 기록")

# --- [6. 데이터 주입 로직 실행] ---
if predict_btn:
    # 1. 추론
    input_data = pd.DataFrame([[temp, humid]], columns=['temp', 'humid'])
    prediction = model.predict(input_data)[0]
    
    st.sidebar.success(f"예측 결과: {prediction:.2f}%")
    st.metric(label="실시간 예측 수율", value=f"{prediction:.2f} %")

    # 2. 구글 시트 데이터 주입 (Injection)
    try:
        existing_data = conn.read(spreadsheet=SHEET_URL, ttl=0)
        new_log = pd.DataFrame({
            "timestamp": [str(datetime.datetime.now())],
            "temp": [temp],
            "humid": [humid],
            "pred": [prediction]
        })
        # 기존 시트 데이터에 새 행 추가
        updated_df = pd.concat([existing_data, new_log], ignore_index=True)
        # 시트 업데이트
        conn.update(spreadsheet=SHEET_URL, data=updated_df)
        st.info("✅ 데이터가 구글 시트에 기록되었습니다. (재학습 데이터 확보)")
    except Exception as e:
        st.error(f"시트 기록 중 오류 발생: {e}")

# --- [7. 모델 관리 섹션: 지표 비교 및 교체] ---
st.divider()
st.subheader("📊 모델 성능 비교 및 교체 (Validation)")

if st.button("🔄 수집된 데이터로 성능 시뮬레이션"):
    old_m, new_m = retrain_and_compare()
    if old_m:
        st.session_state['metrics'] = (old_m, new_m)
    else:
        st.warning("재학습을 위한 데이터가 부족합니다 (최소 10건 필요).")

if 'metrics' in st.session_state:
    old_m, new_m = st.session_state['metrics']
    
    # 지표 테이블
    comparison_df = pd.DataFrame([old_m, new_m], index=["이전 모델 (Old)", "신규 모델 (New)"])
    st.table(comparison_df)
    
    # 시각화
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].bar(["Old", "New"], [old_m["R2"], new_m["R2"]], color=['lightgray', 'skyblue'])
    axes[0].set_title("R-Squared (Higher is better)")
    axes[1].bar(["Old", "New"], [old_m["RMSE"], new_m["RMSE"]], color=['lightgray', 'salmon'])
    axes[1].set_title("RMSE (Lower is better)")
    st.pyplot(fig)
    
    # 모델 승인 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 이전 모델 유지"):
            st.warning("이전 모델 환경을 유지합니다.")
            del st.session_state['metrics']
            st.rerun()
    with col2:
        if st.button("✅ 신규 모델 승인"):
            if os.path.exists("model_temp.pkl"):
                new_model = joblib.load("model_temp.pkl")
                joblib.dump(new_model, MODEL_PATH)
                st.success("🎉 신규 모델이 운영 환경에 배포되었습니다!")
                del st.session_state['metrics']
                st.rerun()

# --- [8. 데이터 로그 확인] ---
with st.expander("📝 현재 구글 시트 로그 확인"):
    current_logs = conn.read(spreadsheet=SHEET_URL, ttl=0)
    st.dataframe(current_logs.tail(10))