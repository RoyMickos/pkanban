"""
A class that runs javascript unit test page and reports the results
"""

import unittest
#from selenium.webdriver.firefox.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import qtestpage
from time import sleep

class TestQUnit(unittest.TestCase):
    #fixtures = ['user-data.json']
    live_server_url = "http://localhost:4000"

    @classmethod
    def setUpClass(cls):
        #cls.selenium = WebDriver()
        cls.selenium = webdriver.Chrome()
        super(TestQUnit, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(TestQUnit, cls).tearDownClass()

    def test_qunit_result(self):
        qtestPage = qtestpage.QTestpage(self.selenium, self.live_server_url)
        # we need to wait for the unit tests to execute
        sleep(10)
        resultfile = open("qunit_result.txt", "w")
        results = qtestPage.getTestResults()
        resultfile.write(results)
        resultfile.close()
        print qtestPage.getTestResultSummary()
        self.assertTrue(results is not None)
        

def suite():
    qtestSuite = unittest.TestLoader().loadTestsFromTestCase(TestQUnit)
    return qtestSuite

if __name__ == '__main__':
    unittest.main()
