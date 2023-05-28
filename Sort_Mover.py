import os
import tkinter as tk
from tkinter import filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import configparser

class FileHandler(FileSystemEventHandler):
    def __init__(self, source_dir, target_dirs):
        super().__init__()
        self.source_dir = source_dir
        self.target_dirs = target_dirs

    def on_created(self, event):
        if event.is_directory:
            return

        filename = event.src_path
        file_extension = os.path.splitext(filename)[1]

        if file_extension.lower() in ['.mp4', '.avi', '.mkv']:
            target_dir = self.target_dirs['video']
        elif file_extension.lower() in ['.jpg', '.png', '.gif']:
            target_dir = self.target_dirs['pictures']
        elif file_extension.lower() in ['.docx', '.pdf', '.txt']:
            target_dir = self.target_dirs['documents']
        elif file_extension.lower() in ['.mp3', '.wav', '.flac']:
            target_dir = self.target_dirs['music']
        else:
            target_dir = self.target_dirs['other']

        os.rename(filename, os.path.join(target_dir, os.path.basename(filename)))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Organizer")

        self.source_dir = tk.StringVar()
        self.target_dirs = {
            'video': tk.StringVar(),
            'pictures': tk.StringVar(),
            'documents': tk.StringVar(),
            'music': tk.StringVar(),
            'other': tk.StringVar()
        }


        self.load_settings()

        source_label = tk.Label(self, text="Source Folder:")
        source_label.pack()
        source_entry = tk.Entry(self, textvariable=self.source_dir, width=50)
        source_entry.pack()
        source_button = tk.Button(self, text="Select Source", command=self.select_source_folder)
        source_button.pack()

        target_label = tk.Label(self, text="Target Folders:")
        target_label.pack()
        for category, var in self.target_dirs.items():
            target_entry = tk.Entry(self, textvariable=var, width=50)
            target_entry.pack()
            target_button = tk.Button(self, text=f"Select {category.capitalize()}", command=lambda v=var: self.select_target_folder(v))
            target_button.pack()

        start_button = tk.Button(self, text="Start", command=self.start)
        start_button.pack()

        stop_button = tk.Button(self, text="Stop", command=self.stop)
        stop_button.pack()

        self.observer = None

    def select_source_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_dir.set(folder)

    def select_target_folder(self, var):
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)

    def start(self):
        source_dir = self.source_dir.get()
        target_dirs = {category: var.get() for category, var in self.target_dirs.items()}

        if source_dir and all(target_dirs.values()):
            self.save_settings()
            self.observer = Observer()
            self.observer.schedule(FileHandler(source_dir, target_dirs), source_dir, recursive=False)
            self.observer.start()

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def load_settings(self):
        config = configparser.ConfigParser()
        config.read('settings.ini')

        self.source_dir.set(config.get('Settings', 'source_dir'))
        for category in self.target_dirs:
            self.target_dirs[category].set(config.get('Settings', f'{category}_dir'))

    def save_settings(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'source_dir': self.source_dir.get()
        }
        for category, var in self.target_dirs.items():
            config['Settings'][f'{category}_dir'] = var.get()

        with open('settings.ini', 'w') as configfile:
            config.write(configfile)

if __name__ == "__main__":
    app = App()
    app.mainloop()
