import threading
import tkinter as tk
from client import Client
from game import Game
from test import View
from utility import Message


class Home:
    def __init__(self):
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
        self.play_button = tk.Button(self.root, text="Play", font=("anything", 16),
                                     image=self.button_box, command=self.play, cursor='hand2',
                                     fg='white', bg='#4e6381', activeforeground='white',
                                     activebackground='#4e6381', relief=tk.GROOVE, compound='center')

        self.view_button = tk.Button(self.root, text="View", font=("anything", 16),
                                     image=self.button_box, command=self.view, cursor='hand2',
                                     fg='white', bg='#4e6381', activeforeground='white',
                                     activebackground='#4e6381', relief=tk.GROOVE, compound='center')

        self.replay_button = tk.Button(self.root, text="Replay", font=("anything", 16),
                                       image=self.button_box, command=self.replay, cursor='hand2',
                                       fg='white', bg='#4e6381', activeforeground='white',
                                       activebackground='#4e6381', relief=tk.GROOVE, compound='center')

        self.window_width = 600
        self.window_height = 500

    def init_window(self):
        self.center_window()
        self.root.title("Home")
        self.frame.pack(expand=True)

        welcome_label = tk.Label(self.frame, text='Welcome to Chess.io', font=('Helvetica', 20),
                                 fg='#403834', bg='#d28c45')
        welcome_label.pack()

        # Center all widgets
        self.play_button.pack(pady=(60, 10))
        self.view_button.pack(pady=(0, 10))
        self.replay_button.pack(pady=(0, 130))

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2

        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def play(self):
        thread = threading.Thread(target=self.start_game)
        thread.start()

    def start_game(self):
        self.play_button.config(state=tk.DISABLED)
        self.view_button.config(state=tk.DISABLED)
        self.replay_button.config(state=tk.DISABLED)
        client = Client(Message.PLAY)
        game = Game(client)
        game.run_game()
        try:
            self.play_button.config(state=tk.NORMAL)
            self.view_button.config(state=tk.NORMAL)
            self.replay_button.config(state=tk.NORMAL)
        except Exception as er:
            print(er)

    def view(self):
        thread = threading.Thread(target=self.view_game)
        thread.start()

    def view_game(self):
        self.play_button.config(state=tk.DISABLED)
        self.view_button.config(state=tk.DISABLED)
        self.replay_button.config(state=tk.DISABLED)
        client = Client(Message.VIEW)
        view = View(client)
        view.init_window()
        view.root.mainloop()

        try:
            self.play_button.config(state=tk.NORMAL)
            self.view_button.config(state=tk.NORMAL)
            self.replay_button.config(state=tk.NORMAL)
        except Exception as er:
            print(er)

    def replay(self):
        pass


if __name__ == '__main__':
    gui = Home()
    gui.init_window()
    gui.root.mainloop()
