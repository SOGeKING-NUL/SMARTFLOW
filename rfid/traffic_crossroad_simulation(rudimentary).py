import tkinter as tk

# Global variables:
countdown = 15
active_light_index = 0
ambulance_priority = False      # True when priority is queued
in_priority_cycle = False       # True when the ambulance is currently in its forced cycle
next_normal_index = None        # Stores the normal next index when ambulance priority is queued

class TrafficLight:
    def __init__(self, parent, name=None):
        """
        Creates an individual traffic light inside the given parent.
        If 'name' is provided, a label is displayed below the light.
        """
        # Create a frame; layout is managed by the parent (using grid)
        self.frame = tk.Frame(parent, bg="#2E3440")
        
        self.canvas = tk.Canvas(self.frame, width=150, height=320, bg="#2E3440", highlightthickness=0)
        self.canvas.pack()  # Pack inside the frame
        
        # Draw the traffic light casing
        self.canvas.create_rectangle(20, 10, 130, 310, fill="#3B4252", outline="#4C566A", width=2)
        # Draw the red (upper) and green (lower) lights
        self.red_light = self.canvas.create_oval(35, 30, 115, 110, fill="red", outline="#ECEFF4", width=2)
        self.green_light = self.canvas.create_oval(35, 200, 115, 280, fill="gray", outline="#ECEFF4", width=2)
        
        # If a name is provided (for example, "Ambulance"), display it below the canvas.
        if name:
            self.name_label = tk.Label(self.frame, text=name, font=("Helvetica", 14, "bold"),
                                       bg="#2E3440", fg="#D8DEE9")
            self.name_label.pack(pady=(5, 0))
    
    def set_green(self):
        """Sets this traffic light to green (and red off)."""
        self.canvas.itemconfig(self.red_light, fill="gray")
        self.canvas.itemconfig(self.green_light, fill="green")
    
    def set_red(self):
        """Sets this traffic light to red (and green off)."""
        self.canvas.itemconfig(self.red_light, fill="red")
        self.canvas.itemconfig(self.green_light, fill="gray")

def update_timer():
    """Updates the countdown timer. When it reaches 0, the current light is turned off.
    If an ambulance priority is queued, the ambulance is activated for its cycle,
    and then the cycle resumes with the originally scheduled next light."""
    global countdown, active_light_index, ambulance_priority, in_priority_cycle, next_normal_index
    timer_label.config(text=f"Time remaining: {countdown} seconds")
    
    if countdown > 0:
        countdown -= 1
        root.after(1000, update_timer)
    else:
        # End the current cycle: turn off the current light.
        traffic_lights[active_light_index].set_red()
        
        # If we are finishing an ambulance cycle, resume with the stored normal next index.
        if in_priority_cycle:
            active_light_index = next_normal_index
            next_normal_index = None
            in_priority_cycle = False
        # Otherwise, if ambulance priority was queued, switch to ambulance.
        elif ambulance_priority:
            next_normal_index = (active_light_index + 1) % len(traffic_lights)
            active_light_index = 2  # Ambulance is at index 2.
            ambulance_priority = False
            in_priority_cycle = True
        else:
            # Normal cycle: simply advance to the next light.
            active_light_index = (active_light_index + 1) % len(traffic_lights)
        
        # Turn on the new active light.
        traffic_lights[active_light_index].set_green()
        countdown = 15
        root.after(1000, update_timer)

def priority_handler(event):
    """When Enter is pressed, if the current light is not the ambulance and
    no ambulance priority is pending, queue the ambulance to be next.
    A message is shown on screen to indicate that ambulance priority has been queued."""
    global ambulance_priority, active_light_index
    if active_light_index != 2 and not ambulance_priority:
        ambulance_priority = True
        priority_label.config(text="Ambulance priority queued!")
        root.after(3000, lambda: priority_label.config(text=""))
    # If the ambulance is already active or queued, do nothing.

# Create the main window.
root = tk.Tk()
root.title("Traffic Lights")
root.configure(bg="#2E3440")

# Header label.
title_label = tk.Label(root, text="Traffic Lights", font=("Helvetica", 24, "bold"),
                       bg="#2E3440", fg="#ECEFF4")
title_label.pack(pady=(20, 10))

# Timer label.
timer_label = tk.Label(root, text="Time remaining: 15 seconds", font=("Helvetica", 16),
                       bg="#2E3440", fg="#ECEFF4")
timer_label.pack(pady=(10, 5))

# Priority message label.
priority_label = tk.Label(root, text="", font=("Helvetica", 16, "bold"),
                          bg="#2E3440", fg="#BF616A")
priority_label.pack(pady=(0, 20))

# Frame to hold the four traffic lights in a 2x2 grid.
lights_frame = tk.Frame(root, bg="#2E3440")
lights_frame.pack(pady=10)

traffic_lights = []
# Create four traffic lights in row-major order:
# Index 0: Top left, Index 1: Top right,
# Index 2: Bottom left (Ambulance), Index 3: Bottom right.
for i in range(2):
    for j in range(2):
        index = i * 2 + j
        if index == 2:
            tl = TrafficLight(lights_frame, name="Ambulance")
        else:
            tl = TrafficLight(lights_frame)
        tl.frame.grid(row=i, column=j, padx=10, pady=10)
        traffic_lights.append(tl)

# Set the initial state: traffic light 0 is green; all others are red.
for i, tl in enumerate(traffic_lights):
    if i == 0:
        tl.set_green()
    else:
        tl.set_red()

# Bind the Enter key for ambulance priority.
root.bind("<Return>", priority_handler)

# Start the countdown timer.
update_timer()

# Run the Tkinter event loop.
root.mainloop()