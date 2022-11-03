from flask import Flask, jsonify, request
from flask_restful import Resource, Api

import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options


def get_result(QUERY_DETAILS):
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Provide the path of chromedriver present on your system.
    driver = webdriver.Chrome(executable_path="chromedriver", options=chrome_options)

    # Setting date for query
    today = date.today()
    today = today.strftime("%d/%m/%Y")

    driver.get(f"http://www.educationboardresults.gov.bd/")

    STUDENT_DETAILS = {
        'success' : False,
        'date': today,
        'is_gpa5': False,
        'data' : {} 
    }

    SSC_input = Select(driver.find_element(by=By.NAME, value="exam"))
    SSC_input.select_by_visible_text(QUERY_DETAILS['exam'])

    year_input = Select(driver.find_element(by=By.NAME, value="year"))
    year_input.select_by_visible_text(QUERY_DETAILS['year'])

    board_input = Select(driver.find_element(by=By.NAME, value="board"))
    board_input.select_by_visible_text(QUERY_DETAILS['board'])

    roll_input = driver.find_element(by=By.NAME, value="roll")
    roll_input.send_keys(QUERY_DETAILS['roll'])

    reg_input = driver.find_element(by=By.NAME, value="reg")
    reg_input.send_keys(QUERY_DETAILS['reg'])


    fieldset_element = driver.find_element(By.TAG_NAME, "fieldset")
    table_rows = fieldset_element.find_elements(By.TAG_NAME, "tr")
    parent_element = table_rows[6]

    child_columns = parent_element.find_elements(By.TAG_NAME, "td")
    maths_to_solve = child_columns[1].text
    solved_maths = eval(maths_to_solve)

    maths_input = driver.find_element(by=By.NAME, value="value_s")
    maths_input.send_keys(solved_maths)

    submit_element = driver.find_elements(By.TAG_NAME, "input")[1]
    submit_element.submit()

    time.sleep(1)

    current_link = driver.current_url

    if 'result.php' in current_link:
        STUDENT_DETAILS['success'] = True
        tbody_elements = driver.find_elements(By.TAG_NAME, "tbody")

        personal_details_table = tbody_elements[8]
        personal_details = personal_details_table.find_elements(By.TAG_NAME, "td")

        result_details_table = tbody_elements[9]
        result_details = result_details_table.find_elements(By.TAG_NAME, "td")

        key = ''
        for idx, i in enumerate(personal_details):
            if idx % 2 == 0:
                i = i.text.lower()
                i = i.replace(" ", "_")
                i = i.replace("'", "")
                key = i
                STUDENT_DETAILS['data'][key] = ''
            else:
                STUDENT_DETAILS['data'][key] = i.text
                key = ''

        STUDENT_DETAILS['is_gpa5'] = STUDENT_DETAILS['data']['gpa'] == '5.00'

        key = ['code', 'subject', 'grade']
        counter = 0
        for idx, i in enumerate(result_details):
            if idx in [0, 1, 2]:
                continue
            if idx % 3 == 0:
                counter = counter + 1
            index_key = idx % 3
            STUDENT_DETAILS['data'][f'{key[index_key]}{counter}'] = i.text

    driver.quit()

    return STUDENT_DETAILS

app = Flask(__name__)
api = Api(app)
  
class Hello(Resource):
    def get(self):
        return jsonify({'message': 'Welcome to SSC Result API!'})
  
class SSCResult(Resource):
  
    def post(self):
        json_data = request.get_json(force=True)
        exam = json_data['exam']
        year = json_data['year']
        board = json_data['board']
        roll = json_data['roll']
        reg = json_data['reg']

        result = get_result({
            'exam' : exam,
            'year' : year,
            'board' : board,
            'roll' : roll,
            'reg' : reg
        })

        return jsonify(result)
  
api.add_resource(Hello, '/')
api.add_resource(SSCResult, '/sscresult')
  
  
if __name__ == '__main__':
    app.run(debug = True)