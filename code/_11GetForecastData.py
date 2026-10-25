import json


def getForecastData(requestedDataType):
    forecastDataFile = "Forecast.json"
    with open(forecastDataFile, "r") as forecastDataRaw:
        forecastData = json.load(forecastDataRaw)
    

    if requestedDataType == "price":
        forecastPriceToReturn = []
        for forecastPrice in forecastData:
                forecastPriceUnpacked = forecastPrice["Fprice"]
                forecastPriceUnpacked *= 0.08
                forecastPriceToReturn.append("%.2f" % forecastPriceUnpacked)
                
        return forecastPriceToReturn


    if requestedDataType == "quantity":
        forecastQuantityToReturn = []
        for forecastQuantity in forecastData:
            forecastQuantityToReturn.append(forecastQuantity["Fquantity"])

        return forecastQuantityToReturn


    if requestedDataType == "date":
        forecastDateToReturn = []
        for forecastDate in forecastData:
            forecastDateToReturn.append(forecastDate["Fweek"])

        return forecastDateToReturn

