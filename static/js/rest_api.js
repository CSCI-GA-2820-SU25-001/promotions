$(function () {
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************
    function update_form_data(res) {
        $("#promotion_id").val(res.id);
        $("#promotion_name").val(res.name);
        $("#promotion_status").val(res.status ? "true" : "false");
        $("#promotion_start_date").val(res.start_date || "");
        $("#promotion_end_date").val(res.end_date || "");
        $("#promotion_type").val(res.promo_type || "");
        $("#promotion_product_id").val(res.product_id);
        $("#promotion_amount").val(res.amount);
    }

    function clear_form_data() {
        $("#promotion_name").val("");
        $("#promotion_status").val("true");
        $("#promotion_start_date").val("");
        $("#promotion_end_date").val("");
        $("#promotion_type").val("");
        $("#promotion_product_id").val("");
        $("#promotion_amount").val("");
    }

    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Promotion
    // ****************************************
    $("#create-btn").click(function () {
        let data = {
            name: $("#promotion_name").val(),
            status: $("#promotion_status").val() === "true",
            start_date: $("#promotion_start_date").val(),
            end_date: $("#promotion_end_date").val(),
            promo_type: $("#promotion_type").val(),
            product_id: parseInt($("#promotion_product_id").val()),
            amount: parseFloat($("#promotion_amount").val())
        };
        $("#flash_message").empty();
        $.ajax({
            type: "POST",
            url: "/promotions",
            contentType: "application/json",
            data: JSON.stringify(data),
        }).done(function(res){
            update_form_data(res);
            flash_message("Promotion created");
        }).fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // ****************************************
    // Update a Promotion
    // ****************************************
    $("#update-btn").click(function () {
        let id = $("#promotion_id").val();
        let data = {
            name: $("#promotion_name").val(),
            status: $("#promotion_status").val() === "true",
            start_date: $("#promotion_start_date").val(),
            end_date: $("#promotion_end_date").val(),
            promo_type: $("#promotion_type").val(),
            product_id: parseInt($("#promotion_product_id").val()),
            amount: parseFloat($("#promotion_amount").val())
        };
        $("#flash_message").empty();
        $.ajax({
            type: "PUT",
            url: `/promotions/${id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        }).done(function(res){
            update_form_data(res);
            flash_message("Promotion updated");
        }).fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // ****************************************
    // Deactivate a Promotion (Soft Delete)
    // ****************************************
    $("#deactivate-btn").click(function () {
        let id = $("#promotion_id").val();
        $("#flash_message").empty();
        $.ajax({
            type: "DELETE",
            url: `/promotions/${id}/deactivate`,
        }).done(function(){
            clear_form_data();
            flash_message("Promotion deactivated");
        }).fail(function(res){
            flash_message("Server error");
        });
    });

    // ****************************************
    // Retrieve a Promotion
    // ****************************************
    $("#retrieve-btn").click(function () {
        let id = $("#promotion_id").val();
        $("#flash_message").empty();
        $.ajax({
            type: "GET",
            url: `/promotions/${id}`,
        }).done(function(res){
            update_form_data(res);
            flash_message("Promotion retrieved");
        }).fail(function(res){
            clear_form_data();
            flash_message(res.responseJSON.message);
        });
    });

    // ****************************************
    // Delete a Promotion
    // ****************************************
    $("#delete-btn").click(function () {
        let id = $("#promotion_id").val();
        $("#flash_message").empty();
        $.ajax({
            type: "DELETE",
            url: `/promotions/${id}`,
        }).done(function(){
            clear_form_data();
            flash_message("Promotion deleted");
        }).fail(function(){
            flash_message("Server error");
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************
    $("#clear-btn").click(function () {
        $("#promotion_id").val("");
        $("#flash_message").empty();
        clear_form_data();
    });

    // ****************************************
    // Search for a Promotion
    // ****************************************
    $("#search-btn").click(function () {
        let type = $("#promotion_type").val();
        let queryString = "";

        if (type) {
            queryString += 'type=' + type;
        }

        $("#flash_message").empty();
        $.ajax({
            type: "GET",
            url: `/promotions?${queryString}`,
            contentType: "application/json"
        }).done(function(res){
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th>ID</th><th>Name</th><th>Status</th><th>Start</th><th>End</th><th>Type</th><th>Product</th><th>Amount</th><th>Actions</th>'
            table += '</tr></thead><tbody>'
            let firstPromotion = "";
            for (let i = 0; i < res.length; i++) {
                let promo = res[i];
                let statusText = promo.status ? "Active" : "Inactive";
                let actionBtn = promo.status
                    ? `<button class="btn btn-warning btn-sm toggle-btn" data-id="${promo.id}" data-action="deactivate">Deactivate</button>`
                    : `<button class="btn btn-success btn-sm toggle-btn" data-id="${promo.id}" data-action="activate">Activate</button>`;
                table += `<tr><td>${promo.id}</td><td>${promo.name}</td><td>${statusText}</td><td>${promo.start_date}</td><td>${promo.end_date}</td><td>${promo.promo_type}</td><td>${promo.product_id}</td><td>${promo.amount}</td><td>${actionBtn}</td></tr>`;
                if (i === 0) {
                    firstPromotion = promo;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);
            if (firstPromotion !== "") {
                update_form_data(firstPromotion);
            }
            flash_message("Search complete");
        }).fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });

    // ****************************************
    //  TOGGLE BUTTON HANDLER (ACTIVATE/DEACTIVATE)
    // ****************************************
    $("#search_results").on("click", ".toggle-btn", function () {
        let id = $(this).data("id");
        let action = $(this).data("action");
        let method = action === "activate" ? "PUT" : "DELETE";
        let url = `/promotions/${id}/${action}`;
        $.ajax({
            type: method,
            url: url
        }).done(function(){
            flash_message(`Promotion ${id} ${action}d`);
            $("#search-btn").click();
        }).fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });
});
