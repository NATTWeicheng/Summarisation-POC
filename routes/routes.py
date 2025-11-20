from flask import Blueprint, request
from logic.summarisationLogic import getDates, getAddTime, groupAddress
routes = Blueprint('routes', __name__)

@routes.route('/get-dates', methods=['POST'])
def getDate():
    return getDates()

@routes.route('/start-end', methods=['POST'])
def startEnd():
    # Start and end date
    data = request.get_json()
    startDate = data.get("startDate")
    endDate = data.get("endDate")
    result = getAddTime(groupAddress(startDate, endDate))
    return result

