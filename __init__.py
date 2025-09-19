
## Selenium Imports ##
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys    
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import webdriver_manager
except Exception as e:
    print(f'[PySBK::Selenium] Import error: {e}')
    
## PySBK Imports ##    
try:
    from PySBK import __about__ as about
    from PySBK.sebrowser import SeleniumBrowser
    from PySBK.sbk import PySBK
except Exception as e:
    print(f'[PySBK] Import Error: {e}')

## Wildcard Importing ##    
__selenium__ = ["By", "EC", "Keys", "WebDriverWait"]
__PySBK__ = ["about", "PySBK", "SeleniumBrowser"]
__all__ = __PySBK__ + __selenium__

## Package Metadata ##
__project_name__ = about.name
__version__ = about.version
__author__ = about.author
__license__ = about.license
__homepage__ = about.homepage



