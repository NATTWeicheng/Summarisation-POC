from logic.GoogleAPI import getLOADINGCNTR
from datetime import datetime

# functions to write in csv(overload functions to write different items)
def writeCSV(date, newList):
    try:
        with open("summary.txt", "w", encoding="utf-8") as f:
            f.write(date)

            for row in newList:
                f.write(str(row))

            print("successfully wrote to file")
    except Exception as e:
        print("an error occured at writeCSV:", e)

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
                if rows[7] == "27 Apr 24":
                    print("\n{:<50} || {:>20} || {:>20} || {:>10} || {:>10} || {:>5}", rows[1],
                          rows[5], rows[6], rows[7], rows[8], rows[13])
    except Exception as e:
        print("Error in retrieving values in sheets:", e)

# Following code is used for LOADING CNTR(pivot table)
def createDeploymentSheet(startDate, endDate):
    newList = []
    try:
        # Get google sheet values
        values = getLOADINGCNTR()
        startIndex = 0
        endIndex = 0


        for i, rows in enumerate(values):
            if len(rows) > 0:
                # Change into string and remove spaces
                cell = str(rows[0].strip())
                if cell.startswith(startDate):
                    startIndex = i
                if cell.startswith(endDate):
                    endIndex = i
                
                if startIndex is None or endIndex is None:
                    print("start or end date not found.")
                    return None

        # Find the values from start date(inclusive) to end date(exclusive)
        newList = values[startIndex:endIndex]
        return newList
        
    except Exception as e:
        print("error creating deployment sheet", e)
        return None

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
        # check for address, row[0] is address
        # checks if it is empty
        localAddress = str(row[0]) if len(row) > 0 else "" 
        if localAddress != "":
            # not empty case
            currentAddress = localAddress
            countEmpty = 1
        else:
            # if empty
            countEmpty += 1

        # store the address data
        loadingAddTimes[currentAddress] = countEmpty

    totalAddTime = []
    currentRow = 0
    n = len(valueList)

    while currentRow < n:
        row = valueList[currentRow]
        address = str(row[0]) if len(row) > 0 else ""

        if address != "":
            # get the address data we just created
            countRow = loadingAddTimes.get(address, 1)
            endRow = min(currentRow + countRow, n)
            specificAddTime = valueList[currentRow:endRow]
            totalAddTime.extend(specificAddTime)
            currentRow = endRow
        else:
            currentRow += 1
    return totalAddTime

# 
def getAddTime(groupedAddress):
    if not groupedAddress:
        return ""

    result = ""
    presentDate = ""
    presentLocation = ""
    deliveryTime = ""

    currentDayData = []
    for row in groupedAddress:
        # convert everything into string
        currentDayData.append([str(cell) for cell in row])

    for row in currentDayData:
        # Carry forward the date from previous rows
        # if not empty
        if len(row) > 0 and row[0] != "":
            # set presentDate as data found
            presentDate = row[0]
        else:
            # if empty, set it as the latest found
            row[0] = presentDate

        if len(row) > 1:
            # if location is empty, set as latest found
            if row[1] == "":
                row[1] = presentLocation
            else:
                # if not empty, set as the current iteration's location
                presentLocation = row[1]

        if len(row) > 2:
            # if time is empty, set as the latest one found
            if row[2] == "":
                row[2] = deliveryTime
            else:
                # if not empty, set as the current iteration's delivery time
                deliveryTime = row[2]

        for i, val in enumerate(row):
            result += f'{i+1}:"{val}"\n'

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
