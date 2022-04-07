import random
import string
# Module to create filesystem paths. We can use the touch() method.
import pandas as pd


class Data_Manager:
    def __init__(self, df):
        self.dataframe = df

    def add(self, username, passwd):
        # adds a user with their password
        index = len(self.dataframe.index)
        self.dataframe.loc[index, :] = [username, passwd]

    def remove(self, username):  # input a pandas dataframe
        # removes a user with their password

        index = int(self.dataframe[self.dataframe['Username'] == username].index.values)
        self.dataframe.drop(labels=[index], axis=0, inplace=True)

    def pwrandom(self):
        # generates a random password based on the length the user specifies
        length = int(input("What would you like the length of your password to be? "))

        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        numbers = string.digits
        symbols = string.punctuation

        all = lowercase + uppercase + numbers + symbols

        temp = random.sample(all, length)
        random_password = "".join(temp)

        return random_password

    def retrieve(self, username):
        return self.dataframe[self.dataframe['Username'] == username]