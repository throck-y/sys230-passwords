import base64
import time
import tkinter
import os
import sys
import random
import pathlib
import pandas as pd
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes


class System:
    """
    KEY:
        ~~internal use only~~ denotes that a function is primarily intended to be utilized within the class, not to
                              called externally (you *can* if you really want to but it might break something, as these
                              functions are also called within other functions and some aren't meant to be called twice)

        -All hashes are done in SHA256

    ====================================================================================================================
    :__init__: Initializes class object.
               :param name: string - optional file name
               :param get_input: function - solicits input from UI
               :param securityQ: boolean - indicates whether object is the security questions
               :return: None

    checkLegality: This is an attempt to avert an exception in the event that a file needs to be created
                   by making sure the user's inputted file name will be accepted by the host OS (Certain
                   characters/file names/etc are disallowed by the OS).
                   :param name: string - file name
                   :return: bool - indicates whether file name is legal
                   -----------------------------------------------------------------------------------------------------
                   calling this externally won't break anything but System handles this so it isn't really necessary
                   ~~internal use only ~~

    strHash: Returns a hash of the inputted string
             :param string_word: string - string to be hashed
             :return: string - SHA256 hash of input string
             -----------------------------------------------------------------------------------------------------------
             only call this if you're using it for your own class, don't pass a hash to System
             ~~internal use only~~

    firstTime: creates files if they are not found
               :param: None
               :return: None
               ---------------------------------------------------------------------------------------------------------
               System handles this, calling this externally will catastrophically break everything
               ~~internal use only~~

    fileExists: Checks to see if specified file exists
                :param name: string - file to look for
                :return: bool - indicates whether file was found
                --------------------------------------------------------------------------------------------------------
                calling this externally won't break anything but System handles this so it isn't really necessary
                ~~internal use only~~

    fileNameGet: Returns name of file
                 :param: None
                 :return: string - name of file

    fileOpen: Opens and decrypts file.
              :param: None
              :return: dataframe - decrypted dataframe read from file

    fileClose: Saves pd dataframe to file, encrypts file, closes file.
               :param: dataframe - changed dataframe to encrypt and save
               :return: None

    fileCreate: Creates file in the OS.
                  :param file: string - Name of file.
                  :param contents: string - optional contents to be written to file.
                  :return: None
                --------------------------------------------------------------------------------------------------------
                file creation is handled internally, calling this will probably overwrite something and break it
                ~~internal use only~~

    fileEncrypt: Encrypts file in OS. Used exclusively within fileClose
                 :param: None
                 :return: None
                 -------------------------------------------------------------------------------------------------------
                 we handled cryptography internally, using this outside of System it will break something
                 ~~internal use only~~

    fileDecrypt: Decrypts file in OS. Used exclusively within fileOpen
                 :param: None
                 :return: None
                 -------------------------------------------------------------------------------------------------------
                 we handled cryptography internally, using this outside of System it will break something
                 ~~internal use only~~

    SecQ: Handles decryption via security questions in the case of a forgotten password.
          :param: None
          :return: boolean - indicates whether questions were answered correctly
          --------------------------------------------------------------------------------------------------------------
          This function involves cryptography, so calling it will break something.
          ~~internal use only~~

    factoryReset: Factory reset. Deletes all files associated with the program and remakes them from scratch. Anything
                  currently saved will be lost.
                  :param: None
                  :return: None

    ====================================================================================================================
    FILES:
        key.key - symmetric encryption key
        security.csv - hashed security question answers (row 1 = plaintext q's, row 2 = answer hashes)
        password.csv - encrypted password file (row 1 = username, row 2 = password)
        mpass.txt - hashed master password

    ====================================================================================================================
    """

    def __init__(self, name='', get_input=input, securityQ=False):
        self.securityQ = securityQ
        self.fileName = name
        self.input = get_input
        if not self.checkLegality(name):
            raise Exception("Error - file name invalid")
        if not self.fileExists("mpass.txt") or not self.fileExists("key.key") or not self.fileExists(name):
            self.firstTime()

    def strHash(self, string_word):
        generate = hashes.Hash(hashes.SHA256())
        generate.update(string_word.encode())
        # The Finalize method is used to perform cleanup operations on unmanaged resources held
        # by the current object before the object is destroyed.
        return generate.finalize()

    def firstTime(self):
        if not self.fileExists("key.key"):
            create = open("key.key", 'x')
            create.close()
            create = open("key.key", 'wb')
            # Fernet guarantees that a message encrypted using it cannot be manipulated or read without the key.
            # Used in symmetric cryptography. Fernet key can be in bytes or string. generate_key() is in the Fernet library.
            create.write(Fernet.generate_key())
            create.close()

        # Create master password if the mpass file doesn't exist.
        if not self.fileExists("mpass.txt"):
            mpass = str(self.input("What would you like your master password to be?"))
            self.fileCreate("mpass.txt", str(self.strHash(mpass)))

        # If the password.csv does not exist, then create a csv file called "password.csv"
        if not self.fileExists("password.csv"):
            # print("Make the password file")
            self.fileCreate("password.csv")
        if not self.fileExists("security.csv"):
            qList = []
            aList = []
            while True:
                q = str(self.input("Please input a security question. Input 'stop' to stop."))
                if q == "stop":
                    break
                a = str(self.input("Please input an answer to said security question. (CASE SENSITIVE): "))
                qList.append(q)
                aList.append(a)

            # Reformats information to where the pandas dataframe can accept it. Prepping the data for pandas.
            SecurityToCsv = [[qList[a] for a in range(len(qList))], [self.strHash(aList[a]) for a in range(len(aList))]]
            secDF = pd.DataFrame(SecurityToCsv)
            print(secDF)
            # Where the inputted questions and the answers are written to the security.csv file.
            secDF.to_csv("security.csv", header=False, index=False)

    def checkLegality(self, name):  # Intended for internal use only
        illegalWin = ["\\/<>:\"\'|?*", "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6",
                      "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8",
                      "LPT9", ""]
        illegalMac = ["/", ":", "NUL", ""]
        illegalLinux = ["/", "NUL", ""]
        if sys.platform == "win32":  # windows
            winContentCheck = False
            for char in illegalWin[0]:  # checks for illegal chars in file name
                if char in name:
                    winContentCheck = True
            if winContentCheck or name.upper() in illegalWin or len(name) > 255 or name[-1] == '.':
                return False
            else:
                return True
        elif sys.platform == "darwin":  # macOS
            if name.upper() in illegalMac or len(name) > 255:
                return False
            else:
                return True
        elif sys.platform == "linux":  # linux
            if name.upper() in illegalLinux or len(name > 255):
                return False
            else:
                return True
        else:  # unsupported OS!
            return True

    def fileExists(self, name=''):
        return (name in os.listdir()) if name else (self.fileName in os.listdir())

    def fileNameGet(self):
        return self.fileName

    def fileOpen(self):
        if self.fileExists():
            if not self.securityQ:
                self.fileDecrypt()
            try:
                content = pd.read_csv(self.fileName, dtype=str, header=None, index_col=False)
            except pd.errors.EmptyDataError:
                content = pd.DataFrame(columns=("Username", "Password"))
            return content
        else:
            raise Exception("Error - File does not exist")

    def fileClose(self, panda):
        if not isinstance(panda, pd.DataFrame):
            raise PandasError()
        if self.securityQ == False:
            panda.to_csv(self.fileName, header=False, index=False)
            self.fileEncrypt()
        else:
            panda.iloc[1] = [self.strHash(x) for x in panda.iloc[1]]
            panda.to_csv(self.fileName, header=False, index=False)
        # self.fileName = ("password.csv")
        # directory = " "
        # filepath = directory + input("Enter filename: ")

    def fileCreate(self, file, contents=""):
        create = open(file, 'x')
        # print(file, contents)
        if contents != "":
            create.write(contents)
        create.close()
        print(file)

    def fileEncrypt(self):
        # Opens key.key file, keyStorage is the file object.
        # almostKey is the contents of key.key that has not been set to the symmetric key.
        keyStorage = open("key.key", 'rb')
        almostKey = keyStorage.read()
        # Fernet function = reads out the key.
        # key variable is the actual key.
        key = Fernet(almostKey)
        keyStorage.close()

        decryptedStorage = open(self.fileName, 'rb')
        decrypted = decryptedStorage.read()
        encrypted = key.encrypt(decrypted)
        decryptedStorage.close()

        # Open the file and write the encrypted string.
        encryptedStorage = open(self.fileName, 'wb')
        encryptedStorage.write(encrypted)
        encryptedStorage.close()

    def fileDecrypt(self):
        mPassFile = open("mpass.txt", 'r')
        mPass = mPassFile.read()
        print(mPass)
        mPassFile.close()
        while (True):
            verifyPassword = str(self.input("Please input your master password. (CASE SENSITIVE)"))
            if str(mPass) == str(self.strHash(verifyPassword)):
                break
                # decrypts if input hash matches stored hash
            else:  # security question else block
                check = str(self.input("Password incorrect. Type 'HELP' if you forgot your password."))
                if check == 'HELP':
                    # user opted for security questions
                    check = self.SecQ()
                    if check:
                        break
                        # correctly answered security question, decrypt
                    else:
                        raise MasterPasswordError()
                else:
                    raise MasterPasswordError()
        keyStorage = open("key.key", 'rb')
        almostKey = keyStorage.read()
        key = Fernet(almostKey)
        keyStorage.close()

        encryptedStorage = open(self.fileName, 'rb')
        encrypted = encryptedStorage.read()
        if encrypted:
            decrypted = key.decrypt(encrypted)
        else:
            decrypted = encrypted
        print(decrypted)
        encryptedStorage.close()
        decryptedStorage = open(self.fileName, 'wb')
        decryptedStorage.write(decrypted)
        decryptedStorage.close()

    def SecQ(self):
        qs = pd.read_csv('security.csv', dtype=str, header=None, index_col=False)
        ind = random.randint(0, len(qs.columns) - 1)  # selects random question
        ansHash = str(self.strHash(self.input(qs.iat[0, ind])))  # hashes user input to be compared to correct answer
        if ansHash == qs.iat[1, ind]:  # compares user input to expected input
            return True
        else:
            return False

    def factoryReset(self):
        if self.fileExists(self.fileName):
            os.remove(self.fileName)
        if self.fileExists("key.key"):
            os.remove("key.key")
        if self.fileExists("mpass.txt"):
            os.remove("mpass.txt")
        if self.fileExists("security.csv"):
            os.remove("security.csv")
        if self.fileExists("password.csv"):
            os.remove("password.csv")
        self.firstTime()


# Exceptions for errors
class FileError(Exception):
    '''
    Exceptions for errors
    '''
    pass


# Send a message if the master password is incorrect.
class MasterPasswordError(FileError):
    '''
    Send a message if the master password is incorrect.
    '''

    def __init__(self, message=''):
        default_message = "Master password is incorrect."
        super().__init__(message if message else default_message)


class FileTypeError(FileError):
    def __init__(self, message=''):
        default_message = "File cannot be accessed."
        super().__init__(message if message else default_message)


class PandasError(FileError):
    def __init__(self, message=''):
        default_message = "Input must be a pandas dataframe."
        super().__init__(message if message else default_message)
