import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

EARTH_RADIUS_KM = 6371.0088

def build_balltree_from_csv(csv_path: str, lat_col: str, lon_col: str, encoding: str = "utf-8"):
    df = pd.read_csv(csv_path, encoding=encoding, low_memory=False)
    df = df.dropna(subset=[lat_col, lon_col]).copy()
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=[lat_col, lon_col])

    coords_rad = np.deg2rad(df[[lat_col, lon_col]].to_numpy())
    tree = BallTree(coords_rad, metric="haversine")
    return tree, df

def count_within_radius_km(tree: BallTree, lat: float, lon: float, radius_km: float) -> int:
    pt = np.deg2rad([[lat, lon]])
    radius_rad = radius_km / EARTH_RADIUS_KM
    idx = tree.query_radius(pt, r=radius_rad, return_distance=False)
    return int(len(idx[0]))

def nearest_row(tree: BallTree, df: pd.DataFrame, lat: float, lon: float) -> pd.Series:
    pt = np.deg2rad([[lat, lon]])
    dist_rad, ind = tree.query(pt, k=1)
    return df.iloc[int(ind[0][0])]