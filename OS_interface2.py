# Runs the python file in 64-bit
import base64
import time
import tkinter
# Allow program to integrate with the OS
import os
import sys
import random
# Module to create filesystem paths. We can use the touch() method.
import pathlib
import pandas as pd
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes


# We are accepting dataframes coming in the file, and using them to create the tools necessary
# to create the UI. This code does not create the UI.

# input_function = input
# We are not populating anything
class System:
    """
    KEY:
        ~~internal use only~~ denotes that a function is primarily intended to be utilized within the class, not to
                              called externally (you *can* if you really want to but it might break something, as these
                              functions are also called within other functions and some aren't meant to be called twice)

    ====================================================================================================================
    :__init__: Initializes class object.

    checkLegality: This is an attempt to avert an exception in the event that a file needs to be created
                   by making sure the user's inputted file name will be accepted by the host OS (Certain
                   characters/file names/etc are disallowed by the OS).
                   :param: - file name
                   :return: bool - true for legal, false for illegal
                   calling this externally won't break anything but System handles this so it isn't really necessary
                   ~~internal use only ~~
    
    strHash: Returns a hash of the inputted string
             only call this if you're using it for your own class, don't pass a hash to System\
             ~~internal use only~~
    
    firstTime: creates files if they are not found
               System handles this, calling this externally will catastrophically break everything
               ~~internal use only~~

    fileExists: Checks to see if specified file exists
                :return: bool - true if found and false if not found
                calling this externally won't break anything but System handles this so it isn't really necessary
                ~~internal use only~~

    fileNameGet: Returns name of file
                 :return: string, name of file
                 

    fileOpen: Opens and decrypts file.
              :return: - pd dataframe

    fileClose: Saves pd dataframe to file, encrypts file, closes file.
               :param: Accepts pd dataframe as input.

    fileCreate: Creates file in the OS.
                file creation is handled internally, calling this will probably overwrite something and break it
                ~~internal use only~~

    fileEncrypt: Re-encrypts file before closing. Used exclusively within fileClose
                 we handled cryptography internally, using this outside of System it will probaably break something
                 ~~internal use only~~ 
                 
    fileDecrypt: Decrypts opened file. Used exclusively within fileOpen
                 we handled cryptography internally, using this outside of System it will probably break something
                 ~~internal use only~~
    ====================================================================================================================
    Primary external methods:
        -open file
            -decrypt file
                -via method
            -return pd dataframe from file
            -raise exception if file not found
        -close file
            -encrypt pd dataframe
                -via method
            -save to file
                -via method(?)
            -close file object
    ====================================================================================================================
    """

    # Maybe we could add a key to each python file.
    def __init__(self, name='', get_input=input, securityQ=False):
        self.securityQ = securityQ
        self.fileName = name
        self.input = get_input
        if not self.checkLegality(name):
            raise Exception("Error - file name invalid")
        if not self.fileExists("mpass.txt") or not self.fileExists("key.key") or not self.fileExists(name):
            self.firstTime()

    # This generates a SHA256 hash when the user self.inputs a string and it will
    # return the string hashed.
    def strHash(self, string_word):
        generate = hashes.Hash(hashes.SHA256())
        generate.update(string_word.encode())
        # The Finalize method is used to perform cleanup operations on unmanaged resources held
        # by the current object before the object is destroyed. The method is protected and therefore
        # is accessible only through this class or through a derived class.
        return generate.finalize()

    # FirstTime finds if the mpass, key.key, password.csv, and the security.csv exist.
    # if they don't then create those files.
    def firstTime(self):
        # key.key file is symmetric key (used for all cryptography), stuff being used to encrypt and decrypt
        # the passwords. The same key encrypts and decrypts.
        if not self.fileExists("key.key"):
            create = open("key.key", 'x')
            create.close()
            # Indicates file is opened for writing in binary mode.
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
        # Since we're soliciting input from the ui we'll have to populate it with usernames/password manually.
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

    # This is an attempt to avert an exception in the event that a file needs to be created
    # by making sure the user's inputted file name will be accepted by the host OS (Certain
    # characters/file names/etc are disallowed by the OS).
    def checkLegality(self, name):  # Intended for internal use only
        """
        illegalOS variables: these are just lists of specifically blacklisted filenames/characters in OS
                             IF statement syntax is: if <bad_char> or <bad_name> or <bad_length> (or if <os_specific>)

        winContentCheck: boolean - true if filename contains illegal characters, false if filename is fine

        :param name: file name
        :return: boolean - false indicates illegal, true indicates legal
        """
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

    # This function determines if specified file exists
    # It will return a boolean - true if found and false if not found
    # This runs internally, we do not see it run. ~~internal use only~~
    def fileExists(self, name=''):
        """
        :param name: file name
        :return: boolean, true - file was found, false - file was not found
        """
        return (name in os.listdir()) if name else (self.fileName in os.listdir())

    def fileNameGet(self):
        return self.fileName

    # Open the pandas dataframe.
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

    # The pandas dataframe is changed and needs to be updated.
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
        """
        :param file: Name of file.
        :param contents: Optional - contents to be written to file.
        :return: Nothing - file is created, with optional content
        """
        # 'x' is only writeable
        create = open(file, 'x')
        #print(file, contents)
        if contents != "":
            create.write(contents)
        create.close()
        print(file)

    def fileEncrypt(self):
        """
        :param file: file name
        :return: nothing, inputted file is now encrypted and unreadable on disk
        """
        # Opens key.key file, keyStorage is the file object.
        # almostKey is the contents of key.key that has not been set to the symmetric key.
        # 'rb' - read in binary.
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

    def fileDecrypt(self, input_function=input):
        """
        :param input_function:
        :param file: file name
        :return: nothing, inputted file is now decrypted and readable on disk
        """
        verifyPassword = str(self.input("Please input your master password. (CASE SENSITIVE)"))
        mPassFile = open("mpass.txt", 'r')
        mPass = mPassFile.read()
        print(mPass)
        mPassFile.close()
        if str(mPass) == str(self.strHash(verifyPassword)):
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
        else:
            # raise Exception("Error - Master Password Incorrect")
            raise MasterPasswordError()

# Exceptions for errors
class FileError(Exception):
    pass

class MasterPasswordError(FileError):
    # Send a message if the master password is incorrect.
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


# Perform function calls here.
#if __name__ == '__main__':
    #print("Working")
    #x = System("password.csv")
    #y = System("security.csv")
    #x.fileEncrypt()
    #y.fileEncrypt()
    #x.fileDecrypt()
    #y.fileDecrypt()

"""
password.csv
    -2 row csv file: r1=username, r2=pass
    -file, not contents, is encrypted with Cryptography

master password file
    -1 word txt file
    -stores hashed password to encrypted password.csv
    -to open password.csv: user inputs password, input is hashed and compared against the hash stored here: pass.csv is
     decrypted if they match
    
security.csv
    -2 row csv file: r1=question, r2=hashed answer
    -stores security questions and answers
    -questions are plaintext, answers are hashed
        -same as master password file: user input is hashed and compared to what is stored

key.key
    -1 word txt file
    -key, stored in bytes

-create files if missing
-read files if files present, return pd dataframe
    -encrypt and decrypt should be internal use only
"""