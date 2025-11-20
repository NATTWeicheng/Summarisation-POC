package com.summarisation;

import java.io.FileWriter;
import java.io.IOException;
import java.time.format.DateTimeFormatter;
import java.time.LocalDateTime;
import java.util.*;

public class SummarisationLogic {

    private GoogleAPI api;
    private DateTimeFormatter dtf;
    private LocalDateTime now;
    private List<List<Object>> newList;

    public SummarisationLogic() {

        api = new GoogleAPI();
        dtf = DateTimeFormatter.ofPattern("dd/MM/yyyy");
        now = LocalDateTime.now();
        newList = new ArrayList<>();

    }

    // functions to write in csv (overloaded functions to write different items)
    public void writeCSV(String date, List<List<Object>> newList) {

        try {
            FileWriter myWriter = new FileWriter("summary.txt");
            myWriter.write(date);

            for (List<Object> rows : newList) {

                myWriter.write(rows.toString());

            }

            myWriter.close();
            System.out.println("Successfully wrote to the file.");
        } catch (IOException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
        }
    }

    // function to print ALL values in the sheets
    public void printValue() {

        try {
            System.out.println(api.getLOADINGCNTR());
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }

    // function to return currentDate
    public String currentDate() {

        return dtf.format(now);

    }

    // Used for export
    public void printETA() {

        try {
            // Assigning Google sheets info into values
            List<List<Object>> values = api.getLOADINGCNTR();

            if (values == null || values.isEmpty()) {
                // If sheets is empty
                System.out.println("No data found.");
            } else {
                System.out.printf("\n%-50s || %20s || %20s || %10s || %10s || %5s || %15s\n", "Name",
                        "Portnet Booking REF", "Vessel / Voyage", "ETA Date", "ETA Timing", "LOT", "Product");
                System.out.println("");
            }
            for (List row : values) {
                if (row.get(7).equals("27 Apr 24")) {
                    System.out.printf("%-50s || %20s || %20s || %10s || %10s || %5s || %15s\n", row.get(1), row.get(5),
                            row.get(6), row.get(7), row.get(8), row.get(13), row.get(18));
                }

            }

        } catch (Exception e) {

            System.out.println(e.getMessage());
        }

    }

    // Used for Export
    public void printCollectionDate() {

        try {
            // Assigning Google sheets info into values
            List<List<Object>> values = api.getLOADINGCNTR();

            if (values == null || values.isEmpty()) {
                // If sheets is empty
                System.out.println("No data found.");
            } else {
                System.out.printf("\n%-50s || %20s || %20s || %10s || %10s || %5s\n", "Name", "Portnet Booking REF",
                        "Vessel / Voyage", "ETA Date", "ETA Timing", "LOT");
                System.out.println("");
            }
            for (List row : values) {
                if (row.get(7).equals("27 Apr 24")) {
                    System.out.printf("%-50s || %20s || %20s || %10s || %10s || %5s\n", row.get(1), row.get(5),
                            row.get(6), row.get(7), row.get(8), row.get(13));
                }

            }

        } catch (Exception e) {
            System.out.println(e.getMessage());
        }

    }

    // Following code is used for LOADING CNTR (pivot table)
    public void createDeploymentSheet(String startDate, String endDate) {

        newList.clear();

        try {
            // Assigning Google sheets info into values
            List<List<Object>> values = api.getLOADINGCNTR();
            int startIndex = 0;
            int endIndex = 0;
            int localIndex = 0;

            for (int i = 0; i < values.size(); i++) {

                List<Object> row = values.get(i);
                localIndex++;

                if (row.get(0).equals(startDate)) {
                    startIndex = localIndex - 1;
                }

                if (row.get(0).equals(endDate)) {
                    endIndex = localIndex - 1;
                }

            }
            // Now we want to add the content into a new List so we can easily manipulate
            // that
            int newListIterator = startIndex;
            while (newListIterator != endIndex) {

                newList.add(values.get(newListIterator));
                newListIterator++;

            }

            // System.out.println(newList);
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }

    }

    public List<List<Object>> groupAddress(String startDate, String endDate) {

        // if timing is not here then add a - first
        createDeploymentSheet(startDate, endDate);

        String dateOfCollectionList = newList.get(0).get(0).toString(); // To get the date for collection List
        Map<String, Integer> loadingAddTimes = new HashMap<String, Integer>(); // Just to get the amount of times 1
                                                                               // loading address should have
        List<List<Object>> totalAddTime = new ArrayList<>(); // This list of list is to store all the information with
                                                             // different addresses and their times

        int countOfEmptyLdAdd = 1; // To get the count of empty addresses
        String currentAddress = ""; // to store a copy of current address outside of the loop (necessary to not lose
                                    // the information when it gets the the next line)

        // Adding into the hashmap the amount of rows we have until the next element,
        // this way we know how many timing there should be for each groups
        for (int i = 0; i < newList.size(); i++) {
            List<Object> row = newList.get(i);
            String localCurrentAdd = row.get(1).toString();

            if (!localCurrentAdd.equals("")) {
                currentAddress = localCurrentAdd;
                countOfEmptyLdAdd = 1;

            } else {
                countOfEmptyLdAdd++;

            }
            loadingAddTimes.put(currentAddress, countOfEmptyLdAdd);
        }

        // System.out.println(loadingAddTimes);
        int currentRow = 0;
        // // Now we iterate through new List to get each of the time and add it into
        // specific add time, then adding that list into totalAddTime
        for (List<Object> row : newList) {
            int countRow = 0;
            List<Object> specificAddTime = new ArrayList<>(); // This list is to store a specific address and it's time

            String localCurrentAdd = row.get(1).toString();

            if (!row.get(1).equals("")) {

                if (loadingAddTimes.containsKey(localCurrentAdd)) {
                    countRow = loadingAddTimes.get(localCurrentAdd);
                }

                for (int i = currentRow; i < countRow + currentRow; i++) {

                    specificAddTime.add(newList.get(i));
                }
                currentRow += countRow;
                totalAddTime.add(specificAddTime);

            }
        }
        return totalAddTime;
    }

    public String getAddTime(List<List<Object>> groupedAddress) {
        StringBuilder result = new StringBuilder();
        List<ArrayList<String>> allAdd = new ArrayList<>();
        // for each grouped addresses
        for (List<Object> row : groupedAddress) {
            ArrayList<String> oneAdd = new ArrayList<>();
            // for each ArrayList in each groupedAddresses
            for (Object obj : row) {
                String str = obj.toString();
                int firstCommaIndex = str.indexOf(",");
                int secondCommaIndex = str.indexOf(",", firstCommaIndex + 1);
                String address = str.substring(firstCommaIndex + 1, secondCommaIndex);
                if (!address.equals("")) {
                    oneAdd.add(address);
                }
            }
            if (!oneAdd.isEmpty()) {
                allAdd.add(oneAdd);
            }
        }

        List<List<String>> current_day_data = new ArrayList<>();
        for (List<Object> x : groupedAddress) {
            for (Object y : x) {
                List<String> temp = new ArrayList<>();
                Iterable<?> iterable_address = (Iterable<?>) y;
                // System.out.println("====================================");
                for (Object z : iterable_address) {
                    // System.out.println("\"" + z + "\"");
                    temp.add(z.toString());
                }
                // System.out.println("====================================");
                current_day_data.add(temp);
            }
        }

        // for(List<String> x:current_day_data){
        // System.out.println(x);
        // }

        String present_date = current_day_data.get(0).get(0);
        String present_location = "";
        String deliveryTime = "";
        for (List<String> element_x : current_day_data) {

            // System.out.println(element_x.get(0));
            // System.out.println(present_date);

            element_x.set(0, present_date);
            if (element_x.get(1).isEmpty()) {
                element_x.set(1, present_location);
            } else {
                present_location = element_x.get(1);
            }
            if (element_x.get(2).isEmpty()) {
                element_x.set(2, deliveryTime);
            } else {
                deliveryTime = element_x.get(2);
            }
            // result.append("==============================================\n");
            for (int i = 0; i < element_x.size(); i++) {
                String element = element_x.get(i);
                result.append((i + 1)).append(":\"").append(element).append("\"\n");
            }
        }
        // result.append("==============================================\n");
        System.out.println(result.toString());
        return result.toString();
    }

    public String printDeploymentSheet(String startDate, String endDate) {
        return getAddTime(groupAddress(startDate, endDate));
    }

    // to get all dates available
    public List<String> getDates() {
        List<String> dates = new ArrayList<>();
        try {
            List<List<Object>> values = api.getLOADINGCNTR(); // Assuming getLOADINGCNTR() returns the data from Google
                                                              // Sheets

            for (List<Object> row : values) {
                String date = row.get(0).toString(); // Assuming date is in the first column (index 0)
                // return dates that are not empty + does not have the word Total / ok
                if (!date.equals("") && !date.contains("ok") && !date.equals("TBA")) {
                // if (!date.equals("") && !date.contains("Total") && !date.contains("ok") && !date.equals("TBA")) {
                    dates.add(date);
                }
            }
        } catch (Exception e) {
            System.out.println("An error occurred while fetching dates: " + e.getMessage());
        }
        return dates;
    }
}
