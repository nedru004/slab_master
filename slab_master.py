import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import os
downloads_path = str(Path.home() / "Downloads")

# Function to calculate G-code based on user inputs
def generate_gcode():
    try:
        # Get user inputs
        width = float(width_entry.get())
        length = float(length_entry.get())
        overlap = float(overlap_entry.get())
        feedrate = float(feedrate_entry.get())
        
        # Calculate number of passes and total time
        passes = round(width / overlap + 0.5)
        total_time = (length / feedrate) * passes + width / feedrate
        
        # Generate G-code
        g_code = f"G90\nG21\nG92 X0 Y0 Z0\n;Total Passes: {passes}\n"
        g_code += f";Approx Total Time: {total_time:.2f} mins\n"
        
        # generate g code for each pass
        for i in range(0, int(passes), 2):
            if i != 0:
                # move over on X axis
                g_code += f"G3 X{overlap * i} I{overlap/2} F{feedrate}\n"
            # cut along Y axis
            g_code += f"G1 Y{length} F{feedrate}\n"
            # move over on X axis
            g_code += f"G2 X{overlap * (i + 1)} I{overlap/2} F{feedrate}\n"
            # cut along -Y axis
            g_code += f"G1 Y0 F{feedrate}\n"

        if passes % 2 != 0:
            # cut along Y axis
            g_code += f"G3 X{overlap * passes} I{overlap/2} F{feedrate}\n"
            # move along X axis
            g_code += f"G1 Y{length} F{feedrate}\n"

        # write g code to file
        with open(os.path.join(downloads_path,"slab_master.gcode"), "w") as f:
            f.write(g_code)
        
        # Display the G-code in a message box
        messagebox.showinfo("Generated G-code", g_code)
    
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for all fields.")

# Create the main window
root = tk.Tk()
root.title("CNC G-code Generator")

# Add labels and input fields
tk.Label(root, text="Width (mm):").grid(row=0, column=0, padx=10, pady=5)
width_entry = tk.Entry(root, textvariable=tk.StringVar(root, "600"))
width_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Length (mm):").grid(row=1, column=0, padx=10, pady=5)
length_entry = tk.Entry(root, textvariable=tk.StringVar(root, "1200"))
length_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Overlap (mm):").grid(row=2, column=0, padx=10, pady=5)
overlap_entry = tk.Entry(root, textvariable=tk.StringVar(root, "32"))
overlap_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Feedrate (mm/min):").grid(row=3, column=0, padx=10, pady=5)
feedrate_entry = tk.Entry(root, textvariable=tk.StringVar(root, "1000"))
feedrate_entry.grid(row=3, column=1, padx=10, pady=5)

# Add a button to generate G-code
generate_button = tk.Button(root, text="Generate G-code", command=generate_gcode)
generate_button.grid(row=4, columnspan=2, pady=10)

# Start the GUI event loop
root.mainloop()
