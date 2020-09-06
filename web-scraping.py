from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from datetime import datetime
import linecache

logs = "web-scraping-log"

def setup():

    global browser

    #set chrome driver
    # DRIVER_PATH = './chromedriver'
    # browser = webdriver.Chrome(executable_path=DRIVER_PATH)
    
    #set firefox driver
    DRIVER_PATH = './geckodriver'
    browser = webdriver.Firefox(executable_path=DRIVER_PATH)
    pass


def read_line_from_file(file_name, line_num):
    
    #return contents of file at line number
    file_content = linecache.getline(file_name, line_num)

    #clear cache so can read most recent file next time
    linecache.clearcache 

    #remove new line from end of line
    file_content = file_content.strip('\n')

    print("line read: %s" %file_content)   
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
    file_name = file_name + timestamp + ".json"

    file = open(file_name, 'w')
    file.write(page_source_json[0])
    file.close

    print("file exported: %s" %file_name)

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
    my_email = read_line_from_file("web-scraping-info",1)
    my_pass = read_line_from_file("web-scraping-info",2)
    
    #find login
    action = browser.find_element_by_xpath('/html/body/header/nav/div[2]/a[1]')
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
    print(boards_url)

    #read file for list of boards, iterate over each 
    with open("web-scraping-info", 'r') as file:
        file_data = file.readlines()
        print("boards to export: %s" %file_data[2:])

        for line_num, line_data in enumerate(file_data, 1):

            #board list starts from line 3
            if(line_num >= 3):  
                
                #reload board url only after first export
                if(line_num > 3):
                    browser.get(boards_url)
                    #wait for page to load - when create new boards link is present
                    wait = WebDriverWait(browser, 30)
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.board-tile.mod-add')))

                board_name = line_data.strip('\n')

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
                    action = browser.find_element_by_xpath('//span[contains(text(),"Show Menu")]')
                    action.click()
                except Exception as print_error:
                    print("ERROR IGNORED")
                    print(print_error)
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
    print("--- start program ---")
    setup()
    # google()
    trello()
    close()
    pass


if __name__ == "__main__":
    main()
    pass

#end of file