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
