# main.py

import tkinter as tk
from fire_simulation_gui import FireSimulationGUI

def main():
    root = tk.Tk()
    root.title("Fire Simulation")
    app = FireSimulationGUI(root, height=200, width=200, initial_state="test_plain", boundary="reflective")
    root.mainloop()

if __name__ == "__main__":
    main()
