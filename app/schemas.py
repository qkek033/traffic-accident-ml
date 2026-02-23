from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    # 범주형(학습에 썼던 것들)
    요일: str
    발생지시도: str
    사고유형_대분류: str
    도로형태_대분류: str
    가해자_당사자종별: str
    피해자_당사자종별: str
    주야: str

    # 수치형
    발생년: int = Field(..., ge=1900, le=2100)
    발생월: int = Field(..., ge=1, le=12)
    발생일: int = Field(..., ge=1, le=31)
    발생시: int = Field(..., ge=0, le=23)
    경도: float
    위도: float
    사상자수: float = Field(..., ge=0)

class PredictResponse(BaseModel):
    predicted_반경500m사고건수: float
    used_features: dict  # 디버깅/검증용(나중에 빼도 됨)