from logic.GoogleAPI import getCredentials, getLOADINGCNTR
from datetime import datetime

# functions to write in csv(overload functions to write different items)
def writeCSV():
    return 0

# function to print ALL values in the sheets
def printValue():
    try:
        values = getLOADINGCNTR()
        return values
    except Exception as e:
        print("Error in retrieving values in sheets:", e)
        return None

# function to return current date
def currentDate():
    return datetime.now()

# used for export
def printETA():
    try:
        values = getLOADINGCNTR()
        # if sheets is empty
        if not values:
            print("No data found.")
        else:
            # Format table headers size
            print("\n{:<50} || {:>20} || {:>20} || {:>10} || {:>10} || {:>5} || {:>15}".format(
                "Name", "Portnet Booking REF", "Vessel / Voyage", "ETA Date", "ETA Timing", "LOT", "Product"
            ))
            print("")
            for rows in values:
                if rows[7] == "27 Apr 24":
                    print("\n{:<50} || {:>20} || {:>20} || {:>10} || {:>10} || {:>5} || {:>15}", rows[1],
                          rows[5], rows[6], rows[7], rows[8], rows[13], rows[18])
    except Exception as e:
        print("Error in retrieving values in sheets:", e)

# Used for export
def printCollectionDate():
    try:
        values = getLOADINGCNTR()
        # if sheets is empty
        if not values:
            print("No data found.")
        else:
            # Format table headers size
            print("\n{:<50} || {:>20} || {:>20} || {:>10} || {:>10} || {:>5}".format(
                "Name", "Portnet Booking REF", "Vessel / Voyage", "ETA Date", "ETA Timing", "LOT"
            ))
            print("")
            for rows in values:
                if rows[7] is "27 Apr 24":
                    print("\n{:<50} || {:>20} || {:>20} || {:>10} || {:>10} || {:>5}", rows[1],
                          rows[5], rows[6], rows[7], rows[8], rows[13])
    except Exception as e:
        print("Error in retrieving values in sheets:", e)

# Following code is used for LOADING CNTR(pivot table)
def createDeploymentSheet(startDate, endDate):
    newList = []
    try:
        values = getLOADINGCNTR()
        startIndex = 0
        endIndex = 0

        for i, rows in enumerate(values):
            if len(rows) > 0:
                if rows[0] == startDate:
                    startIndex = i
                if rows[0] == endDate:
                    endIndex = i
                
                if startIndex is None or endIndex is None:
                    print("start or end date not found.")
                    return None

                else:
                    newList = values [startIndex:endIndex]
                return newList
    except Exception as e:
        print("error")
        return 0

# Count howmany times the address appeared
def groupAddress(startDate, endDate):

    # Retrieve the data
    valueList = createDeploymentSheet(startDate, endDate)

    if not valueList:
        return []
    
    loadingAddTimes = {}
    currentAddress = ""
    countEmpty = 1

    for row in valueList:
        localAddress = str(row[1]) if len(row) > 1 else "" 
        if localAddress != "":
            currentAddress = localAddress
            countEmpty = 1
        else:
            countEmpty += 1

        loadingAddTimes[currentAddress] = countEmpty

    totalAddTime = []
    currentRow = 0
    n = len(valueList)

    while currentRow < n:
        row = valueList[currentRow]
        address = str(row[1]) if len(row) > 1 else ""

        if address != "":
            countRow = loadingAddTimes.get(address, 1)
            endRow = min(currentRow + countRow, n)
            specificAddTime = valueList[currentRow:endRow]
            totalAddTime.append(specificAddTime)
            currentRow = endRow
        else:
            currentRow += 1

    return totalAddTime


def getAddTime(groupedAddress):
    if not groupedAddress:
        return ""

    result = ""
    presentDate = str(groupedAddress[0][0][0])  # Take first row, first column as the date
    presentLocation = ""
    deliveryTime = ""

    currentDayData = []
    for group in groupedAddress:
        for row in group:
            currentDayData.append([str(cell) for cell in row])

    for row in currentDayData:
        row[0] = presentDate

        if len(row) > 1:
            if row[1] == "":
                row[1] = presentLocation
            else:
                presentLocation = row[1]

        if len(row) > 2:
            if row[2] == "":
                row[2] = deliveryTime
            else:
                deliveryTime = row[2]

        for i, val in enumerate(row):
            result += f'{i+1}:"{val}"\n'

    print(result)
    return result


def printDeploymentSheet(startDate, endDate):
    return getAddTime(groupAddress(startDate, endDate))

# get all dates available
def getDates():
    dates = []
    values = getLOADINGCNTR()
    try:
        for rows in values:
            date = str(rows[0]) # assuming date is in the first column(index 0)

            if "ok" not in date and date != "" and date != "TBA": 
                dates.append(date)

        if not dates:
            print("No dates exist.")
            return None
        return dates
    except Exception as e:
        print("An error occured while fetching dates", e)
        return None
