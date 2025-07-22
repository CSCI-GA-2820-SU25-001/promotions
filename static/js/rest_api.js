// ****************************************
//  UTILITY FUNCTIONS
// ****************************************

function flash_message(message) {
  $("#flash_message").html(message);
}

function clear_form_data() {
  $("#promotion_name").val("");
  $("#promotion_category").val("");
  $("#promotion_status").val("true");
  $("#promotion_start_date").val("");
  $("#promotion_end_date").val("");
  $("#promotion_type").val("");
}

function update_form_data(res) {
  $("#promotion_name").val(res.name);
  $("#promotion_category").val(res.category);
  $("#promotion_status").val(res.status);
  $("#promotion_start_date").val(res.start_date);
  $("#promotion_end_date").val(res.end_date);
  $("#promotion_type").val(res.promo_type);
}

// ****************************************
//  CREATE A PROMOTION
// ****************************************

$("#create-btn").click(function () {
  let data = {
    name: $("#promotion_name").val(),
    category: $("#promotion_category").val(),
    status: $("#promotion_status").val() === "true",
    start_date: $("#promotion_start_date").val(),
    end_date: $("#promotion_end_date").val(),
    promo_type: $("#promotion_type").val(),
  };

  $.ajax({
    type: "POST",
    url: "/api/promotions",
    contentType: "application/json",
    data: JSON.stringify(data),
    success: function (res) {
      $("#promotion_id").val(res.id);
      flash_message("Promotion created successfully");
    },
    error: function (res) {
      flash_message(res.responseJSON.message);
    },
  });
});

// ****************************************
//  RETRIEVE A PROMOTION
// ****************************************

$("#retrieve-btn").click(function () {
  let id = $("#promotion_id").val();

  $.ajax({
    type: "GET",
    url: `/api/promotions/${id}`,
    success: function (res) {
      update_form_data(res);
      flash_message("Promotion retrieved successfully");
    },
    error: function (res) {
      flash_message(res.responseJSON.message);
    },
  });
});

// ****************************************
//  UPDATE A PROMOTION
// ****************************************

$("#update-btn").click(function () {
  let id = $("#promotion_id").val();
  let data = {
    name: $("#promotion_name").val(),
    category: $("#promotion_category").val(),
    status: $("#promotion_status").val() === "true",
    start_date: $("#promotion_start_date").val(),
    end_date: $("#promotion_end_date").val(),
    promo_type: $("#promotion_type").val(),
  };

  $.ajax({
    type: "PUT",
    url: `/api/promotions/${id}`,
    contentType: "application/json",
    data: JSON.stringify(data),
    success: function () {
      flash_message("Promotion updated successfully");
    },
    error: function (res) {
      flash_message(res.responseJSON.message);
    },
  });
});

// ****************************************
//  DEACTIVATE A PROMOTION (SOFT DELETE)
// ****************************************

$("#deactivate-btn").click(function () {
  let id = $("#promotion_id").val();

  $.ajax({
    type: "DELETE",
    url: `/api/promotions/${id}/deactivate`,
    success: function () {
      flash_message("Promotion deactivated successfully");
      $("#search-btn").click(); // Refresh list
    },
    error: function (res) {
      flash_message(res.responseJSON.message);
    },
  });
});

// ****************************************
//  SEARCH PROMOTIONS
// ****************************************

$("#search-btn").click(function () {
  let category = $("#promotion_category").val();
  let promo_type = $("#promotion_type").val();
  let query = [];

  if (category) query.push(`category=${category}`);
  if (promo_type) query.push(`promo_type=${promo_type}`);

  let url = "/api/promotions";
  if (query.length > 0) {
    url += "?" + query.join("&");
  }

  $.get(url, function (data) {
    $("table tbody").empty();

    data.forEach((promo) => {
      renderPromotion(promo);
    });

    flash_message("Search complete");
  });
});

// ****************************************
//  CLEAR FORM
// ****************************************

$("#clear-btn").click(function () {
  $("#promotion_id").val("");
  clear_form_data();
  flash_message("");
});

// ****************************************
//  TOGGLE BUTTON HANDLER (ACTIVATE/DEACTIVATE)
// ****************************************

function renderPromotion(promo) {
  let statusText = promo.status ? "Active" : "Inactive";
  let actionBtn = promo.status
    ? `<button class="btn btn-warning btn-sm activate-btn" data-id="${promo.id}" data-action="deactivate">Deactivate</button>`
    : `<button class="btn btn-success btn-sm activate-btn" data-id="${promo.id}" data-action="activate">Activate</button>`;

  let row = `
    <tr>
      <td>${promo.id}</td>
      <td>${promo.name}</td>
      <td>${promo.category || ""}</td>
      <td>${statusText}</td>
      <td>${promo.start_date}</td>
      <td>${promo.end_date}</td>
      <td>${promo.promo_type}</td>
      <td>${actionBtn}</td>
    </tr>
  `;
  $("table tbody").append(row);
}

$("table").on("click", ".activate-btn", function () {
  let promoId = $(this).data("id");
  let action = $(this).data("action"); // "activate" or "deactivate"
  let method = action === "activate" ? "PUT" : "DELETE";
  let url = `/api/promotions/${promoId}/${action}`;

  $.ajax({
    type: method,
    url: url,
    success: function () {
      flash_message(`Promotion ${promoId} ${action}d successfully`);
      $("#search-btn").click(); // Refresh the list
    },
    error: function (res) {
      flash_message(res.responseJSON.message);
    },
  });
});

// COMMENT: 
// - Added full toggle support for Activate/Deactivate.
// - `renderPromotion` appends dynamic buttons.
// - Event handler sends correct request and refreshes list.

