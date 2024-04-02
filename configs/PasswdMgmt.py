import os
import sys

from cryptography.fernet import Fernet


class PasswdMgmt:
    repo = None
    username = None
    password = None
    key = None

    password_and_repo_path = 'configs/pass_and_repo.ini'

    def get_repo(self):
        return self.repo

    def get_username(self):
        return self.username

    def get_password(self):
        return self.decrypt_password()

    def encrypt_password(self):
        f = Fernet(self.key)
        encrypted_password = f.encrypt(self.password.encode())
        return encrypted_password

    def decrypt_password(self):
        f = Fernet(self.key)
        encrypted_password = self.password.encode()[len('encrypted:'):]
        decrypted_password = f.decrypt(encrypted_password).decode()
        return decrypted_password

    def __init__(self):
        # if password file is not exist, then create
        if not os.path.exists(self.password_and_repo_path):
            with open(self.password_and_repo_path, 'w') as configfile:
                configfile.write("repo: \n")
                configfile.write("username: \n")
                configfile.write("password: \n")
                configfile.write("key: " + Fernet.generate_key().decode() + "\n")
            print(
                "The config.ini is created. Please enter your username, password and epg directory in it. "
                "Do not worry! This will be encrypted on the second run.")
            sys.exit(0)

        # Configuration reading
        with open(self.password_and_repo_path, 'r') as configfile:
            lines = configfile.readlines()
            for i in lines:
                if i.startswith("repo"):
                    self.repo = i.split("repo:")[1].strip()
                if i.startswith("username"):
                    self.username = i.split("username:")[1].strip()
                if i.startswith("password"):
                    self.password = i.split("password:")[1].strip()
                if i.startswith("key"):
                    self.key = i.split("key:")[1].strip().encode()

        # Check if it is encrypted
        if not self.password.startswith('encrypted:'):
            # in not then encrypt
            encrypted_password = self.encrypt_password()
            self.password = 'encrypted:' + encrypted_password.decode()

            with open(self.password_and_repo_path, 'w') as configfile:
                configfile.write("repo: " + self.repo + "\n")
                configfile.write("username: " + self.username + "\n")
                configfile.write("password: " + self.password + "\n")
                configfile.write("key: " + self.key.decode('ascii') + "\n")
