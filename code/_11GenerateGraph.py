import matplotlib.pyplot as pyplot
import _10getHistoricData


def generatePriceGraph():
    fig, ax = pyplot.subplots()
    xAxisData = 2000 + 5
    yAxisData = _10getHistoricData.getHistoricData("price")
    ax.plot(xAxisData, yAxisData)
    ax.set(xlabel = "Time (Year)", ylabel = "Price per kilogram (GBP, converted from NOK as of 24/10/2026)")



print(_10getHistoricData.getHistoricData("price"))