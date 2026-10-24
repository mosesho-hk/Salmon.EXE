import json
from pathlib import Path

from optimisation.optimise_algo import optimize_purchasing_schedule
from webui.models import train_and_save_models, predict_next_year


def optimize_forecast_json(forecast_json, maximum_budget, buyer_demand_kg, deadline_weeks):
    """Optimize weekly forecast JSON using NOK and kilograms."""
    forecasts = json.loads(forecast_json)
    return optimize_purchasing_schedule(
        maximum_budget=maximum_budget,
        buyer_demand_kg=buyer_demand_kg,
        # The optimizer treats each array entry as one time step, here a week.
        deadline_days=deadline_weeks,
        supplier_offer_price_kg=[row["Fprice"] for row in forecasts],
        supplier_saleable_stock_kg=[row["Fquantity"] * 1000 for row in forecasts],
        period_labels=[row["Fweek"] for row in forecasts],
    )


def main():
    train_and_save_models()  # Saves both models with joblib.
    forecast_json = json.dumps(predict_next_year(), indent=2, allow_nan=False)
    forecast_path = Path(__file__).resolve().with_name("forecast.json")
    forecast_path.write_text(forecast_json + "\n", encoding="utf-8")
    print(forecast_json)

    # Example buyer requirements; supplier prices and volumes come from the JSON.
    schedule = optimize_forecast_json(
        forecast_path.read_text(encoding="utf-8"),
        maximum_budget=10000.0,  # NOK, matching the forecast currency.
        buyer_demand_kg=100.0,
        deadline_weeks=52,
    )

    print("\nOptimized purchase schedule (forecast data):")
    for week, budget, quantity in schedule:
        print(f"Week starting {week}: buy {quantity:.2f} kg for NOK {budget:.2f}")
    print(f"Total quantity: {sum(row[2] for row in schedule):.2f} kg")
    print(f"Total cost: NOK {sum(row[1] for row in schedule):.2f}")


if __name__ == "__main__":
    main()
