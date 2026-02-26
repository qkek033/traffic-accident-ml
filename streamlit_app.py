import os
import sys
import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium
from pathlib import Path

# 프로젝트 루트를 path에 추가 (app 모듈 import용)
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(layout="wide")

# 로컬 예측 사용 시 모델/데이터 경로 (프로젝트 루트 기준)
MODEL_PATH = ROOT / "models" / "lgbm_model.pkl"
COLS_PATH = ROOT / "models" / "feature_columns.pkl"
CAMERA_CSV = ROOT / "data" / "rawdata" / "전국무인교통단속카메라표준데이터.csv"
SCHOOL_CSV = ROOT / "data" / "rawdata" / "재단법인한국지방교육행정연구재단_초중등학교위치.csv"
SIGN_CSV = ROOT / "data" / "rawdata" / "전국가변전광표지판_안내전광판_표준데이터.csv"
ACCIDENT_CSV = ROOT / "data" / "accident_df.csv"


@st.cache_resource
def load_model_and_geo():
    """모델·특성 컬럼·지오 BallTree 한 번만 로드 (캐시)."""
    from app.model_loader import load_model_and_columns
    from app.geo_features import build_balltree_from_csv

    model, feature_columns = load_model_and_columns(str(MODEL_PATH), str(COLS_PATH))
    camera_tree, camera_df = build_balltree_from_csv(str(CAMERA_CSV), lat_col="위도", lon_col="경도", encoding="cp949")
    sign_tree, sign_df = build_balltree_from_csv(str(SIGN_CSV), lat_col="위도", lon_col="경도", encoding="cp949")
    school_tree, school_df = build_balltree_from_csv(str(SCHOOL_CSV), lat_col="위도", lon_col="경도")
    accident_tree, accident_df = build_balltree_from_csv(str(ACCIDENT_CSV), lat_col="위도", lon_col="경도", encoding="euc-kr")
    return {
        "model": model,
        "feature_columns": feature_columns,
        "camera_tree": camera_tree,
        "camera_df": camera_df,
        "school_tree": school_tree,
        "school_df": school_df,
        "sign_tree": sign_tree,
        "sign_df": sign_df,
        "accident_tree": accident_tree,
        "accident_detail_df": accident_df,
    }


def predict_local(payload: dict, resources: dict) -> dict:
    """API 없이 로컬에서 예측 (app/main.py와 동일 로직)."""
    from app.preprocessing import make_feature_row
    from app.geo_features import count_within_radius_km, nearest_row

    lat = float(payload["위도"])
    lon = float(payload["경도"])
    camera_tree = resources["camera_tree"]
    school_tree = resources["school_tree"]
    sign_tree = resources["sign_tree"]
    accident_tree = resources["accident_tree"]
    accident_detail_df = resources["accident_detail_df"]
    model = resources["model"]
    feature_columns = resources["feature_columns"]

    cam_n = count_within_radius_km(camera_tree, lat, lon, radius_km=0.5)
    sch_n = count_within_radius_km(school_tree, lat, lon, radius_km=0.5)
    sig_n = count_within_radius_km(sign_tree, lat, lon, radius_km=0.5)
    acc_n = count_within_radius_km(accident_tree, lat, lon, radius_km=0.5)

    raw = dict(payload)
    raw["반경500m카메라수"] = cam_n
    raw["반경500m학교수"] = sch_n
    raw["반경500m전광판수"] = sig_n
    raw["반경500m사고건수"] = acc_n

    X = make_feature_row(raw, feature_columns)
    pred = float(model.predict(X)[0])
    nearest = nearest_row(accident_tree, accident_detail_df, lat, lon)

    try:
        발생시간 = f"{int(nearest['발생년'])}-{int(nearest['발생월'])}-{int(nearest['발생일'])} {int(nearest['발생시'])}시"
    except Exception:
        발생시간 = None
    사고유형 = nearest.get("사고유형_대분류", nearest.get("사고유형", None))
    사상자수 = nearest.get("사상자수", None)
    is_in_hotspot = acc_n > 0
    nearest_center = [float(nearest["위도"]), float(nearest["경도"])] if nearest is not None else None

    if nearest is not None:
        lat1, lon1 = np.deg2rad(lat), np.deg2rad(lon)
        lat2, lon2 = np.deg2rad(float(nearest["위도"])), np.deg2rad(float(nearest["경도"]))
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        dist_m = float(6371008.8 * c)
    else:
        dist_m = 0.0

    return {
        "predicted_반경500m사고건수": pred,
        "used_features": {"반경500m카메라수": cam_n, "반경500m학교수": sch_n, "반경500m전광판수": sig_n, "반경500m사고건수": acc_n},
        "is_in_hotspot_500m": is_in_hotspot,
        "nearest_hotspot_distance_m": dist_m,
        "nearest_hotspot_center": nearest_center,
        "최근사고_사고유형": 사고유형,
        "최근사고_발생시간": 발생시간,
        "최근사고_사상자수": 사상자수,
    } 

