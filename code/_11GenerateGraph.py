import matplotlib.pyplot as pyplot
import datetime
import _10getHistoricData


def generatePriceGraph():
    fig, ax = pyplot.subplots()
    yAxisData = _10getHistoricData.getHistoricData("price")
    xAxisStart = datetime.date(2000, 1, 1)
    xAxisDates = [xAxisStart + datetime.timedelta(n) for n in range(len(yAxisData))]
    ax.plot(xAxisDates, yAxisData)
    ax.set(xlabel = "Time (Year)", ylabel = "Price per kilogram (GBP, converted from NOK as of 24/10/2026)")
    fig.savefig("PriceGraph.png")

    pyplot.show()

generatePriceGraph()

