import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import pygame
import soundfile as sf

from TextToSpeech import TextToSpeech

TEXT_FILE = "temp/text.txt"
AUDIO_FILE = "temp/audio.wav"


class TTSGUI:
    def __init__(self, root):
        self.root: tk.Tk = root
        self.root.title("Text to Speech Player")
        self.tts = TextToSpeech()

        self.playing = False
        self.paused = False
        self.seek_time = 0
        self.seek_val = 0

        pygame.mixer.init()

        self.setup_gui()
        self.clear_temp_files()

    def setup_gui(self):
        file_frame = ttk.Frame(self.root)
        file_frame.pack(pady=10, padx=10, fill=tk.X)

        ttk.Button(file_frame, text="Select Text File", command=self.select_file).pack(
            side=tk.LEFT
        )
        ttk.Button(
            file_frame, text="Generate Speech", command=self.generate_speech
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(file_frame, text="Save", command=self.export_result).pack(
            side=tk.LEFT, padx=5
        )

        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=10)

        text_frame = ttk.LabelFrame(self.root, text="Text Content")
        text_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.text_display = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, width=80, height=20
        )
        self.text_display.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10, padx=10, fill=tk.X)

        self.play_button = ttk.Button(
            control_frame, text="Play", command=self.toggle_playback
        )
        self.play_button.pack(side=tk.LEFT)

        ttk.Button(control_frame, text="Stop", command=self.stop_audio).pack(
            side=tk.LEFT, padx=5
        )

        self.seek_var = tk.DoubleVar()
        self.seek_bar = ttk.Scale(
            control_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.seek_var,
            command=self.on_seek,
        )
        self.seek_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.time_label = ttk.Label(control_frame, text="00:00 / 00:00")
        self.time_label.pack(side=tk.LEFT)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file_path:
            self.current_file = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.load_text_content(file_path)

    def load_text_content(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(1.0, content)
            if os.path.exists(file_path.replace(".txt", ".wav")):
                shutil.copy(file_path.replace(".txt", ".wav"), AUDIO_FILE)
                self.play_audio()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file: {e}")

    def write_text_to_tmp_file(self):
        if not os.path.exists(TEXT_FILE):
            os.makedirs(os.path.dirname(TEXT_FILE), exist_ok=True)

        with open(TEXT_FILE, "w", encoding="utf-8") as f:
            f.write(self.text_display.get(1.0, tk.END))

    def generate_speech(self):
        if not self.text_display.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "Please write/load some text first")
            return

        self.write_text_to_tmp_file()

        def process_in_thread():
            try:
                self.tts.process_file(TEXT_FILE, AUDIO_FILE)
                self.root.after(0, lambda: self.on_generation_complete())
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=process_in_thread, daemon=True).start()
        messagebox.showinfo("Processing", "Generating audio...")

    def on_generation_complete(self):
        messagebox.showinfo("Success", "Audio generation completed!")
        self.play_audio()

    def export_result(self):
        if not os.path.isfile(AUDIO_FILE):
            messagebox.showwarning("Warning", "No audio file generated")
            return

        if not os.path.isfile(TEXT_FILE):
            messagebox.showwarning("Warning", "No text file generated")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav", filetypes=[("Wave Files", "*.wav")]
        )
        if file_path:
            shutil.copy(AUDIO_FILE, file_path)
            shutil.copy(TEXT_FILE, file_path.replace(".wav", ".txt"))
            messagebox.showinfo("Success", f"Audio and text exported to {file_path}")

    def toggle_playback(self):
        if not os.path.isfile(AUDIO_FILE):
            messagebox.showwarning("Warning", "No audio file loaded")
            return

        if not self.playing:
            self.play_audio()
        else:
            self.pause_audio()

    def play_audio(self):
        try:
            if not self.paused:
                pygame.mixer.music.load(AUDIO_FILE)
                pygame.mixer.music.play()

                audio_info = sf.info(AUDIO_FILE)
                self.audio_length = audio_info.duration
                self.seek_bar.config(from_=0, to=self.audio_length)
                self.seek_val = 0
                self.seek_time = 0
            else:
                pygame.mixer.music.unpause()

            self.playing = True
            self.paused = False
            self.play_button.config(text="Pause")
            self.update_seek_bar()

        except Exception as e:
            messagebox.showerror("Error", f"Could not play audio: {e}")

    def pause_audio(self):
        pygame.mixer.music.pause()
        self.playing = False
        self.paused = True
        self.play_button.config(text="Play")

    def stop_audio(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.play_button.config(text="Play")
        self.seek_var.set(0)
        self.seek_time = 0
        self.seek_val = 0
        self.update_time_label()

    def on_seek(self, value):
        if self.playing or self.paused:
            pygame.mixer.music.set_pos(float(value))
            self.seek_time = pygame.mixer.music.get_pos() / 1000.0
            self.seek_val = float(value)
            self.update_seek_bar()

    def update_time_label(self):
        total_time = self.format_time(self.audio_length)
        current_time = self.format_time(self.seek_var.get())

        if self.seek_var.get() >= self.audio_length:
            self.stop_audio()

        self.time_label.config(text=f"{current_time} / {total_time}")

    def update_seek_bar(self):
        if self.playing or self.paused:
            current_pos = pygame.mixer.music.get_pos() / 1000.0
            self.seek_var.set(current_pos - self.seek_time + self.seek_val)

            self.update_time_label()

            if self.playing:
                self.root.after(100, self.update_seek_bar)
        else:
            self.playing = False
            self.play_button.config(text="Play")

    def clear_temp_files(self):
        if os.path.isfile(AUDIO_FILE):
            os.remove(AUDIO_FILE)

        if os.path.isfile(TEXT_FILE):
            os.remove(TEXT_FILE)

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
