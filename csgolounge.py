from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
import math
options = webdriver.ChromeOptions()
options.add_argument("--enable-javascript")
options.add_argument("--enable-cookies")
chrome_options = webdriver.ChromeOptions(); 
chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
driver = webdriver.Chrome(executable_path = "./chromedriver", chrome_options = options)
driver.get('https://csgolounge.com/')
time.sleep(99999)
soup = BeautifulSoup(driver.page_source, "html5lib")
print(soup.get_text())

