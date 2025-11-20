// const startDateDropdown = document.getElementById("startDate");
// const endDate = document.getElementById("newEndDate");
const checkDateButton = document.getElementById("submitDateBtn");
const display = document.getElementById("display");
const selectedStartDate = document.getElementById("selectedStartDate");
const bigCalendar = document.getElementById('calendar');

var startDateString = "";
var endDateString = "";
var timings = "";

window.onload = function() {
    // load calendar
    showCalendar();

    // get all dates when page on load
    getAvailDates()
    .then(data => {
        // split by timings and remove "" + []
        timings = data.slice(1, -1).split(',').map(item => item.replace(/^\"|\"$/g, ''));
        addEvents(timings);
    });
}

var prevMonth = document.querySelector('.prev');
var nextMonth = document.querySelector('.next');
var monthPassed = "";
var yearPassed = "";
var dayPassed = "";

const monthNames = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"];

const calendar = {
    currentMonth: new Date().getMonth(),
    currentYear: new Date().getFullYear(),
    selectedDate: null,
    events: {}
};

// change current month / year
prevMonth.addEventListener('click', () => {
    calendar.currentMonth--;
    if (calendar.currentMonth < 0) {
        calendar.currentMonth = 11;
        calendar.currentYear--;
    }
    calendar.selectedDate = null; // Reset selected date when changing month
    showCalendar();
});

nextMonth.addEventListener('click', () => {
    calendar.currentMonth++;
    if (calendar.currentMonth > 11) {
        calendar.currentMonth = 0;
        calendar.currentYear++;
    }
    calendar.selectedDate = null; // Reset selected date when changing month
    showCalendar();
});

// add the timings received from backend into calendar events object
function addEvents(dates) {
    dates.forEach(dateStr => {
        const [day, month, year] = dateStr.split(" ");
        const monthIndex = monthNames.indexOf(month.charAt(0).toUpperCase() + month.slice(1, 3));
        const eventDate = new Date(Date.UTC(2000 + parseInt(year), monthIndex, day)).toISOString().split('T')[0];
        calendar.events[eventDate] = "Schedule"; 
    });
    console.log("calendar events", calendar.events);
}

function showCalendar() {
    // clear any selected dates
    const allDays = document.querySelectorAll('.days li');
    allDays.forEach(day => day.classList.remove('selected'));
    
    const daysInMonth = new Date(calendar.currentYear, calendar.currentMonth + 1, 0).getDate();
    const firstDay = new Date(calendar.currentYear, calendar.currentMonth, 1).getDay();
    const today = new Date();

    document.getElementById('month-year').innerText = monthNames[calendar.currentMonth] + ' ' + calendar.currentYear;

    const daysContainer = document.querySelector('.days');
    daysContainer.innerHTML = '';

    // Add blank days for the first week
    for (let i = 0; i < firstDay; i++) {
        const blankDay = document.createElement('li');
        daysContainer.appendChild(blankDay);
    }

    // Add actual days
    for (let i = 1; i <= daysInMonth; i++) {
        const day = document.createElement('li');
        day.innerText = i;

        // Highlight the current day if no other date is selected
        if (!calendar.selectedDate && calendar.currentMonth === today.getMonth() && calendar.currentYear === today.getFullYear() && i === today.getDate()) {
            day.classList.add('selected');
            dayPassed = i;
            monthPassed = calendar.currentMonth;
            yearPassed = calendar.currentYear;
        }

        // Highlight the selected day
        if (calendar.selectedDate === i && calendar.currentMonth === calendar.selectedMonth && calendar.currentYear === calendar.selectedYear) {
            day.classList.add('selected');
            dayPassed = i;
            monthPassed = calendar.selectedMonth;
            yearPassed = calendar.selectedYear;
        }

        // create event 
        const currentDate = `${calendar.currentYear}-${String(calendar.currentMonth + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
        if (calendar.events[currentDate]) {
            // console.log(`Event found for date: ${currentDate}`);
            const breakline = document.createElement('br');
            const eventDot = document.createElement('div');
            eventDot.classList.add('event');
            eventDot.title = calendar.events[currentDate];
            day.appendChild(breakline);
            day.appendChild(eventDot);
        }

        day.addEventListener('click', () => {
            calendar.selectedDate = i;
            calendar.selectedMonth = calendar.currentMonth;
            calendar.selectedYear = calendar.currentYear;
            showCalendar();
        });

        daysContainer.appendChild(day);
    }
}

checkDateButton.addEventListener("click", function () {

    // hide calendar + check button 
    display.style.display = "block";
    display.style.opacity = '1';
    checkDateButton.style.display = 'none';
    bigCalendar.style.display = 'none';

    // change format of day, month and year passed as startDateString
    // make day be 2 characters
    if (dayPassed < 10) {
        dayPassed = "0" + dayPassed;
    }
    startDateString = dayPassed + " " + (monthNames[monthPassed]).substring(0, 3) + " " + yearPassed.toString().slice(-2);

    // check whether startDate is found in available dates
    var found = false;
    for (var i = 0; i < timings.length; i++) {
        if (startDateString === timings[i]) {
            found = true;
            break;
        }
    }
    
    // if startDateString is not found in list of timings, 
    if (!found) {
        document.getElementById('dataTable').textContent = "Selected date \"" + startDateString + "\" does not have a schedule";
    } else {
        // compare and see which is the next date to be set as endDate
        // convert startDateString to a Date object
        const startDateObject = new Date(startDateString.replace(/(\d{2}) (\w{3}) (\d{2})/, "$1-$2-$20$3"));
        var endDate;
        
        for (var i = 0; i < timings.length; i++) {
            // convert each date string to a date object
            const dateObject = new Date(timings[i].replace(/(\d{2}) (\w{3}) (\d{2})/, "$1-$2-$20$3"));
            if (dateObject > startDateObject) {
                endDate = timings[i];
                break;
            }
        }
        // if startDate was the last in the list
        if (endDate === undefined) {
            endDate = "TBA";
        }

        endDateString = endDate;

        console.log("startDateString", startDateString);
        console.log("endDateString", endDateString);
        
        // set selected start date 
        selectedStartDate.textContent = "Start Date: " + startDateString;

        // pass start and end date into backend
        passDates(startDateString, endDateString)
        .then(data => {
            // create frontend for data
            var dataString = convertData(data).toString();
            var dataArray = dataString.split(/\],\s*\[/).map(item => item.replace(/^\[|\]$/g, ''));
            // console.log("dataArray", dataArray);

            createTables(dataArray);
        })
    }

})




function createTables(dataArray) {
    var tablesContainer = document.getElementById('dataTable');
    while(tablesContainer.firstChild) { 
        tablesContainer.removeChild(tablesContainer.firstChild); 
    } 

    var venueData = {};
    var tempVenueData = {};

    for (var i = 0; i < dataArray.length; i++) {
        var dataEntry = dataArray[i].replace(/\"/g, '').split(', ');

        var address = dataEntry[1];
        var timing = dataEntry[2];
        var loadingAddress = dataEntry[7];

        if (!tempVenueData[address]) {
            tempVenueData[address] = [];
        }

        // only push timings with words that does not match
        if (!loadingAddress == ""){
            if (!loadingAddress.toLowerCase().includes("bag fitting") && 
                !loadingAddress.toLowerCase().includes("sgi stuffing") && 
                !loadingAddress.toLowerCase().includes("psa export")) {
                    // tempVenueData[address].push([timing, loadingAddress]);
                    tempVenueData[address].push([timing]);
            }
        } else {
            tempVenueData[address].push([timing]);
        }
    }

    // remove any address that has no timings
    for (var address in tempVenueData) {
        if (tempVenueData[address].length > 0) {
            venueData[address] = tempVenueData[address];
        }
    }

    // console.log("venueData", venueData);
    // console.log("tempVenueData", tempVenueData);
    for (var address in venueData) {
        var tableWrapper = document.createElement('div');
        tableWrapper.classList.add('tableWrapper');

        var tableHeader = document.createElement('h4');
        tableHeader.textContent = address;
        tableWrapper.appendChild(tableHeader);

        var table = document.createElement('table');
        table.classList.add('innerTable');

        venueData[address].forEach(entry => {
            var row = document.createElement('tr');
            entry.forEach(cellText => {
                var td = document.createElement('td');
                td.textContent = cellText;
                row.appendChild(td);
            });
            table.appendChild(row);
        });

        tableWrapper.appendChild(table);
        tablesContainer.appendChild(tableWrapper);
    }
}

function convertData(input) {
    // Split input into lines and filter out empty lines
    var lines = input.split('\n').filter(line => line.trim() !== '');
    var results = [];
    var entry = [];

    // Process each line
    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        var parts = line.split(':"');
        var index = parts[0].trim();
        var value = parts[1].trim();

        // Remove quotes from value
        value = value.replace(/^"|"$/g, '');

        entry.push(value);

        // get next index to see whether to push entry or not
        if (i + 1 < lines.length) {
            var nextIndex = lines[i + 1].split(':"')[0].trim();
        } else {
            var nextIndex = null;
        }
        // check whether index 6 is the last field, if so, push entry
        if (index === "6" && !(nextIndex === "7")) {

            // Create a string with the entries, without wrapping in quotes
            var formattedEntry = '[' + entry.join(', ') + ']';
            results.push(formattedEntry);
            entry = [];

        // check whether index 7 is the last field, if so, push entry
        } else if (index === "7" && !(nextIndex === "8")) {
            var formattedEntry = '[' + entry.join(', ') + ']';
            results.push(formattedEntry);
            entry = [];

        // check whether index 8 is the last field, if so, push entry
        } else if (index === "8") {
            var formattedEntry = '[' + entry.join(', ') + ']';
            results.push(formattedEntry);
            entry = [];
        }
        
    }
    // console.log(results);
    return results;
}


// backend function 
function passDates(startDate, newEndDate) {
    const requestData = {
        startDate: startDate,
        endDate: newEndDate
    }

    return fetch('/start-end', {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain' // send plain text
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.text())
    .then(data => {
        return data;
    })
    .catch(error => {
        console.error('Error: ', error);
    })
}

function getAvailDates() {
    return fetch('/get-dates', {
        method: 'POST'
    })
    .then(response => {return response.text()})
    .then(data => {
        console.log(data); // Handle the data received from the backend
        return data;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}