import mlflow
import optuna
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

mlflow.set_tracking_uri("sqlite:///mlflow.db")
# 1. MLflow 실험 이름 설정 (마치 폴더 이름 만드는 것과 같습니다)
mlflow.set_experiment("My_First_Automated_Experiment")

def objective(trial):
    # 2. Optuna가 하이퍼파라미터를 제안 (Suggest)
    # 기존에 사람이 수동으로 넣던 숫자를 trial 객체가 대신 골라줍니다.
    n_estimators = trial.suggest_int("n_estimators", 10, 100)
    max_depth = trial.suggest_int("max_depth", 2, 32, log=True)
    
    # 3. 데이터 준비 및 모델 학습
    data = load_wine()
    X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2)
    
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds)
    
    # 4. MLflow에 기록 (이 부분이 핵심입니다!)
    # Optuna의 시도(trial) 한 번마다 MLflow에 기록을 남깁니다.
    with mlflow.start_run(run_name=f"trial_{trial.number}"):
        # A. 내가 설정한 파라미터 기록
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        
        # B. 결과 지표 기록
        mlflow.log_metric("accuracy", accuracy)
        
        # C. 모델 파일 자체를 저장 (선택 사항)
        mlflow.sklearn.log_model(model, "model")
        
    return accuracy

if __name__ == "__main__":
    # 5. Optuna 실행 (최대화 방향, 20번 시도)
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=20)

    print(f"Best trial: {study.best_trial.value}")
    print(f"Best params: {study.best_trial.params}")