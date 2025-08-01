from behave import given, when, then
from selenium.webdriver.common.by import By
import time

# Dictionary to store saved IDs
saved_ids = {}


@given('I visit the "{page_name}"')
@when('I visit the "{page_name}"')
def step_visit_page(context, page_name):
    context.driver.get(context.base_url)
    time.sleep(1)


@when('I set the "{field}" to "{value}"')
def step_set_field(context, field, value):
    field_map = {
        "Name": "promotion_name",
        "Promotion ID": "promotion_id",
        "Product ID": "promotion_product_id",
        "Amount": "promotion_amount",
        "Start Date": "promotion_start_date",
        "End Date": "promotion_end_date",
        "Status": "promotion_status",
    }
    elem_id = field_map.get(field, None)
    if not elem_id:
        raise Exception(f"Unknown field: {field}")
    element = context.driver.find_element(By.ID, elem_id)
    element.clear()
    element.send_keys(value)


@when('I select "{value}" for "{field}"')
def step_select_dropdown(context, value, field):
    from selenium.webdriver.support.ui import Select

    field_map = {"Type": "promotion_type", "Status": "promotion_status"}
    elem_id = field_map.get(field, None)
    if not elem_id:
        raise Exception(f"Unknown select field: {field}")
    select = Select(context.driver.find_element(By.ID, elem_id))
    select.select_by_visible_text(value)


@when('I press the "{button}" button')
def step_press_button(context, button):
    button_id_map = {
        "Create": "create-btn",
        "Search": "search-btn",
        "Clear": "clear-btn",
        "Update": "update-btn",
        "Delete": "delete-btn",
        "Retrieve": "retrieve-btn",
    }
    btn_id = button_id_map.get(button, None)
    if not btn_id:
        raise Exception(f"Unknown button: {button}")
    context.driver.find_element(By.ID, btn_id).click()
    time.sleep(1)


@when('I save the ID for "{name}" as "{var_name}"')
def step_save_id(context, name, var_name):
    rows = context.driver.find_elements(By.CSS_SELECTOR, "#search_results tbody tr")
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        print("DEBUG ROW:", [col.text.strip() for col in cols])
        if cols[1].text.strip() == name:
            saved_ids[var_name] = cols[0].text.strip()
            return
    raise Exception(f"Promotion with name '{name}' not found.")


@when('I set the "Promotion ID" to the saved ID "{var_name}"')
def step_set_saved_id(context, var_name):
    promotion_id = saved_ids.get(var_name, None)
    print(promotion_id)
    if not promotion_id:
        raise Exception(f"No saved ID found for '{var_name}'")
    element = context.driver.find_element(By.ID, "promotion_id")
    element.clear()
    element.send_keys(promotion_id)


@when('I press the action button for the saved ID "{var_name}"')
def step_click_action_button(context, var_name):
    promotion_id = saved_ids.get(var_name, None)
    if not promotion_id:
        raise Exception(f"No saved ID found for '{var_name}'")

    rows = context.driver.find_elements(By.CSS_SELECTOR, "#search_results tbody tr")
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols[0].text.strip() == promotion_id:
            button = cols[8].find_element(By.TAG_NAME, "button")
            button.click()
            time.sleep(1)
            return
    raise Exception(f"Row with ID '{promotion_id}' not found in search results.")


@then('I should see "{expected}" in the "{field}" field')
def step_should_see_in_field(context, expected, field):
    field_map = {
        "Name": "promotion_name",
        "Product ID": "promotion_product_id",
        "Amount": "promotion_amount",
        "Type": "promotion_type",
        "Start Date": "promotion_start_date",
        "End Date": "promotion_end_date",
        "Status": "promotion_status",
    }
    elem_id = field_map.get(field, None)
    if not elem_id:
        raise Exception(f"Unknown field: {field}")
    element = context.driver.find_element(By.ID, elem_id)
    value = element.get_attribute("value")
    assert expected == value, f"Expected '{expected}' in '{field}', but got '{value}'"


@then('the "{field}" field should be empty')
def step_field_should_be_empty(context, field):
    field_map = {"Name": "promotion_name", "Type": "promotion_type"}
    elem_id = field_map.get(field, None)
    if not elem_id:
        raise Exception(f"Unknown field: {field}")
    value = context.driver.find_element(By.ID, elem_id).get_attribute("value")
    assert value == "", f"Expected '{field}' field to be empty, but got '{value}'"


@then('I should see "{text}" in the results')
def step_see_in_results(context, text):
    table = context.driver.find_element(By.ID, "search_results")
    rows = table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        if text in row.text:
            return
    raise AssertionError(f"'{text}' not found in search results")
