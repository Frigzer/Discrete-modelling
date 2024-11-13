# main.py

import tkinter as tk
from game_of_life_gui import GameOfLifeGUI

def main():
    root = tk.Tk()
    root.title("Game of Life")
    app = GameOfLifeGUI(root, height=200, width=200, initial_state="glider", boundary="periodic")
    root.mainloop()

if __name__ == "__main__":
    main()
