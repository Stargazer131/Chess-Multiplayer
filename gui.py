import threading
import tkinter as tk
from tkinter import messagebox
from account import AccountDAO
from client import Client
from game import Game


class Login:
    def __init__(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)

        self.username_entry = tk.Entry(self.frame, width=20, font=("anything", 15))
        self.password_entry = tk.Entry(self.frame, show="*", width=20, font=("anything", 15))
        self.login_button = tk.Button(self.frame, text="Login", command=self.login,
                                      height=2, width=10, cursor='hand2')
        self.register_button = tk.Button(self.frame, text="Register", command=self.register,
                                         height=2, width=10, cursor='hand2')

        self.window_width = 500
        self.window_height = 400

    def init_window(self):
        self.center_window()
        self.root.title("Login")
        self.frame.pack(expand=True)

        # Create labels
        username_label = tk.Label(self.frame, text="Username:")
        password_label = tk.Label(self.frame, text="Password:")

        # Center all widgets
        username_label.pack(pady=(10, 5))
        self.username_entry.pack(pady=5)
        self.username_entry.bind("<Return>", lambda e: self.login())
        password_label.pack(pady=5)
        self.password_entry.pack(pady=5)
        self.password_entry.bind("<Return>", lambda e: self.login())

        self.login_button.pack(pady=(10, 5))
        self.register_button.pack(pady=(10, 5))

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


class Register:
    def __init__(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)

        self.username_entry = tk.Entry(self.frame, width=20, font=("anything", 15))
        self.password_entry = tk.Entry(self.frame, show="*", width=20, font=("anything", 15))
        self.register_button = tk.Button(self.frame, text="Register", command=self.register,
                                         height=2, width=10, cursor='hand2')
        self.return_button = tk.Button(self.frame, text="Return", command=self.go_back,
                                       height=2, width=10, cursor='hand2')

        self.window_width = 500
        self.window_height = 400

    def init_window(self):
        self.center_window()
        self.root.title("Register")
        self.frame.pack(expand=True)

        # Create labels
        username_label = tk.Label(self.frame, text="Username:")
        password_label = tk.Label(self.frame, text="Password:")

        # Center all widgets
        username_label.pack(pady=(10, 5))
        self.username_entry.pack(pady=5)
        self.username_entry.bind("<Return>", lambda e: self.register())
        password_label.pack(pady=5)
        self.password_entry.pack(pady=5)
        self.password_entry.bind("<Return>", lambda e: self.register())

        self.register_button.pack(pady=(10, 5))
        self.return_button.pack(pady=(10, 5))

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
        self.frame = tk.Frame(self.root)

        self.play_button = tk.Button(self.frame, text="Play", command=self.play,
                                     height=2, width=10, cursor='hand2')
        self.leaderboard_button = tk.Button(self.frame, text="Leaderboard", command=None,
                                            height=2, width=10, cursor='hand2')
        self.return_button = tk.Button(self.frame, text="Return", command=self.go_back,
                                       height=2, width=10, cursor='hand2')

        self.window_width = 600
        self.window_height = 500

    def init_window(self):
        self.center_window()
        self.root.title("Home")
        self.frame.pack(expand=True)

        account = AccountDAO().get_by_id(self.client_id)
        welcome_label = tk.Label(self.frame, text=f"Welcome: {account.username}")
        welcome_label.pack(pady=10)
        # Center all widgets
        self.play_button.pack(pady=(50, 50))
        self.leaderboard_button.pack(pady=(50, 50))
        self.return_button.pack(pady=(50, 50))

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
