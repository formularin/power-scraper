"""
Usage:
python report.py [--name|--room|--teacher|--teacher-email] <classes> <grades>
"""


from collections import OrderedDict
from os.path import abspath, dirname, isfile
import os
import sys

from cryptography.fernet import Fernet
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


CWD = abspath(dirname(__file__))
HOME = '/'.join(CWD.split('/')[:3])


def wait_for_element(driver, selector, method, plural=False):
    """Returns element after waiting for page load"""

    try:
        wait = WebDriverWait(driver, 10)
        wait.until(
            eval(f'EC.presence_of_element_located((By.{method}, "{selector}"))')
        )
    finally:
        if plural:
            element = eval(f'driver.find_elements_by_{method.lower()}("{selector}")')
        else:
            element = eval(f'driver.find_element_by_{method.lower()}("{selector}")')

    return element


def main(username, password, url, classes, 
         grades, room, teacher, teacher_email):
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
    
    room : bool, optional
        Whether or not to return the room number of each class in `classes`
    
    teacher : bool, optional
        Whether or not to return the name of the teacher of each class in `classes`
    
    teacher_email : bool optional
        Whether or not to return the email of the teacher of each class in `classes`

    Returns
    -------
    list of dict with keys and values str
        Each dict represents a class, with each key being either a grade (ex. "Q1"),
        or an info category (ex. "TEACHER"), and each value being a string corresponding to that key.
    """
    
    class_dicts = []  # contains dicts representing each class

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

    class_rows = wait_for_element(driver, "//tr[@class='center']", "XPATH", plural=True)[:-1]

    # get column indices of grades
    grades_row = driver.find_element_by_xpath("//tr[@class='center th2'][1]")
    grade_headers = grades_row.find_elements_by_xpath('.//*')[4:-2]
    grade_header_texts = [th for th in grade_headers if th.text in grades]
    grade_column_indices = [grade_headers.index(th) for th in grade_header_texts]

    for row in class_rows:

        class_info = OrderedDict()

        # meta info
        meta_info_td = row.find_element_by_xpath('.//td[@align="left"]')
        meta_info = meta_info_td.text

        class_name = meta_info.split('\n')[0][:-1]
        if class_name not in classes:
            continue

        if teacher_email or teacher:
            email_link = meta_info_td.find_element_by_xpath('.//a[2]')
        
        class_info["Name"] = class_name
        if room:
            class_info["Room"] = meta_info.split('Rm: ')[-1]
        if teacher:
            class_info["Teacher"] = email_link.text[6:-1]
        if teacher_email:
            class_info["Teacher-email"] = email_link.get_attribute('href')[7:]

        # grades
        grade_columns = [td for td in row.find_elements_by_xpath(".//td")
                            if len(td.find_elements_by_xpath(".//a")) == 1]
        scores = [grade_columns[i].find_element_by_xpath('.//a').text
                                for i in grade_column_indices]
        for grade, score in zip(grades, scores):
            class_info[grade] = score

        class_dicts.append(class_info)

    return class_dicts


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

    username, password, url = fernet.decrypt(encrypted).decode('utf-8').split('\n')

    # argument handling for cli to function input
    old_kwargs = {
        "room": False,
        "teacher": False,
        "teacher_email": False,
        "username": username,
        "password": password,
        "url": url,
        "classes": [],
        "grades": [],
    }
    kwargs = OrderedDict(old_kwargs.items())
    arg_num = 0
    lists = ["classes", "grades"]

    for arg in sys.argv[1:]:
        if '--' in arg:
            kwargs[arg[2:]] = True
        else:
            kwargs[lists[arg_num]] = arg.split(';')
            arg_num += 1

    classes = main(**kwargs)

    output_rows = []

    # get headers row
    headers = []
    items = [i for i in kwargs.items()
             if "username" not in i
             and "password" not in i
             and "url" not in i
             and "classes" not in i]
    for k, v in items:
        if not v:
            continue
        if k == "grades":
            for grade in v:
                headers.append(grade)
        else:
            headers.append(k)
    
    formats = ['{:20}' for _ in range(len(headers))]
    headers_row = ' '.join(formats).format(*headers)
    output_rows.append(headers_row)

    # get class rows
    for course in classes:
        output_rows.append(' '.join(formats).format(*list(course.values())))

    # get divider row
    n_dashes = (max([len(i) for i in output_rows]) - 20 + 
                max([len(list(course.values())[-1]) for course in classes]))
    divider_row = ''.join(['-' for _ in range(n_dashes)])
    output_rows.insert(1, divider_row)

    print('\n'.join(output_rows))
