import threading
import tkinter as tk
from tkinter import messagebox
from account import AccountDAO
from client import Client
from game import Game


class Login:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False,False)
        self.root.config(bg = '#d28c45')
        self.frame = tk.Frame(self.root,bd = 30, bg = '#ffcf9f')

        # Load images
        self.login_icon = tk.PhotoImage(file = 'img/icon.png')
        self.entry_box = tk.PhotoImage(file = 'img/entry.png')
        self.login_button_box = tk.PhotoImage(file = 'img/login-button.png')
        self.register_button_box = tk.PhotoImage(file='img/register-button.png')

        # Create widget
        self.username_entry_box = tk.Label(self.frame, image = self.entry_box, bg = '#ffcf9f')
        self.username_entry = tk.Entry(self.frame, width=20, font=("anything", 16), relief= tk.FLAT, fg = 'gray')
        self.password_entry_box = tk.Label(self.frame, image=self.entry_box, bg='#ffcf9f')
        self.password_entry = tk.Entry(self.frame, width=20, font=("anything", 16), relief=tk.FLAT, fg = 'gray')
        self.login_button = tk.Button(self.frame, text="Login",font=("anything", 16),image=self.login_button_box,
                                       command=self.login, cursor='hand2',fg = 'white', bg='#ffcf9f', activeforeground='white',
                                       activebackground='#ffcf9f', borderwidth = 0,relief=tk.FLAT, compound='center')
        self.register_button = tk.Button(self.frame, text="Register",font=("anything", 16),image=self.register_button_box,
                                       command=self.register, cursor='hand2',fg = 'white', bg='#ffcf9f', activeforeground='white',
                                       activebackground='#ffcf9f', borderwidth = 0,relief=tk.FLAT, compound='center')

        self.window_width = 600
        self.window_height = 500

    def init_window(self):
        self.center_window()
        self.root.title("Login")
        self.root.iconphoto(True, self.login_icon)
        self.frame.pack(expand=True)

        # Insert initial text for username and password entry
        self.username_entry.insert(0, 'username')
        self.password_entry.insert(0, 'password')

        # Initial text disappear when user interact
        self.username_entry.bind("<FocusIn>", self.username_entry_click)
        self.username_entry.bind("<FocusOut>", self.username_entry_leave)
        self.password_entry.bind("<FocusIn>", self.password_entry_click)
        self.password_entry.bind("<FocusOut>", self.password_entry_leave)

        # Center all widgets
        self.username_entry_box.place(x = 0,y = -8)
        self.username_entry.pack(pady = 10)
        self.username_entry.bind("<Return>", lambda e: self.login())
        self.password_entry_box.place(x = 0, y = 62)
        self.password_entry.pack(pady = 30)
        self.password_entry.bind("<Return>", lambda e: self.login())

        self.login_button.pack(pady = 10)
        or_label = tk.Label(self.frame, text = 'or', font=("anything", 16), fg = 'white', bg = '#ffcf9f')
        or_label.pack()
        self.register_button.pack(pady = 10)

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2

        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        account = AccountDAO().get_by_user_and_pass(username, password)
        if account:
            messagebox.showinfo("Success", f"Welcome {account.username}")
            self.root.destroy()
            home = Home(account.account_id)
            home.init_window()
            home.root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid Information")

    def register(self):
        self.root.destroy()
        register = Register()
        register.init_window()
        register.root.mainloop()

    def username_entry_click(self,event):
        if self.username_entry.get() == 'username':
            self.username_entry.delete(0, "end")
            self.username_entry.config(fg="black")  # Change text color to black

    def password_entry_click(self,event):
        if self.password_entry.get() == 'password':
            self.password_entry.delete(0, "end")
            self.password_entry.config(fg="black", show = '*')  # Change text color to black

    def username_entry_leave(self, event):
        if self.username_entry.get() == "":
            self.username_entry.insert(0, 'username')
            self.username_entry.config(fg="gray")  # Change text color to gray
    def password_entry_leave(self,event):
        if self.password_entry.get() == "":
            self.password_entry.insert(0, 'password')
            self.password_entry.config(fg="gray",show = "")  # Change text color to gray

