"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase 
import unittest
from django.test import LiveServerTestCase
#from selenium.webdriver.firefox.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import mainpage
from time import sleep

class TestMainView(LiveServerTestCase):
    #fixtures = ['user-data.json']

    @classmethod
    def setUpClass(cls):
        #cls.selenium = WebDriver()
        cls.selenium = webdriver.Chrome()
        super(TestMainView, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(TestMainView, cls).tearDownClass()

    def test_main_page(self):
        mainPage = mainpage.MainPage(self.selenium, self.live_server_url)
        pomis = mainPage.getPomodoro()
        self.assertTrue(pomis.getValue() == "0:00", "Pomodoro loaded")
        print "message:"
        print mainPage.getMessage()
        self.assertTrue(mainPage.getMessage() == "")
        """
        self.selenium.get("%s%s" % (self.live_server_url, '/pkanban'))
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID,"pkmessage_area")))
        #backlog_element = self.selenium.find_element_by_xpath("//body")
        pomodoro_element = self.selenium.execute_script("return document.getElementById('pkpomodoro')")
        #print pomodoro_element
        self.assertTrue(pomodoro_element is not None)
        """
        
    def test_pomodoro_short(self):
        """ test_pomodoro
        test the pomodoro timer widget on the main view, short test (not testing expiration of the timer)
        """
        mainPage = mainpage.MainPage(self.selenium, self.live_server_url)
        # start with plain view and no task selected - basic timer operations
        pomis = mainPage.getPomodoro()
        self.assertTrue(pomis.getValue() == "0:00")
        pomis.click()
        sleep(2)
        pomis.click()
        aValue = pomis.getValue()
        self.assertTrue(aValue != "0:00")
        sleep(2)
        self.assertTrue(pomis.getValue() == aValue)
        

def suite():
    mainViewSuite = unittest.TestLoader().loadTestsFromTestCase(TestMainView)
    return mainViewSuite
