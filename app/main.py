from fastapi import FastAPI
from app.schemas import PredictRequest, PredictResponse
from app.model_loader import load_model_and_columns
from app.preprocessing import make_feature_row
from app.geo_features import build_balltree_from_csv, count_within_radius_km

app = FastAPI(title="Traffic Accident Risk API")

# 전역으로 로드(서버 시작 시 1번만)
MODEL_PATH = "models/lgbm_model.pkl"
COLS_PATH  = "models/feature_columns.pkl"

CAMERA_CSV = "data/rawdata/전국무인교통단속카메라표준데이터.csv"
SCHOOL_CSV = "data/rawdata/재단법인한국지방교육행정연구재단_초중등학교위치.csv"
SIGN_CSV   = "data/rawdata/전국가변전광표지판_안내전광판_표준데이터.csv"

model = None
feature_columns = None

camera_tree = None
school_tree = None
sign_tree = None

@app.on_event("startup")
def startup():
    global model, feature_columns
    global camera_tree, school_tree, sign_tree

    model, feature_columns = load_model_and_columns(MODEL_PATH, COLS_PATH)

    # csv 컬럼명은 네 데이터 실제 컬럼에 맞춰야 함.
    # 노트북에선 camera['위도'], camera['경도']로 썼으니 일단 그걸 가정.
    camera_tree = build_balltree_from_csv(CAMERA_CSV, lat_col="위도", lon_col="경도", encoding="cp949")
    sign_tree   = build_balltree_from_csv(SIGN_CSV,   lat_col="위도", lon_col="경도", encoding="cp949")

    # 학교 파일은 encoding이 다를 수 있어서(노트북에선 encoding 미지정) 일단 기본으로
    # 만약 깨지면 encoding="cp949"로 바꾸면 됨.
    school_tree = build_balltree_from_csv(SCHOOL_CSV, lat_col="위도", lon_col="경도")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    lat = req.위도
    lon = req.경도
    if req.요일 not in ["월요일","화요일","수요일","목요일","금요일","토요일","일요일"]:
        raise ValueError("잘못된 요일")

    # 500m 반경 시설 수 계산
    cam_n = count_within_radius_km(camera_tree, lat, lon, radius_km=0.5)
    sch_n = count_within_radius_km(school_tree, lat, lon, radius_km=0.5)
    sig_n = count_within_radius_km(sign_tree,   lat, lon, radius_km=0.5)

    raw = req.model_dump()
    raw["반경500m카메라수"] = cam_n
    raw["반경500m학교수"] = sch_n
    raw["반경500m전광판수"] = sig_n

    X = make_feature_row(raw, feature_columns)
    pred = float(model.predict(X)[0])

    return PredictResponse(
        predicted_반경500m사고건수=pred,
        used_features={
            "반경500m카메라수": cam_n,
            "반경500m학교수": sch_n,
            "반경500m전광판수": sig_n,
        },
    )