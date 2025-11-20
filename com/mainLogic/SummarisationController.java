package com.summarisation;

import java.util.List;

import org.json.JSONObject;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/")
public class SummarisationController {

    SummarisationLogic summarisationLogic = new SummarisationLogic();

    // @GetMapping("index")
    // public String showMyPage() {
    // return "index";
    // }

    @PostMapping("/start-end")
    @ResponseBody
    public String passStartEndDate(@RequestBody String requestBody) {

        JSONObject jsonObject = new JSONObject(requestBody);
        String startDate = jsonObject.getString("startDate");
        String endDate = jsonObject.getString("endDate");

        // Call the logic with start and end dates
        String result = summarisationLogic.getAddTime(summarisationLogic.groupAddress(startDate, endDate));
        // System.out.println(result);
        return result;
    }

    @PostMapping("/get-dates")
    public List<String> getAvailDates() {
        return summarisationLogic.getDates();
    }

}
