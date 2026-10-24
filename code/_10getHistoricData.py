from openpyxl import load_workbook      # module/library for dealing with spreadsheets

def getHistoricData(requestedDataType):
    # get stuff from spreadsheet
    dataSet = "Salmon.EXE\data\Salmon_data.xlsx"
    workbook = load_workbook(dataSet)
    worksheet = workbook["Vekt"]


    # return the list of prices
    if requestedDataType == "price":
        priceList = []
        for priceRow in worksheet:
            price = priceRow[3].value
            if price != None:
                price *= 0.08
                priceList.append(price)
            else:
                pass

        return priceList


    # return the list of quantity
    if requestedDataType == "quantity":
        quantityList = []
        for quantityRow in worksheet:
            quantity = quantityRow[2].value
            if quantity != None:
                quantityList.append(quantity)
            else:
                pass
        print(quantityList)
        
        return quantityList

