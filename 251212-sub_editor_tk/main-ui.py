import tkinter as tk
from tkinter import ttk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Generated UI")
        # Geometry based on reference CSS (approx 500 width, 850 height)
        self.root.geometry("500x850")
        
        # Configure the grid to expand properly
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Main container frame with padding to mimic the 'left: 55px' from CSS
        # Added uniform padding around the content
        main_frame = ttk.Frame(self.root, padding="50 30 50 30")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure columns for the main frame
        # We need 4 columns for the button row and bottom row
        for i in range(4):
            main_frame.columnconfigure(i, weight=1)

        # --- Row 0: Time Display ---
        # el-1765425574137-0
        self.a_time = ttk.Label(main_frame, text="00:00:00", anchor="center", font=("Arial", 24))
        self.a_time.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 20))

        # --- Row 1: Waveform (Canvas) ---
        # el-1765425574137-1
        self.a_wave = tk.Canvas(main_frame, bg="#d0d0d0", highlightthickness=1, highlightbackground="gray")
        self.a_wave.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(0, 20))
        # This row should expand to fill available space
        main_frame.rowconfigure(1, weight=1)

        # --- Row 2: Control Buttons ---
        # el-1765425574137-2 to -5
        # Load, Play, Pause, Save
        self.b_load = ttk.Button(main_frame, text="Load")
        self.b_load.grid(row=2, column=0, sticky="ew", padx=2, ipady=5)

        self.b_play = ttk.Button(main_frame, text="Play")
        self.b_play.grid(row=2, column=1, sticky="ew", padx=2, ipady=5)

        self.b_pause = ttk.Button(main_frame, text="Pause")
        self.b_pause.grid(row=2, column=2, sticky="ew", padx=2, ipady=5)

        self.b_save = ttk.Button(main_frame, text="Save")
        self.b_save.grid(row=2, column=3, sticky="ew", padx=2, ipady=5)

        # Space between buttons and subtitle
        main_frame.rowconfigure(2, minsize=60)

        # --- Row 3: Subtitle Input ---
        # el-1765425574137-8
        self.i_sub = tk.Text(main_frame, height=5, width=40, bg="#2a2e37", fg="white", insertbackground="white")
        self.i_sub.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 20))
        self.i_sub.insert("1.0", "Subtitle text goes here...")

        # --- Row 4: Bottom Navigation & Info ---
        # el-1765425574137-6 (Up)
        self.b_up = ttk.Button(main_frame, text="Up")
        self.b_up.grid(row=4, column=0, sticky="ew", padx=2, ipady=5)

        # el-1765425574137-7 (Line #)
        self.a_on_show = ttk.Label(main_frame, text="Line #", anchor="center")
        self.a_on_show.grid(row=4, column=1, sticky="ew", padx=2)

        # el-1765425574137-9 (Entry)
        self.i_no = ttk.Entry(main_frame, width=5)
        self.i_no.insert(0, "1")
        self.i_no.grid(row=4, column=2, sticky="ew", padx=2)

        # el-1765425574137-10 (Down)
        self.b_down = ttk.Button(main_frame, text="Down")
        self.b_down.grid(row=4, column=3, sticky="ew", padx=2, ipady=5)


if __name__ == "__main__":
    root = tk.Tk()
    # Configure global style similar to CSS if possible, but keeping it simple for now
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 10))
    
    app = App(root)
    root.mainloop()
