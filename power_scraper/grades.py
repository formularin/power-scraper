from os.path import abspath, dirname, isfile
import os

from selenium.webdriver import Chrome

from encrypt import encrypt, decrypt

HOME = '/'.join(abspath(dirname(__file__)).split('/')[:3])


def main(username, password, district):
    """Scrapes powerschool and gives all grades"""


if __name__ == '__main__':
    
    if not isfile(f'{HOME}/.user-secrets'):
        user_secrets = []
        user_secrets.append(input('Username: '))
        os.system("stty -echo")
        user_secrets.append(input('Password: '))
        os.system("stty echo")
        print()
        user_secrets.append(input('District (url to sign in is powerschool.THIS.org): '))
        with open(f'{HOME}/.user-secrets', 'w+') as f:
            f.write(encrypt('\n'.join(user_secrets)))
    
    with open(f'{HOME}/.user-secrets', 'r') as f:
        user_secrets = decrypt(f.read().split('\n'))

    main(*user_secrets)
