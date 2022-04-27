import tkinter as tk
import time
from pandas import DataFrame
from OS_interface3 import System, MasterPasswordError
from Dataframe import Data_Manager

class GUI:
    """
    KEY:
        * denotes that a function has been completed
        ! denotes that a function is a work in progress
        (function names that start with _) denotes that a function is primarily intended to be utilized within the
                              class, not to called externally (you *can* if you really want to but it might break
                              something, as these functions are also called within other functions and some aren't
                              meant to be called twice)

    ====================================================================================================================
    ! :__init__: Initializes class object

    * update_pass_csv: Updates password csv file

    * clear_frame: Clears the window of all widgets currently in the window 
                   (except for the menu buttons at the top)
    
    * _grid_frame: Grids the frame in its designated place

    * get_input: GUI replacement of python input function

    * _store_result: Stores the result for the get_input function

    ! create_interfaces: Creates OS interface with password file and conducts master password authentication

    * display_help: Displays the instructions on the GUI 
                   (Instruction message is in a work in progress)

    * retrieve_pass: Retrieves a password for the user

    * add_pass: Adds a password for the user (takes a parameter for custom password or not)

    * remove_pass: Removes a password for the user

    * list_usernames: Lists usernames of the user
    """
    instructions = ("Welcome to the Password Manager!\n"
                    "When first entering the password manager, you will be prompted to set up a master password and security questions.\n"
                    "To access other features of the manager, you will be asked to enter your master password.\n"
                    "To retrieve, remove, or generate a password, click the corresponding button and enter the associated username.\n"
                    "To add a custom password, click the corresponding button and enter your username/password.\n"
                    "To list all your usernames, click the corresponding button.\n")

    def __init__(self):
        #self.sys_obj = System(name="password.csv")
        self.authenticated = False
        self.root = tk.Tk()
        self.root.title("Password Manager")
        self.root.resizable(False, False)
        self.main_frame = tk.Frame(self.root)
        # button_frame = tk.Frame(self.root)
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()

        # Chosen so window is essentially centered on the screen
        top_left = (width//6, height//10)
        self.root.geometry(f"{(2*width)//3}x{(2*height)//3}+{top_left[0]}+{top_left[1]}")
        menu = tk.Menu(self.root)
        menu.add_command(label="Help", command=self.display_help)
        menu.add_command(label="Retrieve Password", command=self.retrieve_pass)
        menu.add_command(label="Add Custom Password", command=self.add_pass)
        menu.add_command(label="Remove Password", command=self.remove_pass)
        menu.add_command(label="Generate Password", command=lambda: self.add_pass(custom=False))
        menu.add_command(label="List Usernames", command=self.list_usernames)
        self.root.config(menu=menu)

        # tk.Button(button_frame, text="Help", command=self.display_help).pack(side="left")
        # tk.Button(button_frame, text="Retrieve Password", command=self.retrieve_pass).pack(side="left")
        # tk.Button(button_frame, text="Add Custom Password", command=self.add_pass).pack(side="left")
        # tk.Button(button_frame, text="Remove Password", command=self.remove_pass).pack(side="left")
        # tk.Button(button_frame, text="Generate Password", command=lambda: self.add_pass(custom=False)).pack(side="left")
        # tk.Button(button_frame, text="List Usernames", command=self.list_usernames).pack(side="left")
        # button_frame.place(relx=0.5, anchor="n") # Horizontally centering buttons
        self.root.after(1000, self.create_interfaces)
        self.root.mainloop()
        self.update_pass_csv()
        
    def update_pass_csv(self):
        self.pass_int.fileClose(self.manager.dataframe)

    def clear_frame(self):
        self.main_frame.destroy()
        self.main_frame = tk.Frame(self.root)
    
    def _grid_frame(self, x=0.3, y=0.1):
        self.main_frame.place(relx=x, rely=y)

    def get_input(self, prompt):
        """
        :param prompt: Input prompt
        :return: str, User input string
        """
        self.result = tk.StringVar()
        self.clear_frame()
        tk.Label(self.main_frame, text=prompt).grid(row=0)
        self.txtbox = tk.Text(self.main_frame, height=1, width=30)
        self.txtbox.grid(row=1, pady=10)
        self._grid_frame()
        tk.Button(self.main_frame, text="Enter", command=self._store_result).grid(row=1, column=1)
        self.txtbox.bind("<Return>", lambda event: self._store_result())
        self.root.update()
        self.root.wait_variable(self.result)
        self.clear_frame()
        val = self.result.get()
        print(val)
        return val
    
    def _store_result(self):
        result = self.txtbox.get("1.0", "end").strip().replace("\r", "")
        self.txtbox.delete("1.0", "end")
        if result:
            self.result.set(result)

    def create_interfaces(self):
        self.pass_int = System(name="password.csv", get_input=self.get_input)
        while not self.authenticated:
            try:
                df = self.pass_int.fileOpen()
                df.columns = ("Username", "Password")
                self.manager = Data_Manager(df, input_function=self.get_input)
                self.authenticated = True
                self.update_pass_csv()
            except MasterPasswordError:
                self.clear_frame()
                tk.Label(self.main_frame, text="Authentication Failed.").grid()
                self._grid_frame()
                self.root.update()
                time.sleep(1)

    def display_help(self):
        if self.authenticated:
            self.clear_frame()
            tk.Label(self.main_frame, text=self.instructions).pack()
            self._grid_frame(x=0.2)

    def retrieve_pass(self, prompt="view"):
        if self.authenticated:
            self.clear_frame()
            username = self.get_input(f"Enter the username of the password you would like to {prompt}.")
            result = self.manager.retrieve(username)
            if result.empty:
                tk.Label(self.main_frame, text=f"No passwords with username {username}").grid(row=0)
                self._grid_frame()
                return username, False
            result = result["Password"].to_string(index=False)
            #result = " username  password\n        1         2\n        2         3\n        4         5"
            if prompt == "view":
                tk.Label(self.main_frame, text=f"Passwords for {username}", font="BOLD").grid(row=0)
                tk.Label(self.main_frame, text=result).grid(row=1)
                self._grid_frame()
            return username, result
    
    def add_pass(self, custom=True):
        if self.authenticated:
            self.clear_frame()
            username = self.get_input("Enter the username of the new password.")
            if custom:
                password = self.get_input("Enter the password.")
            else:
                password = self.manager.pwrandom()
            self.manager.add(username, password)
            self.update_pass_csv()
            tk.Label(self.main_frame, text="Password Stored!").grid(row=0)
            self._grid_frame()
    
    def remove_pass(self):
        if self.authenticated:
            username, result = self.retrieve_pass(prompt="delete")
            if result is not False:
                choice = ""
                while choice != "Y" and choice != "N":
                    choice = self.get_input(f"The password is {result}.\n\nAre you sure you would like to delete this? (Enter Y/N)")
                if choice.upper() == "Y":
                    self.manager.remove(username)
                    self.update_pass_csv()
                    tk.Label(self.main_frame, text="Deleted!").grid(row=0)
                    self._grid_frame()
                else:
                    tk.Label(self.main_frame, text="No modifications were made.").grid(row=0)
                    self._grid_frame()
    
    def list_usernames(self):
        if self.authenticated:
            self.clear_frame()
            names = self.manager.dataframe["Username"]
            if names.empty:
                tk.Label(self.main_frame, text="No usernames or passwords stored.").grid(row=0)
            else:
                tk.Label(self.main_frame, text="Usernames", font="BOLD").grid(row=0)
                tk.Label(self.main_frame, text=names.to_string(index=False)).grid(row=1)
            self._grid_frame()

if __name__ == "__main__":
    GUI()