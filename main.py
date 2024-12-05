import tkinter as tk
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

        self.config(bg='#212024')

        # buttons
        self.menu = Menu(self)
        self.menu.pack(fill=tk.BOTH, expand=True)

        # run
        self.mainloop()


class Menu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#212024')
        # load current song file
        self.track_song = SongTracker()
        self.track_song.load_song()

        # button icons
        self.play_icon = tk.PhotoImage(file='graphics/play_button.png')
        self.next_icon = tk.PhotoImage(file='graphics/next_button.png')
        self.prev_icon = tk.PhotoImage(file='graphics/previous_button.png')
        self.pause_icon = tk.PhotoImage(file='graphics/pause_button.png')

        # title label
        tk.Label(self, textvariable=self.track_song.title_text, font=('MS Sans Serif', 20),
                 fg='white', bg='#212024', width=30, height=1, anchor=tk.NW).place(relx=0, y=0, rely=0)

        # artist label
        tk.Label(self, textvariable=self.track_song.artist_text, font=('MS Sans Serif', 15),
                 fg='#c9c9c9', bg='#212024', width=20, height=1, anchor=tk.NW).place(relx=0.025, y=0, rely=0.2)

        # button frame
        self.create_buttons()

        # track song status
        self.song_status = 'idle'

    def create_buttons(self):
        play_button = tk.Button(self, image=self.play_icon, activebackground='#212024', bg='#212024',
                                relief='flat', overrelief='flat', command=lambda: self.play_song())
        next_button = tk.Button(self, image=self.next_icon, activebackground='#212024', bg='#212024',
                                relief='flat', overrelief='flat', command=lambda: self.next_song())
        prev_button = tk.Button(self, image=self.prev_icon, activebackground='#212024', bg='#212024',
                                relief='flat', overrelief='flat', command=lambda: self.prev_song())

        play_button.place(relx=0.4, y=0, relwidth=0.2, rely=0.4)
        next_button.place(relx=0.6, y=0, relwidth=0.2, rely=0.4)
        prev_button.place(relx=0.2, y=0, relwidth=0.2, rely=0.4)

    def show_pause_button(self):
        pause_button = tk.Button(self, image=self.pause_icon, activebackground='#212024', bg='#212024',
                                 relief='flat', overrelief='flat', command=lambda: self.show_resume_button())
        pause_button.place(relx=0.4, y=0, relwidth=0.2, rely=0.4)

    def show_resume_button(self):
        self.song_status = 'paused'
        pygame.mixer.music.pause()
        resume_button = tk.Button(self, image=self.play_icon, activebackground='#212024', bg='#212024',
                                  relief='flat', overrelief='flat', command=lambda: self.play_song())
        resume_button.place(relx=0.4, y=0, relwidth=0.2, rely=0.4)

    def play_song(self):
        if self.song_status == 'idle':
            self.song_status = 'playing'
            pygame.mixer.music.play()
        else:
            self.song_status = 'playing'
            pygame.mixer.music.unpause()
        self.show_pause_button()

    def next_song(self):
        self.track_song.load_next_song()
        self.handle_song_status()

    def prev_song(self):
        self.track_song.load_prev_song()
        self.handle_song_status()

    def handle_song_status(self):
        if self.song_status == 'playing':
            pygame.mixer.music.play()
        elif self.song_status == 'paused':
            self.song_status = 'idle'


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

        pygame.mixer.music.load(f'music_folder/{self.current_song.data}')


pygame.init()
pygame.mixer.init()
App('Music', (400, 200))
