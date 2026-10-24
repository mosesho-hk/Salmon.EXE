#from webui.models import train_and_save_models, print_predictions

#train_and_save_models()  # Creates models/price_model.joblib and quantity_model.joblib
#prediction = print_predictions()  # Prints price in NOK/kg and quantity in tonnes

#print(prediction)  # Prints the dictionary returned by print_predictions

from pathlib import Path
from optimisation.optimise_engine import optimize_forecast_json

def main():
    forecast_path = Path(__file__).resolve().with_name("forecast.json")
    try:
        schedule = optimize_forecast_json(
            forecast_path.read_text(encoding="utf-8"),
            maximum_budget=1200.0,  # NOK
            buyer_demand_kg=100.0,
            deadline_weeks=3,
        )
    except (ValueError, RuntimeError) as error:
        print(f"Optimization failed for {forecast_path}: {error}")
        return 1
    print(schedule)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
