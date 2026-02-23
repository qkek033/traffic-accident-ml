import pandas as pd

CAT_COLS = [
    '요일','발생지시도','사고유형_대분류','도로형태_대분류','가해자_당사자종별','피해자_당사자종별','주야'
]
NUM_COLS = [
    '발생년','발생월','발생일','발생시','경도','위도','사상자수',
    '반경500m카메라수','반경500m학교수','반경500m전광판수'
]

def make_feature_row(raw: dict, feature_columns: list[str]) -> pd.DataFrame:
    """
    raw: 요청값 + (반경500m카메라수/학교수/전광판수)까지 포함된 dict
    feature_columns: 학습 때 저장해둔 X.columns
    """
    df = pd.DataFrame([raw])

    X_cat = pd.get_dummies(df[CAT_COLS], drop_first=False)
    X_num = df[NUM_COLS].copy()
    X = pd.concat([X_cat, X_num], axis=1)

    # 학습 컬럼에 맞춰서 없는 컬럼은 0으로 채우고, 순서도 동일하게 맞춤
    X = X.reindex(columns=feature_columns, fill_value=0)
    return X