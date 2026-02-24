from fastapi import FastAPI
import pandas as pd
import numpy as np
from app.schemas import PredictRequest, PredictResponse
from app.model_loader import load_model_and_columns
from app.preprocessing import make_feature_row
from app.geo_features import build_balltree_from_csv, count_within_radius_km, nearest_row

app = FastAPI(title="Traffic Accident Risk API")

MODEL_PATH = "models/lgbm_model.pkl"
COLS_PATH  = "models/feature_columns.pkl"

CAMERA_CSV = "data/rawdata/전국무인교통단속카메라표준데이터.csv"
SCHOOL_CSV = "data/rawdata/재단법인한국지방교육행정연구재단_초중등학교위치.csv"
SIGN_CSV   = "data/rawdata/전국가변전광표지판_안내전광판_표준데이터.csv"

# ✅ 최근 사고정보용 (너가 말한 accident_df.csv)
ACCIDENT_DETAIL_CSV = "data/accident_df.csv"  # ← 네 프로젝트에 이 경로로 두면 됨

model = None
feature_columns = None

camera_tree = None
camera_df = None

school_tree = None
school_df = None

sign_tree = None
sign_df = None

accident_tree = None
accident_detail_df = None


@app.on_event("startup")
def startup():
    global model, feature_columns
    global camera_tree, camera_df
    global school_tree, school_df
    global sign_tree, sign_df
    global accident_tree, accident_detail_df

    model, feature_columns = load_model_and_columns(MODEL_PATH, COLS_PATH)

    camera_tree, camera_df = build_balltree_from_csv(CAMERA_CSV, lat_col="위도", lon_col="경도", encoding="cp949")
    sign_tree,   sign_df   = build_balltree_from_csv(SIGN_CSV,   lat_col="위도", lon_col="경도", encoding="cp949")
    school_tree, school_df = build_balltree_from_csv(SCHOOL_CSV, lat_col="위도", lon_col="경도")  # 필요시 cp949

    # ✅ 최근 사고 상세정보 로드 (발생년/월/일/시, 사상자수 포함)
    accident_tree, accident_detail_df = build_balltree_from_csv(
        ACCIDENT_DETAIL_CSV, lat_col="위도", lon_col="경도", encoding="euc-kr"
    )

    # 컬럼 확인용 (원하면 잠깐 보고 지워도 됨)
    #print("ACCIDENT_DETAIL columns:", accident_detail_df.columns)
    #print(accident_detail_df.columns)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    lat = float(req.위도)
    lon = float(req.경도)

    # 500m 반경 시설 수
    cam_n = count_within_radius_km(camera_tree, lat, lon, radius_km=0.5)
    sch_n = count_within_radius_km(school_tree, lat, lon, radius_km=0.5)
    sig_n = count_within_radius_km(sign_tree,   lat, lon, radius_km=0.5)

    # ✅ 500m 반경 사고 건수도 계산(사고상세 DF 기반)
    acc_n = count_within_radius_km(accident_tree, lat, lon, radius_km=0.5)

    # 모델 입력 row 만들기
    raw = req.model_dump()
    raw["반경500m카메라수"] = cam_n
    raw["반경500m학교수"] = sch_n
    raw["반경500m전광판수"] = sig_n
    raw["반경500m사고건수"] = acc_n  # ← 이 feature를 모델이 쓰고 있다면 매우 중요

    X = make_feature_row(raw, feature_columns)
    pred = float(model.predict(X)[0])

    # ✅ 최근 사고 찾기
    nearest = nearest_row(accident_tree, accident_detail_df, lat, lon)

    # 발생시간 만들기
    try:
        발생시간 = f"{int(nearest['발생년'])}-{int(nearest['발생월'])}-{int(nearest['발생일'])} {int(nearest['발생시'])}시"
    except:
        발생시간 = None

    사고유형 = nearest.get("사고유형_대분류", nearest.get("사고유형", None))
    #사고유형 = str(nearest["사고유형_대분류"]) if "사고유형_대분류" in nearest.index else None

    사상자수 = nearest.get("사상자수", None)
    # hotspot 관련 값은 네 기존 로직을 유지한다고 가정 (여기서는 임시로 “가까운 사고를 hotspot 중심”처럼 보이게 처리)
    # 이미 너 API에 is_in_hotspot_500m / nearest_hotspot_* 계산 로직이 있다면 그걸 그대로 쓰면 됨.
    # 아래는 최소 동작용(500m 내 사고가 있으면 hotspot 포함으로 간주)
    is_in_hotspot = acc_n > 0
    nearest_center = [float(nearest["위도"]), float(nearest["경도"])] if nearest is not None else None

    # 거리(미터) 대충 계산: haversine(라디안) * 지구반지름 * 1000
    if nearest is not None:
        lat1, lon1 = np.deg2rad(lat), np.deg2rad(lon)
        lat2, lon2 = np.deg2rad(float(nearest["위도"])), np.deg2rad(float(nearest["경도"]))
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
        c = 2*np.arcsin(np.sqrt(a))
        dist_m = float(6371008.8 * c)
    else:
        dist_m = 0.0

    return PredictResponse(
        predicted_반경500m사고건수=pred,
        used_features={
            "반경500m카메라수": cam_n,
            "반경500m학교수": sch_n,
            "반경500m전광판수": sig_n,
            "반경500m사고건수": acc_n,
        },
        is_in_hotspot_500m=is_in_hotspot,
        nearest_hotspot_distance_m=dist_m,
        nearest_hotspot_center=nearest_center,

        최근사고_사고유형=사고유형,
        최근사고_발생시간=발생시간,
        최근사고_사상자수=사상자수,
    )