import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

EARTH_RADIUS_KM = 6371.0088

def _to_radians(lat_series, lon_series):
    lat = np.asarray(lat_series, dtype=float)
    lon = np.asarray(lon_series, dtype=float)
    return np.deg2rad(np.c_[lat, lon])

def build_balltree_from_csv(path: str, lat_col: str, lon_col: str, encoding: str | None = None):
    df = pd.read_csv(path, encoding=encoding) if encoding else pd.read_csv(path)
    # 🔥 추가 (이게 핵심)
    df = df[[lat_col, lon_col]].dropna()
    df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
    df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
    df = df.dropna()
    coords_rad = _to_radians(df[lat_col], df[lon_col])
    tree = BallTree(coords_rad, metric="haversine")
    return tree

def count_within_radius_km(tree: BallTree, lat: float, lon: float, radius_km: float) -> int:
    # BallTree haversine은 “라디안 거리”라서 km -> 라디안 변환 필요
    radius_rad = radius_km / EARTH_RADIUS_KM
    point = _to_radians([lat], [lon])
    ind = tree.query_radius(point, r=radius_rad, return_distance=False)
    return int(len(ind[0]))