class Register:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.config(bg='#d28c45')
        self.frame = tk.Frame(self.root, bd=30, bg='#ffcf9f')

        # Load images
        self.entry_box = tk.PhotoImage(file='img/entry.png')
        self.register_button_box = tk.PhotoImage(file='img/register-button.png')
        self.return_button_box = tk.PhotoImage(file='img/return-button.png')

        # Create widget
        self.username_entry_box = tk.Label(self.frame, image=self.entry_box, bg='#ffcf9f')
        self.username_entry = tk.Entry(self.frame, width=20, font=("anything", 16), relief=tk.FLAT, fg='gray')
        self.password_entry_box = tk.Label(self.frame, image=self.entry_box, bg='#ffcf9f')
        self.password_entry = tk.Entry(self.frame, width=20, font=("anything", 16), relief=tk.FLAT, fg='gray')
        self.register_button = tk.Button(self.frame, text="Register", font=("anything", 16),
                                         image=self.register_button_box, command=self.register,
                                         cursor='hand2', fg='white', bg='#ffcf9f', activeforeground='white',
                                         activebackground='#ffcf9f', borderwidth=0, relief=tk.FLAT, compound='center')
        self.return_button = tk.Button(self.root, image = self.return_button_box, command=self.go_back,
                                         cursor='hand2', bg='#d28c45', activebackground='#d28c45', borderwidth=0, relief=tk.FLAT)

        self.window_width = 600
        self.window_height = 500

    def init_window(self):
        self.center_window()
        self.root.title("Register")
        self.frame.pack(expand=True)


        # Center all widgets
        self.username_entry_box.place(x=0, y=-8)
        self.username_entry.pack(pady=10)
        self.username_entry.bind("<Return>", lambda e: self.login())
        self.password_entry_box.place(x=0, y=62)
        self.password_entry.pack(pady=30)
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.register_button.pack(pady=(10, 5))
        self.return_button.place(x=10,y=10)

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2

        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        account = AccountDAO().get_by_user_and_pass(username, password)
        if account:
            messagebox.showinfo("Success", f"Welcome {account.username}")
            self.root.destroy()
            home = Home(account.account_id)
            home.init_window()
            home.root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid Information")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Can't leave any field blank")
            return

        account = AccountDAO().get_by_user(username)
        if account:
            messagebox.showerror("Error", "This username has been used!")
        else:
            AccountDAO().add(username, password)
            messagebox.showinfo("Success", "Your account has been created!")

    def go_back(self):
        self.root.destroy()
        login = Login()
        login.init_window()
        login.root.mainloop()

class Home:
    def __init__(self, client_id: int):
        self.client_id = client_id
        self.root = tk.Tk()
        self.root.resizable(False, False)

        # Create background
        self.background_image = tk.PhotoImage(file="img/background.png")
        self.background_label = tk.Label(self.root, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        self.frame = tk.Frame(self.root, bg='#d28c45')

        # Load images
        self.button_box = tk.PhotoImage(file='img/login-button.png')
        self.logout_button_box = tk.PhotoImage(file='img/register-button.png')

        # Create widget
        self.play_button = tk.Button(self.root, text="Play", font=("anything", 16), image=self.button_box,
                                      command=self.play, cursor='hand2', fg='white', bg='#4e6381', activeforeground='white',
                                      activebackground='#4e6381', relief=tk.GROOVE, compound='center')
        self.leaderboard_button = tk.Button(self.root, text="Leaderboard", font=("anything", 16), image=self.button_box,
                                      command=None, cursor='hand2', fg='white', bg='#4e6381',activeforeground='white',
                                      activebackground='#4e6381', relief=tk.GROOVE, compound='center')
        self.logout_button = tk.Button(self.root, text='Log Out',font=("anything", 16), image=self.logout_button_box,
                                      command=self.go_back, cursor='hand2', fg='white',bg='#eb4934', activebackground='#eb4934',
                                      activeforeground='white',relief=tk.GROOVE, compound='center')

        self.window_width = 600
        self.window_height = 500

    def init_window(self):
        self.center_window()
        self.root.title("Home")
        self.frame.pack(expand=True)

        account = AccountDAO().get_by_id(self.client_id)
        welcome_label_1 = tk.Label(self.frame, text=f"Welcome: {account.username}",font=('Helvetica', 20),
                                 fg = '#403834', bg = '#d28c45')
        welcome_label_2 = tk.Label(self.frame, text='to Chess.io', font=('Helvetica', 20),
                                   fg='#403834', bg='#d28c45')
        welcome_label_1.pack()
        welcome_label_2.pack()

        # Center all widgets
        self.play_button.pack(pady = (60,10))
        self.leaderboard_button.pack(pady = (0,10))
        self.logout_button.pack(pady = (0,130))

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2

        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def play(self):
        thread = threading.Thread(target=self.start_game, args=(self.client_id, ))
        thread.start()

    @staticmethod
    def start_game(client_id: int):
        client = Client(client_id)
        game = Game(client)
        game.run_game()

    def go_back(self):
        self.root.destroy()
        login = Login()
        login.init_window()
        login.root.mainloop()


if __name__ == '__main__':
    gui = Login()
    gui.init_window()
    gui.root.mainloop()
