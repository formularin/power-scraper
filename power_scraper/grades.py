import os
from os.path import abspath, dirname, isfile

from cryptography.fernet import Fernet
from selenium.webdriver import Chrome


HOME = '/'.join(abspath(dirname(__file__)).split('/')[:3])


def main(username, password, district):
    """Scrapes powerschool and gives all grades"""

    print(username, password, district)


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
