from openpyxl import load_workbook      # module/library for dealing with spreadsheets

def getHistoricData(requestedDataType):
    # get stuff from spreadsheet
    dataSet = "data\Salmon_data.xlsx"
    workbook = load_workbook(dataSet)
    worksheet = workbook["Vekt"]

    # Return the list of dates
    if requestedDataType == "date":
        dateList = []
        for dateRow in worksheet:
            date = dateRow[1].value
            if date == None:
                pass
            else:
                dateList.append(date)

        return dateList
    

    # return the list of prices in GBP, converted from NOK. Screw you, Norwegian Krone.
    if requestedDataType == "price":
        priceList = []
        for priceRow in worksheet:
            price = priceRow[3].value
            if price == None:
                pass
            elif price == "Price per kg (NOK)":
                pass
            else:
                price *= 0.08
                priceList.append("%.2f" % price)

        return priceList


    # return the list of quantity
    if requestedDataType == "quantity":
        quantityList = []
        for quantityRow in worksheet:
            quantity = quantityRow[2].value
            if quantity == "Weight (tonnes)":
                pass
            elif quantity != None:
                quantityList.append(quantity)
            else:
                pass
        
        return quantityList

