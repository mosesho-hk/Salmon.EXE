#from webui.models import train_and_save_models, print_predictions

#train_and_save_models()  # Creates models/price_model.joblib and quantity_model.joblib
#prediction = print_predictions()  # Prints price in NOK/kg and quantity in tonnes

#print(prediction)  # Prints the dictionary returned by print_predictions

from pathlib import Path
from optimisation.optimise_engine import optimize_forecast_json

schedule = optimize_forecast_json(
    Path("forecast.json").read_text(encoding="utf-8"),
    maximum_budget=10000.0,
    buyer_demand_kg=100.0,
    deadline_weeks=52,
)
print(schedule)