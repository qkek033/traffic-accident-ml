from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class PredictRequest(BaseModel):
    위도: float
    경도: float

    # (기존에 쓰던 feature들 유지하려면 optional로 두면 됨)
    요일: Optional[str] = None
    발생지시도: Optional[str] = None
    사고유형_대분류: Optional[str] = None
    도로형태_대분류: Optional[str] = None
    가해자_당사자종별: Optional[str] = None
    피해자_당사자종별: Optional[str] = None
    주야: Optional[str] = None
    발생년: Optional[int] = None
    발생월: Optional[int] = None
    발생일: Optional[int] = None
    발생시: Optional[int] = None
    사상자수: Optional[float] = None

class PredictResponse(BaseModel):
    predicted_반경500m사고건수: float
    used_features: Dict[str, Any]

    is_in_hotspot_500m: bool
    nearest_hotspot_distance_m: float
    nearest_hotspot_center: Optional[List[float]] = None  # [lat, lon]

    # ✅ 최근 사고 정보(이제 accident_df.csv 기반으로 내려줄 것)
    최근사고_사고유형: Optional[str] = None
    최근사고_발생시간: Optional[str] = None
    최근사고_사상자수: Optional[float] = None