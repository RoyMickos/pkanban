# mainpage.py - abstraction of pkanban's main SPA page using Page object pattern
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class ElementNotFound(Exception):
    def __init__(self, elemName, msg):
        self.elemName = elemName
        self.msg = msg

class PomodoroTimer:
    def __init__(self,driver):
        self.driver = driver
        self.widget = self.driver.find_element_by_id("pkpomodoro")
        if self.widget is None:
            raise ElementNotFound("pkpomodoro", "No such id found by driver")
        
    def click(self):
        self.widget.click()
        
    def getValue(self):
        return self.widget.text
        

class MainPage:
    
    def __init__(self, driver, url):
        self.driver = driver # web driver
        # this is a SPA application, so to verify we will need to wait until js
        # has generated the page
        self.driver.get("%s%s" % (url, '/pkanban'))
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID,"pkmessage_area")))
            
    def getMessage(self):
        return self.driver.find_element_by_id("pkmessage_area").text
    
    def getPomodoro(self):
        return PomodoroTimer(self.driver)
    