#  Traffic Accident Risk Prediction Service
> 위치 기반 데이터를 활용해 교통사고 위험도를 예측하고, 지도 인터랙션을 통해 직관적으로 분석할 수 있는 ML 기반 서비스입니다. 
> (FastAPI + Streamlit + ML)

---

##  Overview
본 프로젝트는 교통사고 데이터를 기반으로 특정 위치의 사고 위험도를 예측하고,
주변 환경 및 공간 정보를 결합하여 직관적인 시각화까지 제공하는 서비스입니다.

단순 모델링을 넘어서,
- FastAPI를 활용한 모델 서빙
- BallTree 기반 공간 Feature 엔지니어링
- Streamlit + 지도 인터랙션 UI
까지 포함한 **End-to-End ML 서비스 구조**를 직접 구현했습니다.
---

##  Features

- **위치 기반 사고 위험 예측**
- **지도 클릭 인터랙션**
- **위험도 시각화 (KPI + Progress Bar)**
- **사고다발구역 포함 여부 판단**
- **주변 시설 기반 Feature 반영**
- **ML 모델 기반 예측 (LightGBM)**
- **실제 사고 데이터 기반 최근 사고 정보 제공**

---

##  Tech Stack

| Category | Stack |
|--------|------|
| Backend | FastAPI |
| Frontend | Streamlit |
| ML | LightGBM |
| Data | Pandas, Numpy |
| Geo | BallTree (Haversine) |
| Visualization | Folium |

---

##  Architecture

```plaintext
User (Streamlit UI)
        ↓
FastAPI Server (Prediction API)
        ↓
ML Model (LightGBM)
        ↓
Geo Feature Engineering (BallTree)
        ↓
Accident Data (CSV)