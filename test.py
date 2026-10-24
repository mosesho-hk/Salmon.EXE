from webui.models import train_and_save_models, print_predictions

train_and_save_models()  # Creates models/price_model.joblib and quantity_model.joblib
prediction = print_predictions()  # Prints price in NOK/kg and quantity in tonnes

print(prediction)  # Prints the dictionary returned by print_predictions

