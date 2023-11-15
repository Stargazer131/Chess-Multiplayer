import datetime
import threading
import tkinter as tk
from client import Client
from game import Game, GameView, GameReplay

from utility import Message


class Home:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)

        # Create icon
        self.icon = tk.PhotoImage(file='img/icon.png')
        self.root.iconphoto(True, self.icon)

        # Create background
        self.background_image = tk.PhotoImage(file="img/background.png")
        self.background_label = tk.Label(self.root, image=self.background_image, bg='#ffcf9f')
        self.background_label.place(relwidth=1, relheight=1)

        self.frame = tk.Frame(self.root, bg='#d28c45')

        # Load images
        self.button_box = tk.PhotoImage(file='img/button.png')

        # Create widget
        self.play_button = tk.Button(self.root, text="Play", font=("anything", 16),
                                     image=self.button_box, command=self.play, cursor='hand2',
                                     fg='white', bg='#4e6381', activeforeground='white', borderwidth=0,
                                     activebackground='#4e6381', relief=tk.GROOVE, compound='center')

        self.view_button = tk.Button(self.root, text="View", font=("anything", 16),
                                     image=self.button_box, command=self.view, cursor='hand2',
                                     fg='white', bg='#4e6381', activeforeground='white', borderwidth=0,
                                     activebackground='#4e6381', relief=tk.GROOVE, compound='center')

        self.replay_button = tk.Button(self.root, text="Replay", font=("anything", 16),
                                       image=self.button_box, command=self.replay, cursor='hand2',
                                       fg='white', bg='#4e6381', activeforeground='white', borderwidth=0,
                                       activebackground='#4e6381', relief=tk.GROOVE, compound='center')

        self.window_width = 700
        self.window_height = 600

    def init_window(self):
        self.center_window()
        self.root.title("Home")
        self.frame.pack(expand=True)

        welcome_label = tk.Label(self.frame, text='Welcome to Chess.io', font=('Helvetica', 25),
                                 fg='#d28c45', bg='#ffcf9f')
        welcome_label.pack()

        # Center all widgets
        self.play_button.pack(pady=(50, 20))
        self.view_button.pack(pady=(0, 20))
        self.replay_button.pack(pady=(0, 200))

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2

        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def play(self):
        self.root.destroy()
        client = Client(Message.PLAY)
        game = Game(client)
        game.run_game()

    def view(self):
        self.root.destroy()
        client = Client(Message.VIEW)
        view = View(client)
        view.init_window()
        view.root.mainloop()

    def replay(self):
        self.root.destroy()
        client = Client(Message.REPLAY)
        replay = Replay(client)
        replay.init_window()
        replay.root.mainloop()


class View:
    def __init__(self, client):
        self.room_data = []
        self.client = client
        self.selection = Message.NO_SELECTION

        self.window_width = 700
        self.window_height = 600

        self.root = tk.Tk()
        self.frame = tk.Frame(self.root, bg='#d28c45')
        self.root.config(bg='#d28c45')

        self.button_box = tk.PhotoImage(file='img/small-button.png', master=self.root)
        self.refresh_button = tk.Button(self.root, image=self.button_box, text=f"Refresh", font="anything", fg='white',
                                        command=self.get_data, cursor='hand2', compound=tk.CENTER, bg='#d28c45',
                                        borderwidth=0, activeforeground='white',
                                        activebackground='#d28c45', relief=tk.FLAT)
        self.canvas = tk.Canvas(self.root, width=self.window_width-50, height=self.window_height-100,
                                highlightthickness=1, highlightbackground="black", bg='#ffcf9f')
        self.background_image = tk.PhotoImage(file="img/canvas-background.png", master=self.canvas)
        self.background = self.canvas.create_image((0, 0), image=self.background_image)
        self.room_frame = tk.Frame(self.canvas, bg='#ffcf9f')

    def init_window(self):
        self.root.resizable(False, False)
        self.root.title("Room View")
        self.center_window()
        self.init_canvas()

    def create_rooms(self):
        for index, data in enumerate(self.room_data):
            game_id, viewers = data[0], data[1]
            row = index // 5
            col = index % 5
            button = tk.Button(self.room_frame, text=f"Room: {game_id}\nWatching: {viewers}", width=14, height=5,
                               command=lambda m=game_id: self.view(m), cursor='hand2', fg='white', bg='#3e8ed0',
                               activeforeground='white', activebackground='#3e8ed0', relief=tk.GROOVE)
            button.grid(row=row, column=col, padx=10, pady=10)

    def init_canvas(self):
        # Create a frame to hold the room buttons
        self.refresh_button.pack(pady=(10, 0))
        self.canvas.pack(padx=0, pady=10)
        self.canvas.create_window((-320, -250), window=self.room_frame, anchor="nw")

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
        self.root.destroy()

    def view_game(self, game_id: int):
        self.client.send(game_id)
        view = GameView(self.client)
        view.run_game()

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2

        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")


