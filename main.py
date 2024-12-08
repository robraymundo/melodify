import tkinter as tk
from tkinter import ttk
import pygame
import os


class App(tk.Tk):
    def __init__(self, title, size):
        # main setup
        super().__init__()
        self.minsize(size[0], size[1])
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.maxsize(size[0], size[1])
        self.resizable(False, False)
        self.config(bg='#282424')

        # interface
        self.menu = Menu(self, root=self)
        self.menu.pack(fill=tk.BOTH, expand=True)

        # run
        self.mainloop()


class Menu(tk.Frame):
    def __init__(self, parent, root):
        super().__init__(parent, bg='#212024')

        self.root = root

        # load current song file
        self.track_song = SongTracker()
        self.track_song.load_song()

        # button icons
        self.play_icon = tk.PhotoImage(file='graphics/play_button.png')
        self.next_icon = tk.PhotoImage(file='graphics/next_button.png')
        self.prev_icon = tk.PhotoImage(file='graphics/previous_button.png')
        self.pause_icon = tk.PhotoImage(file='graphics/pause_button.png')

        # buttons
        self.play_button = None
        self.next_button = None
        self.prev_button = None
        self.pause_button = None
        self.resume_button = None

        # button
        self.button_frame = tk.Frame(self, bg='#212024')
        self.create_buttons()

        # progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar",
                        background='white',
                        foreground='#444',
                        troughcolor='#212024',
                        borderwidth=0,
                        )

        self.progress_bar = None
        self.create_progress_bar()

        # label
        self.label_frame = tk.Frame(self, bg='#212024')
        self.create_label()

        # track song status
        self.song_status = 'idle'
        self.update_progress_bar()

    def create_progress_bar(self):
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=450, mode="determinate")
        self.progress_bar.pack(side="bottom", pady=10)

    def create_label(self):
        tk.Label(self.label_frame, textvariable=self.track_song.title_text, font=('MS Sans Serif', 20),
                 fg='white', bg='#212024', padx=10, anchor=tk.NW).pack(side="top", anchor="nw")

        tk.Label(self.label_frame, textvariable=self.track_song.artist_text, font=('MS Sans Serif', 15),
                 fg='#c9c9c9', bg='#212024', padx=20, anchor=tk.NW).pack(side="top", anchor="nw")

        self.label_frame.pack(side="top", pady=10, anchor="nw")

    def create_buttons(self):
        self.play_button = tk.Button(self.button_frame, image=self.play_icon, activebackground='#212024', bg='#212024',
                                     relief='flat', overrelief='flat', command=lambda: self.play_song())
        self.next_button = tk.Button(self.button_frame, image=self.next_icon, activebackground='#212024', bg='#212024',
                                     relief='flat', overrelief='flat', command=lambda: self.next_song())
        self.prev_button = tk.Button(self.button_frame, image=self.prev_icon, activebackground='#212024', bg='#212024',
                                     relief='flat', overrelief='flat', command=lambda: self.prev_song())

        self.prev_button.grid(row=0, column=0)
        self.play_button.grid(row=0, column=1)
        self.next_button.grid(row=0, column=2)

        self.button_frame.pack(side="bottom")

    def show_pause_button(self):
        self.play_button.destroy()
        self.pause_button = tk.Button(self.button_frame, image=self.pause_icon, activebackground='#212024',
                                      bg='#212024',
                                      relief='flat', overrelief='flat', command=lambda: self.show_resume_button())
        self.pause_button.grid(row=0, column=1)

    def show_resume_button(self):
        self.song_status = 'paused'
        pygame.mixer.music.pause()

        self.pause_button.destroy()
        self.resume_button = tk.Button(self.button_frame, image=self.play_icon, activebackground='#212024',
                                       bg='#212024',
                                       relief='flat', overrelief='flat', command=lambda: self.play_song())
        self.resume_button.grid(row=0, column=1)

    def play_song(self):
        if self.song_status == 'idle':
            self.song_status = 'playing'
            pygame.mixer.music.play()
        else:
            self.song_status = 'playing'
            pygame.mixer.music.unpause()
        self.show_pause_button()

    def next_song(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        self.track_song.load_next_song()
        self.handle_song_status()

    def prev_song(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        pygame.mixer.music.stop()
        self.track_song.load_prev_song()
        self.handle_song_status()

    def handle_song_status(self):
        if self.song_status == 'playing':
            pygame.mixer.music.play()
        elif self.song_status == 'paused':
            self.song_status = 'idle'

    def update_progress_bar(self):
        current_position = pygame.mixer.music.get_pos() / 1000
        duration = self.track_song.duration

        progress = (current_position / duration) * 170
        self.progress_bar['value'] = progress
        self.root.update()

        self.root.after(500, self.update_progress_bar)


class SongNode:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None


class SongTracker:
    def __init__(self):
        self.head = None
        self.tail = None

        for file_name in os.listdir('music_folder'):
            new_song = SongNode(file_name)
            if not self.head:
                self.head = new_song
            else:
                current = self.head
                while current.next:
                    current = current.next
                current.next = new_song
                new_song.prev = current

                self.tail = new_song
                self.head.prev = self.tail

        self.current_song = self.head

        self.duration = None

        # text variables
        song_title = self.current_song.data.partition('-')[2][0:-4]
        song_artist = self.current_song.data.partition('-')[0]

        self.title_text = tk.StringVar()
        self.title_text.set(song_title)

        self.artist_text = tk.StringVar()
        self.artist_text.set(song_artist)

    def load_next_song(self):
        if self.current_song.next:
            self.current_song = self.current_song.next
        else:
            self.current_song = self.head

        self.load_song()

    def load_prev_song(self):
        if self.current_song.prev:
            self.current_song = self.current_song.prev

            self.load_song()

    def load_song(self):
        song_title = self.current_song.data.partition('-')[2][0:-4]
        song_artist = self.current_song.data.partition('-')[0]
        self.title_text.set(song_title)
        self.artist_text.set(song_artist)
        self.duration = pygame.mixer.Sound(f'music_folder/{self.current_song.data}').get_length()

        pygame.mixer.music.load(f'music_folder/{self.current_song.data}')


pygame.init()
pygame.mixer.init()
App('Melodify', (500, 220))
