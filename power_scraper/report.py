from os.path import abspath, dirname, isfile
import os

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


def main(username, password, url, classes, grades, 
         name=True, room=True, teacher=True, teacher_email=True):
    """Scrapes powerschool and returns grades and other info according to input
    
    Parameters
    ----------
    username : str
        Powerschool username (required to sign in to access grades).
        Either specified on script run or stored in file.
    
    password : str
        Powerschool password (required to sign in to access grades),
        Either specified on script run or stored in file.
    
    url : str
        URL to sign in page (ex. powerschool.niskyschools.org)
    
    classes : list of str or "ALL"
        Names of classes to return info about. "ALL" signifies all classes.
    
    grades : list of str or "ALL"
        Names of grades to return for each class in `classes`. (ex. "Q1")
        "ALL" signifies all grades.
    
    name : bool, optional
        Whether or not to return the name of each class in `classes`
        (Default value is True)
    
    room : bool, optional
        Whether or not to return the room number of each class in `classes`
        (Default value is True)
    
    teacher : bool, optional
        Whether or not to return the name of the teacher of each class in `classes`
        (Default value is True)
    
    teacher_email : bool optional
        Whether or not to return the email of the teacher of each class in `classes`
        (Default value is True)

    Returns
    -------
    list of dict with keys and values str
        Each dict represents a class, with each key being either a grade (ex. "Q1"),
        or an info category (ex. "TEACHER"), and each value being a string corresponding to that key.
    """

    classes = []  # contains dicts representing each class

    options = ChromeOptions()
    options.add_argument('headless')
    driver = Chrome(f'{CWD}/chromedriver', options=options)

    driver.get(url)

    # sign in
    username_input = wait_for_element(driver, "fieldAccount", "ID")
    username_input.send_keys(username)
    username_input.send_keys(Keys.TAB)

    password_input = driver.find_element_by_id("fieldPassword")
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)

    class_rows = driver.find_elements_by_xpath('//tr[@class="center"]')[:-1]
    for row in class_rows:
        
        class_info = {}

        # meta info
        meta_info_td = row.find_element_by_xpath('.//td[@align="left"]')
        meta_info = meta_info_td.text
        if teacher_email or teacher:
            email_link = meta_info_td.find_element_by_xpath('.//a[2]')
        
        if name:
            class_info["NAME"] = meta_info.split('\n')[0][:-1]
        if room:
            class_info["ROOM"] = meta_info.split('Rm: ')[-1]
        if teacher:
            class_info["TEACHER"] = email_link.text[6:-1]
        if teacher_email:
            class_info["TEACHER_EMAIL"] = email_link.get_attribute('href')[7:]

        classes.append(class_info)

    return classes


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
        user_secrets.append(input('URL to sign in page: '))

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
