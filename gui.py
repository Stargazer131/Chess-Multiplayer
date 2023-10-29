import threading
import tkinter as tk
from client import Client
from game import Game, GameView
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


class View:
    def __init__(self, client):
        self.room_data = []
        self.client = client
        self.selection = Message.NO_SELECTION

        self.window_width = 700
        self.window_height = 600

        self.root = tk.Tk()
        self.frame = tk.Frame(self.root, bg='#d28c45')
        self.refresh_button = tk.Button(self.root, text=f"Refresh", width=10, height=3,
                                        command=self.get_data, cursor='hand2', bg='#b1caf2')
        self.canvas = tk.Canvas(self.root, width=self.window_width-50, height=self.window_height-100,
                                highlightthickness=1, highlightbackground="black")
        self.room_frame = tk.Frame(self.canvas)

    def init_window(self):
        self.root.resizable(False, False)
        self.root.title("Room Viewing")
        self.center_window()
        self.init_canvas()

    def create_rooms(self):
        for index, data in enumerate(self.room_data):
            game_id, viewers = data[0], data[1]
            row = index // 5
            col = index % 5
            button = tk.Button(self.room_frame, text=f"Room: {game_id}\nWatching: {viewers}", width=14, height=5,
                               command=lambda: self.view(game_id), cursor='hand2', bg='#b1caf2')
            button.grid(row=row, column=col, padx=10, pady=10)

    def init_canvas(self):
        # Create a frame to hold the room buttons
        self.refresh_button.pack()
        self.canvas.pack(padx=10, pady=10)
        self.canvas.create_window((0, 0), window=self.room_frame, anchor="nw")

        # ------------------
        self.create_rooms()
        # ------------------

        # Bind the canvas to the mousewheel for scrolling
        self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(-1 * (event.delta // 120), "units"))

        # Update the canvas scroll region
        self.room_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_data(self):
        self.client.send(Message.ALL_DATA)
        self.room_data = self.client.receive()
        for widget in self.room_frame.winfo_children():
            widget.destroy()
        self.create_rooms()

    def view(self, game_id: int):
        thread = threading.Thread(target=self.view_game, args=(game_id,))
        thread.start()

    def view_game(self, game_id: int):
        self.refresh_button.config(state=tk.DISABLED)
        for child in self.room_frame.winfo_children():
            child.configure(state=tk.DISABLED)
        self.client.send(game_id)
        view = GameView(self.client)
        view.run_game()
        try:
            self.refresh_button.config(state=tk.NORMAL)
            for child in self.room_frame.winfo_children():
                child.configure(state=tk.NORMAL)
        except Exception as er:
            print(er)

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2

        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")


if __name__ == '__main__':
    gui = Home()
    gui.init_window()
    gui.root.mainloop()
