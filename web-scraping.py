from selenium import webdriver


def setup_chrome():
    DRIVER_PATH = './chromedriver'
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    driver.get('https://google.com')
    print(driver.page_source)


def main():
    print("***start***")
    setup_chrome()

if __name__ == "__main__":
    main()
    pass