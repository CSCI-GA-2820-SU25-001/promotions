Feature: Promotions Management UI with Dynamic ID
  As an Admin
  I want to create and manage promotions
  So that I can verify end-to-end functionality using dynamic IDs

  Background:
    Given the following promotions exist
      | Name        | Type         | Product ID | Amount | Start Date  | End Date    | Status   |
      | Flash Sale  | PERCENT_OFF  | 101        | 25     | 2025-07-15  | 2025-07-31  | true     |
      | BOGO Deal   | BOGO         | 102        | 1      | 2025-08-01  | 2025-08-15  | false |
      | Summer Cut  | AMOUNT_OFF   | 103        | 10     | 2025-07-01  | 2025-07-25  | true   |

  Scenario: Create 3 promotions and save their IDs
    When I visit the "Home Page"
    And I set the "Name" to "Flash Sale"
    And I select "PERCENT_OFF" for "Type"
    And I set the "Product ID" to "101"
    And I set the "Amount" to "25"
    And I select "true" for "Status"
    And I set the "Start Date" to "2025-07-15"
    And I set the "End Date" to "2025-07-31"
    And I press the "Create" button

    And I set the "Name" to "BOGO Deal"
    And I select "BOGO" for "Type"
    And I set the "Product ID" to "102"
    And I set the "Amount" to "1"
    And I select "false" for "Status"
    And I set the "Start Date" to "2025-08-01"
    And I set the "End Date" to "2025-08-15"
    And I press the "Create" button

    And I set the "Name" to "Summer Cut"
    And I select "AMOUNT_OFF" for "Type"
    And I set the "Product ID" to "103"
    And I set the "Amount" to "10"
    And I select "true" for "Status"
    And I set the "Start Date" to "2025-07-01"
    And I set the "End Date" to "2025-07-25"
    And I press the "Create" button


  Scenario: Retrieve a promotion by saved ID  
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    And I save the ID for "Flash Sale" as "flash_sale_id"
    And I save the ID for "BOGO Deal" as "bogo_id"
    And I save the ID for "Summer Cut" as "summer_cut_id"
    And I set the "promotion ID" to the saved ID "flash_sale_id"
    And I press the "Retrieve" button
    Then I should see "Flash Sale" in the "Name" field
    And I should see "101" in the "Product ID" field
    And I should see "25" in the "Amount" field
    And I should see "PERCENT_OFF" in the "Type" field
    And I should see "2025-07-15" in the "Start Date" field
    And I should see "2025-07-31" in the "End Date" field
    And I should see "true" in the "Status" field

  Scenario: Update the promotion
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    And I save the ID for "Flash Sale" as "flash_sale_id"
    And I set the "promotion ID" to the saved ID "flash_sale_id"
    When I set the "promotion ID" to the saved ID "flash_sale_id"
    And I press the "Retrieve" button
    Then I should see "Flash Sale" in the "Name" field
    When I set the "Amount" to "30"
    And I press the "Update" button
    Then I should see "30" in the "Amount" field

  Scenario: Deactivate the promotion
    When I visit the "Home Page"
    And I press the "Clear" button
    When I press the "Search" button
    And I save the ID for "Flash Sale" as "flash_sale_id"
    And I press the action button for the saved ID "flash_sale_id"
    And I set the "promotion ID" to the saved ID "flash_sale_id"
    And I press the "Retrieve" button
    Then I should see "false" in the "Status" field

  Scenario: Reactivate the promotion
    When I visit the "Home Page"
    And I press the "Clear" button
    When I press the "Search" button
    And I save the ID for "BOGO Deal" as "bogo_id"
    And I press the action button for the saved ID "bogo_id"
    And I set the "promotion ID" to the saved ID "bogo_id"
    And I press the "Retrieve" button
    Then I should see "true" in the "Status" field

  Scenario: Delete the promotion
    When I visit the "Home Page"
    And I press the "Clear" button
    When I press the "Search" button
    And I save the ID for "Flash Sale" as "flash_sale_id"
    And I set the "promotion ID" to the saved ID "flash_sale_id"
    And I press the "Delete" button
    Then the "Name" field should be empty
    And the "Type" field should be empty
  
  Scenario: Search by promo_type
    When I visit the "Home Page"
    And I select "BOGO" for "Type"
    And I press the "Search" button
    Then I should see "BOGO Deal" in the results


