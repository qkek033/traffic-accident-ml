import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

# ------------------------
# 🎨 CSS (핵심🔥)
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
st.title("🚗 교통사고 위험 분석 대시보드")
st.caption("AI 기반 사고 위험도 + 공간 분석")

# ------------------------
# 레이아웃
# ------------------------
col1, col2 = st.columns([1, 2])

# ======================
# 👉 좌측 입력
# ======================
with col1:
    st.markdown("### 📍 위치 입력")

    # 기본값
    if "lat" not in st.session_state:
        st.session_state["lat"] = 35.69368672
    if "lon" not in st.session_state:
        st.session_state["lon"] = 128.4698345

    위도 = st.number_input("위도", value=st.session_state["lat"])
    경도 = st.number_input("경도", value=st.session_state["lon"])

    st.markdown("👉 지도 클릭으로 자동 입력 가능")

    st.markdown("---")

    if st.button("🚀 분석 시작", use_container_width=True):
        st.session_state["run"] = True

# ======================
# 👉 우측 결과
# ======================
with col2:

    if "run" in st.session_state:

        url = "http://127.0.0.1:8000/predict"

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
            "사상자수": 0.3
        }

        res = requests.post(url, json=payload)
        result = res.json()

        pred = result["predicted_반경500m사고건수"]
        is_in = result["is_in_hotspot_500m"]
        dist = result["nearest_hotspot_distance_m"]

        # ------------------------
        # 🎨 위험도 판단
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
        # 🔥 상단 KPI 카드
        # ------------------------
        st.markdown("### 📊 핵심 지표")

        c1, c2, c3 = st.columns(3)

        c1.metric("사고 위험 점수", f"{pred:.2f}")
        c2.metric("위험 등급", label)
        c3.metric("최근접 거리(m)", f"{dist:.0f}")

        # ------------------------
        # 🚦 위험도 바 (핵심🔥)
        # ------------------------
        st.markdown("### 🚦 위험도 시각화")

        st.progress(min(pred / 2, 1.0))

        # ------------------------
        # 📍 사고다발구역 상태
        # ------------------------
        st.markdown("### 📍 사고다발구역 여부")

        if is_in:
            st.error("🚨 사고다발구역 포함")
        else:
            st.success("🟢 안전 지역")

        # ------------------------
        # 🚨 사고 정보 카드
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
            <div class="small">사망자수</div>
        </div>
        """, unsafe_allow_html=True)

        # ------------------------
        # 🗺️ 지도
        # ------------------------
        st.markdown("### 🗺️ 위치 분석 (클릭 가능)")

        m = folium.Map(location=[위도, 경도], zoom_start=15)

        # 클릭 이벤트 받기
        map_data = st_folium(m, width=1000, height=400)

        # 👉 클릭하면 좌표 저장
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