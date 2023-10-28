import threading
import tkinter as tk

from utility import Message


class View:
    def __init__(self, client):
        self.room_data = []
        self.client = client
        self.selection = Message.NO_SELECTION

        self.window_width = 700
        self.window_height = 600

        self.root = tk.Tk()
        self.refresh_button = tk.Button(self.root, text=f"Refresh", width=10, height=3,
                                        command=self.change, cursor='hand2', bg='#b1caf2')
        self.canvas = tk.Canvas(self.root, width=self.window_width-50, height=self.window_height-100,
                                highlightthickness=1, highlightbackground="black")
        self.room_frame = tk.Frame(self.canvas)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)

    def init_window(self):
        self.root.resizable(False, False)
        self.root.title("Room Viewing")
        self.center_window()
        thread = threading.Thread(target=self.fetch_room_data, daemon=True)
        thread.start()
        self.init_canvas()

    def create_rooms(self):
        for index, data in enumerate(self.room_data):
            room, viewers = data[0], data[1]
            row = index // 5
            col = index % 5
            button = tk.Button(self.room_frame, text=f"{room}\nWatching: {viewers}", width=14, height=5,
                               command='None', cursor='hand2', bg='#b1caf2')
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

    def change(self):
        for widget in self.room_frame.winfo_children():
            widget.destroy()
        self.create_rooms()

    def fetch_room_data(self):
        while True:
            try:
                self.client.send_int(self.selection)
                self.room_data = self.client.receive()
            except Exception as er:
                print(er)
                break

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2

        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")


if __name__ == '__main__':
    pass
