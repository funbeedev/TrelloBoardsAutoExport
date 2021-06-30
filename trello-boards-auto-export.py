from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as Options_firefox
from selenium.webdriver.chrome.options import Options as Options_chrome

import time
from datetime import datetime
import linecache
import traceback

script_config_file = "trello-boards-info"
log_file = "trello-scraping.log"


def log(print_this):
    #print to console
    print(print_this)
    #print to file
    print(print_this, file=open(log_file, "a"))
    pass

def setup():

    global browser

    log("timestamp: %s" %datetime.now())

    #first line in file contains config for script
    settings = read_data_from_file(script_config_file, 1).split(';')
    #get driver and headless setting, make reading all lower case to avoid caps issues
    driver_setting = settings[0].lower().split('driver=')[1]
    headless_setting = settings[1].lower().split('headless=')[1]

    #Configure firefox 
    if driver_setting == 'firefox':
        DRIVER_PATH = './geckodriver'
        firefox_options = Options_firefox()
        
        if headless_setting == 'true':
            firefox_options.headless = True
        else:
            firefox_options.headless = False

        browser = webdriver.Firefox(executable_path=DRIVER_PATH, options=firefox_options)

    #Configure chrome 
    elif driver_setting == "chrome":
        DRIVER_PATH = './chromedriver'
        chrome_options = Options_chrome()

        if headless_setting == 'true':
            chrome_options.add_argument("--headless")
            #need to add this otherwise will occassionally get error 'element not interactable'
            chrome_options.add_argument("--window-size=1920,1080")
        else:
            chrome_options.add_argument("--None")

        browser = webdriver.Chrome(executable_path=DRIVER_PATH, options=chrome_options)

    else:
        driver_setting = "unrecognised driver"

    log("Driver = %s, Headless mode = %s" %(driver_setting, headless_setting))

    pass


def read_data_from_file(file_name, line_num):
     
    if line_num == 0:
        #read all lines in file
        file_content = linecache.getlines(file_name)

        #remove newline from all lines
        for n, data in enumerate(file_content):
            file_content[n] = data.strip('\n')

    else:
        #read contents of file at line number
        file_content = linecache.getline(file_name, line_num)

        #remove newline from line
        file_content = file_content.strip('\n')

    #clear cache so can read most recent file next time
    linecache.clearcache 
     
    return file_content
    

def save_board_as_json(file_name, page_source):

    #edit page source to remove html and keep only json parts

    #split where json starts. by first instance of json formatting
    page_source_json = page_source.split('{"id"', 1)

    #add starting string back to split content
    page_source_json[1] = '{"id"' + page_source_json[1]

    #split where json ends. by html tags presence
    page_source_json = page_source_json[1].split('</', 1)

    #write modified file
    timestamp = datetime.now().strftime("_%d%m%Y")
    file_name = 'board_exports/' + file_name + timestamp + ".json"

    file = open(file_name, 'w')
    file.write(page_source_json[0])
    file.close

    log("file exported: %s" %file_name)

    return 0


def close():
    browser.close()
    time.sleep(3)
    quit()
    pass


def google():

    #control google search bar
    browser.get('https://google.com')

    # google_search = browser.find_element_by_xpath('//*[@id="tsf"]/div[2]/div[1]/div[1]/div/div[2]/input')
    google_search = browser.find_element_by_name('q')
    google_search.send_keys('Python docs')
    google_search.send_keys(Keys.ENTER)
    time.sleep(5)

    pass
   


def trello():

    browser.get('https://trello.com')

    #read file for login info
    my_email = read_data_from_file(script_config_file,2)
    my_pass = read_data_from_file(script_config_file,3)
    
    log("from file: my_email: %s, my_pass: ***" %my_email)  

    #find login
    action = browser.find_element_by_xpath('/html/body/header/nav/div/a[1]')
    action.click()

    #wait for email field
    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="user"]')))
    browser.find_element_by_xpath('//*[@id="user"]').send_keys(my_email) 

    #wait for atlassian button 
    wait = WebDriverWait(browser, 10)
    wait.until(EC.text_to_be_present_in_element_value((By.ID, 'login'), 'Atlassian'))
    action = browser.find_element_by_xpath('//*[@id="login"]')
    action.click()

    #wait for password field and login
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))) 
    action = browser.find_element_by_xpath('//*[@id="password"]').send_keys(my_pass, Keys.ENTER)  
    
    #wait for login to complete - when create new boards link is present
    wait = WebDriverWait(browser, 30)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.board-tile.mod-add'))) 

    #grab url of boards page
    boards_url = browser.current_url

    #read entire file to get list of boards
    file_data = read_data_from_file(script_config_file, 0)

    #remove items so we only have board info
    boards_list = file_data[3:]
    log("from file: boards to export: %s" %boards_list)

    #iterate over each board 
    for board_num, board_name in enumerate(boards_list, 1):

        #reload board url only after first export
        if(board_num > 1):
            browser.get(boards_url)
            
            #wait for page to load - when create new boards link is present
            wait = WebDriverWait(browser, 30)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.board-tile.mod-add')))

        #set xpath to board, translate phrase removes case sensitivity
        board_path = '//div[@title=translate("'+board_name+'","abcdefghijklmnopqrstuvwxyz","ABCDEFGHIJKLMNOPQRSTUVWXYZ")]' # without checking casing: '//div[@title="nameofboard"]'

        #click on board
        action = browser.find_element_by_xpath(board_path)
        action.click()

        #wait for board to fully load - when 'add another list' is present
        wait = WebDriverWait(browser, 30)
        wait.until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Add another list")]'))) 

        #open side menu
        #TODO prevent error from occuring
        try:
            action = browser.find_element_by_xpath('//span[contains(text(),"Show menu")]')
            action.click()
        except Exception as print_error:
            log("ERROR IGNORED")
            log(print_error)
            time.sleep(2)

        #select more option
        action = browser.find_element_by_xpath('//*[@id="content"]/div/div[2]/div/div/div[2]/div/ul[1]/li[5]/a')
        action.click()

        #print and export
        action = browser.find_element_by_xpath('//*[@id="content"]/div/div[2]/div/div/div[2]/div/ul[2]/li[4]/a')
        action.click()

        #export as json
        action = browser.find_element_by_xpath('//*[@id="chrome-container"]/div[4]/div/div[2]/div/div/div/ul/li[3]/a')
        action.click()
    
        #extract json in page and export to file
        save_board_as_json(board_name ,browser.page_source)
    pass      

pass



def main():

    try:
        log("--- start program ---")
        setup()
        # google()
        trello()
        close()
    
    except Exception as print_error:
        #TODO: how to combine print to file and stderr?
        traceback.print_exception(type(print_error), print_error, print_error.__traceback__, file=open("trello-scraping.log","a"))
        traceback.print_exception(type(print_error), print_error, print_error.__traceback__)


if __name__ == "__main__":
    main()
    pass

#end of file
