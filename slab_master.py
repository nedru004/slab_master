import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import os
downloads_path = str(Path.home() / "Downloads")


# Function to generate segmented moves
def generate_segmented_moves(start, end, feedrate, segment_length=100):
    moves = []
    if start < end:
        current = start
        while current < end:
            next_position = min(current + segment_length, end)
            moves.append(f"G1 Y{next_position:.2f} F{feedrate}")
            current = next_position
    else:
        current = start
        while current > end:
            next_position = max(current - segment_length, end)
            moves.append(f"G1 Y{next_position:.2f} F{feedrate}")
            current = next_position
    return moves


# Function to generate G-code based on user inputs
def generate_gcode():
    try:
        # Get user inputs
        width = float(width_entry.get())
        length = float(length_entry.get())
        overlap = float(overlap_entry.get())
        feedrate = float(feedrate_entry.get())
        feedrate_non_motor = "6000"
        segment_length = 100  # Length of each segment for chopping moves

        # Calculate number of passes and total time
        passes = round(width / overlap + 0.5)
        total_time = (length / feedrate) * passes + width / feedrate

        # Generate G-code
        g_code = f"G90\nG21\nG92 X0 Y0 Z0\n;Total Passes: {passes}\n"
        g_code += f";Approx Total Time: {total_time:.1f} mins\n"

        # if both directions is selected
        if both_directions.get() == 1:
            # generate g code for each pass
            for i in range(0, int(passes), 2):
                if i != 0:
                    # move over on X axis
                    g_code += f"G3 X{overlap * i} I{overlap/2} F{feedrate}\n"
                # cut along Y axis
                g_code += f"G1 Y{length} F{feedrate}\n"
                segmented_moves = generate_segmented_moves(0, length, feedrate, segment_length)
                g_code += "\n".join(segmented_moves) + "\n"
                # move over on X axis
                g_code += f"G2 X{overlap * (i + 1)} I{overlap/2} F{feedrate}\n"
                # cut along -Y axis
                segmented_moves = generate_segmented_moves(length, 0, feedrate, segment_length)
                g_code += "\n".join(segmented_moves) + "\n"

            if passes % 2 != 0:
                # cut along Y axis
                g_code += f"G3 X{overlap * passes} I{overlap/2} F{feedrate}\n"
                # move along X axis
                g_code += f"G1 Y{length} F{feedrate}\n"

        else:
            # generate g code for each pass
            for i in range(0, int(passes)):
                # move z up 2 mm
                g_code += f"G1 Z2 F{feedrate}\n"
                # first pass move negative on x axis to avoid slab
                if i == 0:
                    g_code += f"G1 X{-overlap*2} F{feedrate}\n"
                # move to the end of the slab
                g_code += f"G1 Y{length} F{feedrate_non_motor}\n"
                if i == 0:
                    # move back over
                    g_code += f"G1 X0 F{feedrate}\n"
                if i != 0:
                    # move over on X axis
                    g_code += f"G1 X{overlap * i} F{feedrate}\n"
                # move z down 2 mm
                g_code += f"G1 Z0 F{feedrate}\n"
                # cut along Y axis
                segmented_moves = generate_segmented_moves(length, 0, feedrate, segment_length)
                g_code += "\n".join(segmented_moves) + "\n"

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

tk.Label(root, text="Segmented Length (mm):").grid(row=4, column=0, padx=10, pady=5)
segment_length = tk.Entry(root, textvariable=tk.StringVar(root, "10"))
segment_length.grid(row=4, column=1, padx=10, pady=5)

#create a checkbox to select if user want both directions
both_directions = tk.IntVar()
both_directions.set(1)
tk.Checkbutton(root, text="Both Directions", variable=both_directions).grid(row=5, columnspan=2, pady=5)

# Add a button to generate G-code
generate_button = tk.Button(root, text="Generate G-code", command=generate_gcode)
generate_button.grid(row=6, columnspan=2, pady=10)

# Start the GUI event loop
root.mainloop()