# ------------------------
#  CSS
# ------------------------
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 15px;
    background-color: #1e1e1e;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
}
.metric {
    font-size: 30px;
    font-weight: bold;
}
.small {
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# ------------------------
# 제목
# ------------------------
st.title("교통사고 위험 분석 대시보드")
st.caption("AI 기반 사고 위험도 + 공간 분석")

# ------------------------
# 레이아웃
# ------------------------
col1, col2 = st.columns([1, 2])

# ======================
#  좌측 입력
# ======================
with col1:
    st.markdown("### 위치 입력")

    # 기본값
    if "lat" not in st.session_state:
        st.session_state["lat"] = 35.69368672
    if "lon" not in st.session_state:
        st.session_state["lon"] = 128.4698345

    위도 = st.number_input("위도", value=st.session_state["lat"])
    경도 = st.number_input("경도", value=st.session_state["lon"])

    st.markdown("지도 클릭으로 자동 입력 가능")

    st.markdown("---")

    if st.button("분석 시작", use_container_width=True):
        st.session_state["run"] = True

# ======================
#  우측 결과
# ======================
with col2:

    if "run" in st.session_state:

        payload = {
            "요일": "월요일",
            "발생지시도": "서울",
            "사고유형_대분류": "차대사람",
            "도로형태_대분류": "단일로",
            "가해자_당사자종별": "승용차",
            "피해자_당사자종별": "보행자",
            "주야": "주",
            "발생년": 2023,
            "발생월": 5,
            "발생일": 12,
            "발생시": 14,
            "경도": 경도,
            "위도": 위도,
            "사상자수": 0.3,
        }

        try:
            resources = load_model_and_geo()
            result = predict_local(payload, resources)
        except FileNotFoundError as e:
            st.error(
                "**모델 또는 데이터 파일을 찾을 수 없습니다.**\n\n"
                "다음 경로가 프로젝트 루트 기준으로 존재하는지 확인하세요.\n\n"
                f"• `{MODEL_PATH}`\n• `{COLS_PATH}`\n"
                f"• `{CAMERA_CSV}`\n• `{SCHOOL_CSV}`\n• `{SIGN_CSV}`\n• `{ACCIDENT_CSV}`\n\n"
                f"상세: {e}"
            )
            st.stop()
        except Exception as e:
            st.error(f"예측 중 오류가 발생했습니다: {e}")
            st.stop()

        pred = result["predicted_반경500m사고건수"]
        is_in = result["is_in_hotspot_500m"]
        dist = result["nearest_hotspot_distance_m"]

        # ------------------------
        #  위험도 판단
        # ------------------------
        if pred < 0.5:
            label = "안전"
            color = "green"
        elif pred < 1.0:
            label = "주의"
            color = "orange"
        else:
            label = "위험"
            color = "red"

        # ------------------------
        #  상단 KPI 카드
        # ------------------------
        st.markdown("###  핵심 지표")

        c1, c2, c3 = st.columns(3)

        c1.metric("사고 위험 점수", f"{pred:.2f}")
        c2.metric("위험 등급", label)
        c3.metric("최근접 거리(m)", f"{dist:.0f}")

        # ------------------------
        #  위험도 바 
        # ------------------------
        st.markdown("###  위험도 시각화")

        st.progress(min(pred / 2, 1.0))

        # ------------------------
        #  사고다발구역 상태
        # ------------------------
        st.markdown("###  사고다발구역 여부")

        if is_in:
            st.error("🚨 사고다발구역 포함")
        else:
            st.success("🟢 안전 지역")

        # ------------------------
        #  사고 정보 카드
        # ------------------------
        st.markdown("### 🚨 최근 사고 정보")

        st.markdown(f"""
        <div class="card">
            <div class="metric">{result.get("최근사고_사고유형", "정보없음")}</div>
            <div class="small">사고유형</div>
            <br>
            <div class="metric">{result.get("최근사고_발생시간")}</div>
            <div class="small">발생시간</div>
            <br>
            <div class="metric">{result.get("최근사고_사상자수")}</div>
            <div class="small">사상자수</div>
        </div>
        """, unsafe_allow_html=True)

        # ------------------------
        #  지도
        # ------------------------
        st.markdown("###  위치 분석 (클릭 가능)")

        m = folium.Map(location=[위도, 경도], zoom_start=15)

        # 클릭 이벤트 받기
        map_data = st_folium(m, width=1000, height=400)

        #  클릭하면 좌표 저장
        if map_data and map_data["last_clicked"]:
            lat_clicked = map_data["last_clicked"]["lat"]
            lon_clicked = map_data["last_clicked"]["lng"]

            st.session_state["lat"] = lat_clicked
            st.session_state["lon"] = lon_clicked

            st.rerun()

        # 사용자
        folium.Marker([위도, 경도], icon=folium.Icon(color="blue")).add_to(m)

        center = result.get("nearest_hotspot_center")

        if center:
            h_lat, h_lon = center

            folium.Marker(
                [h_lat, h_lon],
                icon=folium.Icon(color="red")
            ).add_to(m)

            folium.Circle(
                [h_lat, h_lon],
                radius=500,
                color="red",
                fill=True,
                fill_opacity=0.2
            ).add_to(m)

        st_folium(m, width=1000, height=500)