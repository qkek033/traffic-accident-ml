from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import pandas as pd

app = FastAPI(title="Traffic Risk Prediction API")

# 모델 로드
with open("lgbm_model.pkl", "rb") as f:
    model = pickle.load(f)

# feature 컬럼 로드 (입력 순서 고정용)
with open("feature_columns.pkl", "rb") as f:
    feature_columns = pickle.load(f)

class PredictRequest(BaseModel):
    features: dict  # {"주야": 0, "교차로": 1, ...}

@app.get("/")
def health():
    return {
        "status": "ok",
        "n_features": len(feature_columns),
        "message": "Use POST /predict with {'features': {...}}",
    }

@app.post("/predict")
def predict(req: PredictRequest):
    # 1) 요청 dict에서 컬럼 순서대로 값 채우기 (없는 값은 0)
    row = {col: req.features.get(col, 0) for col in feature_columns}

    # 2) 모델 입력 형태로 변환
    X_input = pd.DataFrame([row], columns=feature_columns)

    # 3) 예측
    pred = model.predict(X_input)[0]

    return {"prediction": float(pred)}