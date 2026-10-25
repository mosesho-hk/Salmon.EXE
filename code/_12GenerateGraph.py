import matplotlib.pyplot as pyplot, datetime, numpy, _10GetHistoricData, _11GetForecastData


def generatePriceGraph():
    # plotting historic data
    fig, ax = pyplot.subplots(figsize=(16, 6), dpi=100)
    yAxisData = _10GetHistoricData.getHistoricData("price")
    xAxisStart = datetime.date(2000, 1, 1)
    xAxisDates = [xAxisStart + datetime.timedelta(n * 7) for n in range(len(yAxisData))]
    ax.plot(xAxisDates, numpy.asarray(yAxisData, float), color = "black")

    # plotting vertical line separating historic and forecast data
    pyplot.axvline(x = xAxisDates[-1], color = "green", linestyle = "dashed")
    pyplot.legend()

    # plotting forecast data and setting a different background colour + text to show it is predicted
    yForecastAxisData = _11GetForecastData.getForecastData("price")
    xForecastAxisStart = datetime.date(2026, 10, 5)
    xForecastAxisDates = [xForecastAxisStart + datetime.timedelta(m * 7) for m in range(len(yForecastAxisData))]
    pyplot.axvspan(xForecastAxisStart, xForecastAxisDates[-1], facecolor = "b", alpha = 0.2)
    ax.plot(xForecastAxisDates, numpy.asarray(yForecastAxisData, float), color = "red")

    # misc graph stuff and generating the graph
    ax.set(xlabel = "Time (Year)", ylabel = "Price per kilogram (GBP, converted from NOK as of 24/10/2026)")
    pyplot.title("Price Per Kilogram of Salmon Sold")
    pyplot.grid()
    fig
    fig.savefig("PriceGraph.png", bbox_inches = "tight")
    pyplot.show()


# same as above but for quantity
def generateQuantityGraph():
    fig, ax = pyplot.subplots(figsize=(16, 6), dpi=100)
    yAxisData = _10GetHistoricData.getHistoricData("quantity")
    xAxisStart = datetime.date(2000, 1, 1)
    xAxisDates = [xAxisStart + datetime.timedelta(n * 7) for n in range(len(yAxisData))]
    ax.plot(xAxisDates, numpy.asarray(yAxisData, float), color = "black")

    pyplot.axvline(x = xAxisDates[-1], color = "green", linestyle = "dashed")
    pyplot.legend()

    yForecastAxisData = _11GetForecastData.getForecastData("quantity")
    xForecastAxisStart = datetime.date(2026, 10, 5)
    xForecastAxisDates = [xForecastAxisStart + datetime.timedelta(m * 7) for m in range(len(yForecastAxisData))]
    pyplot.axvspan(xForecastAxisStart, xForecastAxisDates[-1], facecolor = "b", alpha = 0.2)
    ax.plot(xForecastAxisDates, numpy.asarray(yForecastAxisData, float), color = "red")

    ax.set(xlabel = "Time (Year)", ylabel = "Weight (Metric tonnes)")
    pyplot.title("Number of Available Salmon in the Market")
    pyplot.grid()
    fig
    fig.savefig("PriceGraph.png", bbox_inches = "tight")
    pyplot.show()

generatePriceGraph()

