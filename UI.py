import tkinter as tk
import time
from OS_interface import System, MasterPasswordError

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

    * clear_frame: Clears the window of all widgets currently in the window 
                   (except for the menu buttons at the top)
    
    * _grid_frame: Grids the frame in its designated place

    * get_input: GUI replacement of python input function

    * _store_result: Stores the result for the get_input function

    * display_help: Displays the instructions on the GUI 
                   (Instruction message is in a work in progress)

    ! retrieve_pass: Retrieves a password for the user
    """
    instructions = "help"
    def __init__(self):
        #self.sys_obj = System(name="password.csv")
        self.authenticated = False
        self.root = tk.Tk()
        self.root.title("Password Manager")
        self.root.resizable(False, False)
        self.main_frame = tk.Frame(self.root)
        button_frame = tk.Frame(self.root)
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()

        # Chosen so window is essentially centered on the screen
        top_left = (width//6, height//10)
        self.root.geometry(f"{(2*width)//3}x{(2*height)//3}+{top_left[0]}+{top_left[1]}")
        tk.Button(button_frame, text="Help", command=self.display_help).pack(side="left")
        tk.Button(button_frame, text="Retrieve Password", command=self.retrieve_pass).pack(side="left")
        button_frame.place(relx=0.5, anchor="n") # Horizontally centering buttons
        self.root.after(1000, self.create_interfaces)
        self.root.mainloop()
    
    def create_interfaces(self):
        self.pass_int = System(name="password.csv", get_input=self.get_input)
        while not self.authenticated:
            try:
                self.pass_int.fileDecrypt()
                self.authenticated = True
            except MasterPasswordError:
                self.clear_frame()
                tk.Label(self.main_frame, text="Authentication Failed.").grid()
                self._grid_frame()
                self.root.update()
                time.sleep(1)
            

    def clear_frame(self):
        self.main_frame.destroy()
        self.main_frame = tk.Frame(self.root)
    
    def _grid_frame(self):
        self.main_frame.place(relx=0.5, rely=0.1)

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
        self.root.update()
        self.root.wait_variable(self.result)
        self.clear_frame()
        return self.result.get()
    
    def _store_result(self):
        result = self.txtbox.get("1.0", "end").strip().replace("\r", "")
        self.txtbox.delete("1.0", "end")
        if result:
            self.result.set(result)

    def display_help(self):
        if self.authenticated:
            self.clear_frame()
            tk.Label(self.main_frame, text=self.instructions).pack()
            self._grid_frame()

    def retrieve_pass(self):
        if self.authenticated:
            self.clear_frame()
            id = self.get_input("Enter the id of the password you would like to retrieve.")
            print(id)
        # To interface with Data Manager

if __name__ == "__main__":
    GUI()