class Replay:
    def __init__(self, client):
        self.game_data = []
        self.client = client
        self.selection = Message.NO_SELECTION

        self.window_width = 700
        self.window_height = 600

        self.root = tk.Tk()
        self.frame = tk.Frame(self.root, bg='#d28c45')
        self.root.config(bg='#d28c45')

        self.button_box = tk.PhotoImage(file='img/small-button.png', master=self.root)
        self.refresh_button = tk.Button(self.root, image=self.button_box, text=f"Refresh", font="anything", fg='white',
                                        command=self.get_data, cursor='hand2', compound=tk.CENTER, bg='#d28c45',
                                        borderwidth=0, activeforeground='white',
                                        activebackground='#d28c45', relief=tk.FLAT)
        self.canvas = tk.Canvas(self.root, width=self.window_width-50, height=self.window_height-100,
                                highlightthickness=1, highlightbackground="black", bg='#ffcf9f')
        self.background_image = tk.PhotoImage(file="img/canvas-background.png", master=self.canvas)
        self.background = self.canvas.create_image((0, 0), image=self.background_image)
        self.room_frame = tk.Frame(self.canvas, bg='#ffcf9f')

    def init_window(self):
        self.root.resizable(False, False)
        self.root.title("Game Replay")
        self.center_window()
        self.init_canvas()

    def create_games(self):
        for index, data in enumerate(self.game_data):
            day, hour, game_id = data.split('_')
            timestamp = datetime.datetime.strptime(day+' '+hour, "%d-%m-%Y %H-%M-%S")

            row = index // 5
            col = index % 5
            text = f"Game: {game_id}\nDate: {timestamp.strftime('%d/%m/%Y')}" \
                   f"\nTime: {timestamp.strftime('%H:%M:%S')}"

            button = tk.Button(self.room_frame, text=text, width=14, height=5,
                               command=lambda m=(game_id, day, hour): self.replay(*m),
                               cursor='hand2', fg='white', bg='#3e8ed0', relief=tk.GROOVE,
                               activeforeground='white', activebackground='#3e8ed0')
            button.grid(row=row, column=col, padx=10, pady=10)

    def init_canvas(self):
        # Create a frame to hold the room buttons
        self.refresh_button.pack(pady=(10, 0))
        self.canvas.pack(padx=0, pady=10)
        self.canvas.create_window((-320, -250), window=self.room_frame, anchor="nw")

        # ------------------
        self.create_games()
        # ------------------

        # Bind the canvas to the mousewheel for scrolling
        self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(-1 * (event.delta // 120), "units"))

        # Update the canvas scroll region
        self.room_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_data(self):
        self.client.send(Message.ALL_DATA)
        self.game_data = self.client.receive()
        for widget in self.room_frame.winfo_children():
            widget.destroy()
        self.create_games()

    def replay(self, game_id: str, day: str, hour: str):
        thread = threading.Thread(target=self.replay_game, args=(game_id, day, hour))
        thread.start()
        self.root.destroy()

    def replay_game(self, game_id: str, day: str, hour: str):
        self.client.send(f'{day}_{hour}_{game_id}')
        data = self.client.receive()
        replay = GameReplay(self.client, data['board'], data['moves_information'], data['winner'])
        replay.run_game()

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
