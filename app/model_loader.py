import joblib

def load_model_and_columns(model_path: str, columns_path: str):
    model = joblib.load(model_path)
    feature_columns = joblib.load(columns_path)
    return model, feature_columns