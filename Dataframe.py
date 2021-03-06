import random
import string
# Module to create filesystem paths. We can use the touch() method.
import pandas as pd

#data manager class
class Data_Manager:
    #This initialises the dataframe
    def __init__(self, df, input_function=input):
        self.dataframe = df
        self.input_function = input_function
    #this adds a user with a password to the dataframe
    def add(self, username, passwd):
        # adds a user with their password
        index = len(self.dataframe.index)
        self.dataframe.loc[index, :] = [username, passwd]
    #removes the user with their password
    def remove(self, username):  # input a pandas dataframe
        # removes a user with their password

        index = int(self.dataframe[self.dataframe['Username'] == username].index.values)
        self.dataframe.drop(labels=[index], axis=0, inplace=True)

    def pwrandom(self):
        # generates a random password based on the length the user specifies
        length = int(self.input_function("What would you like the length of your password to be? "))

        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        numbers = string.digits
        symbols = string.punctuation

        all = lowercase + uppercase + numbers + symbols

        temp = random.sample(all, length)
        random_password = "".join(temp)

        return random_password
    #retrieves the data for a certain username
    def retrieve(self, username):
        return self.dataframe[self.dataframe['Username'] == username]