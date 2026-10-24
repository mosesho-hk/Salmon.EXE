# Salmon.EXE

Small Python prototype based on the price and quantity notebooks.

Install dependencies, train both models, save them with joblib, and print a
JSON forecast for the next 52 weeks after the final observation in the Excel file:

```bash
python -m pip install -r requirements.txt
python webui/models.py --train
```

Run predictions again using the saved models without retraining:

```bash
python webui/models.py
```

Or call the functions from Python:

```python
from webui.models import train_and_save_models, print_predictions

train_and_save_models()  # Creates models/price_model.joblib and quantity_model.joblib
predictions = print_predictions()  # Prints JSON and returns a list of 52 dictionaries
```

Each JSON item has `Fprice` (NOK/kg), `Fquantity` (tonnes), and `Fweek`
(the week's Monday as `YYYY-MM-DD`). For example, the first item is:

```json
{"Fprice": 73.13, "Fquantity": 757.25, "Fweek": "2026-10-12"}
```

`predict_next_year()` returns the list without printing. Forecasting starts after
the last data week, rather than at the current date or the next calendar year.
Later weeks use earlier predicted prices and quantities as history; this is a
recursive forecast, so errors can accumulate over the 52 weeks.

Both commands accept `--data path/to/Salmon_data.xlsx` and `--model-dir path/to/models`.
The input uses the notebooks' `Vekt` worksheet layout. Prediction needs complete
price and volume observations for the last four consecutive weeks.

The prototype uses the notebooks' XGBoost price-change features and LightGBM
quantity features. It chooses LightGBM's tree count using chronological
validation, then fits both final models on all available history for forecasting.
These final fits are not held-out accuracy evaluations. Quantity means weekly
export volume, not inventory. Only load joblib files you trust, and use the same
dependency versions for training and loading.

Run the combined forecasting and purchasing demo with:

```bash
python -m pip install -r requirements.txt
python test.py
```

With the existing Windows virtual environment, use
`.\.venv\Scripts\python.exe test.py`.

`test.py` retrains and saves both models, writes the 52-week forecast to
`forecast.json`, and prints it. It then reads that JSON and calls
`optimize_forecast_json()` to find a purchasing schedule using:

- `Fprice` as the price in NOK/kg.
- `Fquantity` multiplied by 1,000 to convert tonnes to kilograms.
- `Fweek` as the purchase week's date.

The example buyer requirements are a NOK 10,000 budget, 100 kg demand, and a
52-week deadline. Edit these arguments in `test.py` to try different scenarios.
Each optimizer time step represents a week; its existing `deadline_days` argument
receives the number of weeks from the adapter. Optional `period_labels` preserve
the forecast dates in the returned schedule.

To optimize an existing JSON forecast without retraining:

```python
from pathlib import Path
from test import optimize_forecast_json

schedule = optimize_forecast_json(
    Path("forecast.json").read_text(encoding="utf-8"),
    maximum_budget=10000.0,
    buyer_demand_kg=100.0,
    deadline_weeks=52,
)
print(schedule)
```

Expected optimization output:

```text
Optimized purchase schedule (forecast data):
Week starting 2026-12-14: buy 100.00 kg for NOK 7231.00
Total quantity: 100.00 kg
Total cost: NOK 7231.00
```

The optimizer returns `(week_date, budget_allocated_nok, quantity_kg)` tuples and uses
PuLP with HiGHS, installed by `requirements.txt`. It raises `ValueError` if the
budget or stock cannot meet demand. For this prototype, forecast export volume
is treated as purchasable stock; it is not confirmed supplier inventory. The combined demo
prints both JSON and schedule text; use `python webui/models.py` for JSON-only output.
