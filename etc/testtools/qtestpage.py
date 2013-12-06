# qtestpage.py - abstraction of the qunit test page for javascript unit tests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class QTestpage:
    def __init__(self, driver, url):
        self.driver = driver # web driver
        #self.driver.get("%s%s" % (url, '/static/templates/tests.html'))
        self.driver.get("%s%s" % (url, '/dev/static/src/tests.html'))
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID,"pkanban_testready")))
        
    def getTestResultSummary(self):
        return self.driver.find_element_by_id("qunit-testresult").text
    
    def getTestResults(self):
        return self.driver.find_element_by_id("qunit-tests").text
    