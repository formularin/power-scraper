import os
from os.path import abspath, dirname, isfile
import time

from cryptography.fernet import Fernet
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


CWD = abspath(dirname(__file__))
HOME = '/'.join(CWD.split('/')[:3])


def wait_for_element(driver, selector, method):
    """Returns element after waiting for page load"""
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(
            eval(f'EC.presence_of_element_located((By.{method}, "{selector}"))')
        )
    finally:
        element = eval(f'driver.find_element_by_{method.lower()}("{selector}")')

    return element


def main(username, password, district):
    """Scrapes powerschool and gives all grades"""

    options = ChromeOptions()
    options.add_argument('headless')
    driver = Chrome(f'{CWD}/chromedriver', options=options)

    driver.get(f'https://powerschool.{district}.org/public/')

    username_input = driver.find_element_by_id("fieldAccount")
    username_input.send_keys(username)
    username_input.send_keys(Keys.TAB)

    password_input = driver.find_element_by_id("fieldPassword")
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)


if __name__ == '__main__':

    if not isfile(f'{HOME}/.user-secrets'):
        
        # generate encryption key
        key = Fernet.generate_key()
        with open(f'{HOME}/.key.key', 'wb') as f:
            f.write(key)

        # get user info
        user_secrets = []
        user_secrets.append(input('Username: '))
        os.system("stty -echo")
        user_secrets.append(input('Password: '))
        os.system("stty echo")
        print()
        user_secrets.append(input('District (url to sign in is powerschool.THIS.org): '))

        # write encrypted message to file
        bytes_info = '\n'.join(user_secrets).encode()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(bytes_info)

        with open(f'{HOME}/.user-secrets', 'wb') as f:
            f.write(encrypted)

    # read key from file
    with open(f'{HOME}/.key.key', 'rb') as f:
        key = f.read()

    fernet = Fernet(key)
    
    # read encrypted message
    with open(f'{HOME}/.user-secrets', 'rb') as f:
        encrypted = f.read()

    user_secrets = fernet.decrypt(encrypted).decode('utf-8').split('\n')

    main(*user_secrets)
