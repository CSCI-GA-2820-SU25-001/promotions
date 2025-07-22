$(function () {
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************
    function update_form_data(res) {
        $("#promotion_id").val(res.id);
        $("#promotion_name").val(res.name);
        $("#promotion_category").val(res.category);
        $("#promotion_status").val(res.status ? "true" : "false");
        $("#promotion_start_date").val(res.start_date || "");
        $("#promotion_end_date").val(res.end_date || "");
    }
    function clear_form_data() {
        $("#promotion_name").val("");
        $("#promotion_category").val("");
        $("#promotion_status").val("true");
        $("#promotion_start_date").val("");
        $("#promotion_end_date").val("");
    }
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }
    // ****************************************
    // Create a Promotion
    // ****************************************
    $("#create-btn").click(function () {
        let name = $("#promotion_name").val();
        let category = $("#promotion_category").val();
        let status = $("#promotion_status").val() === "true";
        let start_date = $("#promotion_start_date").val();
        let end_date = $("#promotion_end_date").val();
        let data = {
            "name": name,
            "category": category,
            "status": status,
            "start_date": start_date,
            "end_date": end_date
        };
        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "POST",
            url: "/promotions",
            contentType: "application/json",
            data: JSON.stringify(data),
        });
        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });
        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });
    // ****************************************
    // Update a Promotion
    // ****************************************
    $("#update-btn").click(function () {
        let promotion_id = $("#promotion_id").val();
        let name = $("#promotion_name").val();
        let category = $("#promotion_category").val();
        let status = $("#promotion_status").val() === "true";
        let start_date = $("#promotion_start_date").val();
        let end_date = $("#promotion_end_date").val();
        let data = {
            "name": name,
            "category": category,
            "status": status,
            "start_date": start_date,
            "end_date": end_date
        };
        $("#flash_message").empty();
        let ajax = $.ajax({
                type: "PUT",
                url: `/promotions/${promotion_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })
        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });
        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });
    // ****************************************
    // Retrieve a Promotion
    // ****************************************
    $("#retrieve-btn").click(function () {
        let promotion_id = $("#promotion_id").val();
        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "GET",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: ''
        })
        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });
        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });
    // ****************************************
    // Delete a Promotion
    // ****************************************
    $("#delete-btn").click(function () {
        let promotion_id = $("#promotion_id").val();
        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "DELETE",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: '',
        })
        ajax.done(function(res){
            clear_form_data()
            flash_message("Promotion has been Deleted!")
        });
        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });
    // ****************************************
    // Clear the form
    // ****************************************
    $("#clear-btn").click(function () {
        $("#promotion_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });
    // ****************************************
    // Search for a Promotion
    // ****************************************
    $("#search-btn").click(function () {
        let name = $("#promotion_name").val();
        let category = $("#promotion_category").val();
        let status = $("#promotion_status").val() === "true";
        let queryString = "";
        if (name) {
            queryString += 'name=' + name
        }
        if (category) {
            if (queryString.length > 0) {
                queryString += '&category=' + category
            } else {
                queryString += 'category=' + category
            }
        }
        if (status) {
            if (queryString.length > 0) {
                queryString += '&status=' + status
            } else {
                queryString += 'status=' + status
            }
        }
        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "GET",
            url: `/promotions?${queryString}`,
            contentType: "application/json",
            data: ''
        })
        ajax.done(function(res){
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Category</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '<th class="col-md-2">Start Date</th>'
            table += '<th class="col-md-2">End Date</th>'
            table += '</tr></thead><tbody>'
            let firstPromotion = "";
            for(let i = 0; i < res.length; i++) {
                let promotion = res[i];
                table +=  `<tr id="row_${i}"><td>${promotion.id}</td><td>${promotion.name}</td><td>${promotion.category}</td><td>${promotion.status}</td><td>${promotion.start_date || ""}</td><td>${promotion.end_date || ""}</td></tr>`;
                if (i == 0) {
                    firstPromotion = promotion;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);
            if (firstPromotion != "") {
                update_form_data(firstPromotion)
            }
            flash_message("Success")
        });
        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });
})
