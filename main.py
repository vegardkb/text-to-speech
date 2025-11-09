import tkinter as tk

from TextToSpeechInterface import TTSGUI


def main():
    root = tk.Tk()
    _ = TTSGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
