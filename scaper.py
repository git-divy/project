from playwright.sync_api import sync_playwright
import parser
from tqdm import tqdm
import os
from dotenv import load_dotenv
load_dotenv()

URL = os.getenv('URL')

def scrape_data(FROM, TO, URL):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()
        page.goto(URL)

        
        page.wait_for_selector("#ddlAttttype")
        page.select_option("#ddlAttttype", value="1")
        datax = ''
        datax_json = []

        for i in tqdm(range(FROM, TO+1)):

            try:
                page.fill("#txtRollNo", "")
                page.wait_for_selector("#txtRollNo")
                page.locator("#txtRollNo").click()
                page.locator("#txtRollNo").type(f'{i}', delay=80)
                value = page.locator("#txtRollNo").input_value()
                #print('Roll No : ', value)

                page.wait_for_selector("#btnView")
                page.locator('#btnView').click()

                content = page.locator("xpath=/html/body/form/div[3]/div/div/div/div[2]/div[2]/div/div[2]").inner_html()     

                
                if content is not None:
                    parsed_json = parser.parse_attendance_html(content)
                    datax_json.append(parsed_json)

            except Exception as ex:
                print(str(ex))

        browser.close()

        return datax_json

