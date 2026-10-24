"""Train, save, and run the salmon notebook models locally."""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "Salmon_data.xlsx"
DEFAULT_MODELS = ROOT / "models"
PRICE_FEATURES = [
    "price_lag_1", "price_lag_2", "price_lag_4",
    "price_change_lag_1", "price_change_lag_2", "price_volatility_4",
    "volume_lag_1", "week_sin", "week_cos",
]
QUANTITY_FEATURES = [
    "volume_lag_1", "volume_lag_2", "volume_lag_4", "volume_mean_4",
    "volume_std_4", "price_lag_1", "week_sin", "week_cos",
]


def load_data(path=DEFAULT_DATA):
    """Read the notebooks' Vekt worksheet as a regular weekly history."""
    raw = pd.read_excel(path, sheet_name="Vekt", header=None, engine="openpyxl")
    rows = raw[1].astype(str).str.fullmatch(r"\d{4}U\d{2}")
    data = raw.loc[rows, [1, 2, 3]].copy()
    data.columns = ["week", "volume_tonnes", "price_nok_kg"]
    if data.empty:
        raise ValueError("No weekly observations found in the Vekt worksheet.")
    data.index = pd.DatetimeIndex([
        date.fromisocalendar(int(w[:4]), int(w[5:]), 1) for w in data.pop("week")
    ], name="date")
    if data.index.duplicated().any():
        raise ValueError("Duplicate weeks found in the input data.")
    return data.apply(pd.to_numeric, errors="coerce").sort_index().asfreq("W-MON")


def build_features(data):
    """Use only earlier weeks to construct each target week's features."""
    price = pd.DataFrame(index=data.index)
    quantity = pd.DataFrame(index=data.index)
    for lag in (1, 2, 4):
        price[f"price_lag_{lag}"] = data.price_nok_kg.shift(lag)
        quantity[f"volume_lag_{lag}"] = data.volume_tonnes.shift(lag)
    price["price_change_lag_1"] = data.price_nok_kg.diff().shift(1)
    price["price_change_lag_2"] = data.price_nok_kg.diff().shift(2)
    price["price_volatility_4"] = data.price_nok_kg.shift(1).rolling(4).std()
    price["volume_lag_1"] = data.volume_tonnes.shift(1)
    quantity["volume_mean_4"] = data.volume_tonnes.shift(1).rolling(4).mean()
    quantity["volume_std_4"] = data.volume_tonnes.shift(1).rolling(4).std()
    quantity["price_lag_1"] = data.price_nok_kg.shift(1)
    weeks = data.index.isocalendar().week.astype(int)
    for frame, period in ((price, 52.18), (quantity, 52.1775)):
        frame["week_sin"] = np.sin(2 * np.pi * weeks / period)
        frame["week_cos"] = np.cos(2 * np.pi * weeks / period)
    return price[PRICE_FEATURES], quantity[QUANTITY_FEATURES]


def train_and_save_models(data_path=DEFAULT_DATA, model_dir=DEFAULT_MODELS):
    """Fit notebook models and save both estimators using joblib."""
    data = load_data(data_path)
    price_x, quantity_x = build_features(data)
    price_y = data.price_nok_kg.diff()
    price_ok = price_x.notna().all(axis=1) & price_y.notna()
    quantity_ok = quantity_x.notna().all(axis=1) & data.volume_tonnes.notna()
    price_x, price_y = price_x.loc[price_ok], price_y.loc[price_ok]
    quantity_x = quantity_x.loc[quantity_ok]
    quantity_y = data.volume_tonnes.loc[quantity_ok]
    if min(len(price_x), len(quantity_x)) < 20:
        raise ValueError("At least 20 usable training rows are required after creating lags.")

    price_model = XGBRegressor(
        n_estimators=150, learning_rate=0.02, max_depth=3,
        subsample=0.8, colsample_bytree=0.8, reg_alpha=0.5,
        reg_lambda=1.5, random_state=42, n_jobs=1,
    )
    price_model.fit(price_x, price_y)
    quantity_options = dict(
        objective="regression", metric="mae", learning_rate=0.03,
        num_leaves=15, max_depth=4, min_child_samples=30,
        reg_lambda=5, verbosity=-1, random_state=42, n_jobs=1,
    )
    # Select tree count on chronological validation, then refit on all history.
    train_end, val_end = int(len(quantity_x) * 0.70), int(len(quantity_x) * 0.85)
    candidate = lgb.LGBMRegressor(n_estimators=2000, **quantity_options)
    candidate.fit(
        quantity_x.iloc[:train_end], quantity_y.iloc[:train_end],
        eval_set=[(quantity_x.iloc[train_end:val_end], quantity_y.iloc[train_end:val_end])],
        callbacks=[lgb.early_stopping(50, verbose=False)],
    )
    quantity_model = lgb.LGBMRegressor(
        n_estimators=candidate.best_iteration_, **quantity_options
    )
    quantity_model.fit(quantity_x, quantity_y)
    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(price_model, model_dir / "price_model.joblib")
    joblib.dump(quantity_model, model_dir / "quantity_model.joblib")
    return price_model, quantity_model


