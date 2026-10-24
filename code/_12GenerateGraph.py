import matplotlib.pyplot as pyplot
from matplotlib.pyplot import figure
import datetime
import numpy
import _10GetHistoricData


def generatePriceGraph():
    fig, ax = pyplot.subplots(figsize=(16, 6), dpi=100)
    yAxisData = _10GetHistoricData.getHistoricData("price")
    xAxisStart = datetime.date(2000, 1, 1)
    xAxisDates = [xAxisStart + datetime.timedelta(n * 7) for n in range(len(yAxisData))]
    ax.plot(xAxisDates, numpy.asarray(yAxisData, float))


    
    ax.set(xlabel = "Time (Year - Month)", ylabel = "Price per kilogram (GBP, converted from NOK as of 24/10/2026)")
    pyplot.title("Price Per Kilogram of Salmon Sold")
    pyplot.grid()
    fig
    fig.savefig("PriceGraph.png")
    pyplot.show()

generatePriceGraph()

