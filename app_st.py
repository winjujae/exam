import streamlit as st
import pandas as pd
import random
import os

# --- [재학습을 위한 데이터 저장 함수] ---
def save_data(temp, humid, prediction):
    file_name = "factory_logs.csv"
    new_data = {"temp": temp, "humid": humid, "pred": prediction}
    df = pd.DataFrame([new_data])
    
    # 파일이 없으면 만들고, 있으면 추가
    if not os.path.isfile(file_name):
        df.to_csv(file_name, index=False)
    else:
        df.to_csv(file_name, mode='a', header=False, index=False)

# --- [화면 구성] ---
st.title("🏭 제조 수율 예측 및 데이터 수집기")

temp = st.slider("현재 공정 온도", 0, 100, 50)
humid = st.slider("현재 공정 습도", 0, 100, 50)

if st.button("수율 예측하기"):
    # 1. 원래 FastAPI에 있던 로직을 여기서 직접 수행 (requests.post 필요 없음!)
    # 실제 모델이 있다면 여기서 model.predict() 수행
    prediction = (temp * 0.7) + (humid * 0.3) + random.uniform(-2, 2)
    
    # 2. 결과 출력
    st.success(f"예측 수율: {prediction:.2f}%")
    
    # 3. [핵심] 재학습을 위한 데이터 로깅
    save_data(temp, humid, prediction)
    st.info("데이터가 'factory_logs.csv'에 저장되었습니다.")

# --- [재학습용 데이터 확인 섹션] ---
if st.checkbox("누적 데이터 확인하기"):
    if os.path.exists("factory_logs.csv"):
        logs = pd.read_csv("factory_logs.csv")
        st.write(f"현재 수집된 데이터 수: {len(logs)}건")
        st.dataframe(logs.tail(10)) # 최근 10건만 보기
    else:
        st.warning("아직 수집된 데이터가 없습니다.")