def load_models(model_dir=DEFAULT_MODELS):
    """Load trusted model files previously created by train_and_save_models."""
    model_dir = Path(model_dir)
    return (
        joblib.load(model_dir / "price_model.joblib"),
        joblib.load(model_dir / "quantity_model.joblib"),
    )


def _predict_week(data, price_model, quantity_model):
    """Predict the week immediately after the supplied history."""
    next_week = data.index.max() + pd.Timedelta(weeks=1)
    extended = data.reindex(data.index.append(pd.DatetimeIndex([next_week])))
    price_x, quantity_x = build_features(extended)
    price_x, quantity_x = price_x.tail(1), quantity_x.tail(1)
    if price_x.isna().any().any() or quantity_x.isna().any().any():
        raise ValueError("Prediction requires complete price and volume data for the last four weeks.")
    # The price model predicts a change, so restore the absolute price.
    price = float(price_x["price_lag_1"].iloc[0] + price_model.predict(price_x)[0])
    quantity = float(quantity_model.predict(quantity_x)[0])
    if not np.isfinite([price, quantity]).all():
        raise ValueError("Models produced a non-finite forecast.")
    quantity = max(0.0, quantity)
    return {"week": next_week.date().isoformat(), "price_nok_kg": price, "volume_tonnes": quantity}


def predict_next_week(data_path=DEFAULT_DATA, model_dir=DEFAULT_MODELS):
    """Return one week's price (NOK/kg) and export quantity (tonnes)."""
    return _predict_week(load_data(data_path), *load_models(model_dir))


def predict_next_year(data_path=DEFAULT_DATA, model_dir=DEFAULT_MODELS):
    """Return 52 weekly forecasts after the final observation, recursively."""
    history = load_data(data_path)
    price_model, quantity_model = load_models(model_dir)
    forecasts = []
    for _ in range(52):
        result = _predict_week(history, price_model, quantity_model)
        forecasts.append({
            "Fprice": round(result["price_nok_kg"], 2),
            "Fquantity": round(result["volume_tonnes"], 2),
            "Fweek": result["week"],
        })
        # Feed both forecasts back into history at full precision for later lags.
        history.loc[pd.Timestamp(result["week"]), ["price_nok_kg", "volume_tonnes"]] = [
            result["price_nok_kg"], result["volume_tonnes"],
        ]
    return forecasts


def print_predictions(data_path=DEFAULT_DATA, model_dir=DEFAULT_MODELS):
    """Print a JSON array of 52 forecasts and return the same list."""
    result = predict_next_year(data_path, model_dir)
    print(json.dumps(result, indent=2, allow_nan=False))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", action="store_true", help="Train and save models before predicting")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODELS)
    args = parser.parse_args()
    if args.train:
        train_and_save_models(args.data, args.model_dir)
        print(f"Saved models to {args.model_dir}", file=sys.stderr)
    print_predictions(args.data, args.model_dir)
