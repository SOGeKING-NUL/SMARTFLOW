import tkinter as tk
import random
import serial
import threading
import time
import winsound  # Windows-specific sound alerts

# ------------------- Configuration -------------------
SERIAL_PORT = 'COM3'  # Update this to match your ESP32 port
BAUD_RATE = 9600

# ------------------- Global Variables -------------------
countdown = random.randint(12, 15)
active_light_index = 0
ambulance_priority = False
dsp_priority = False
in_priority_cycle = False
next_normal_index = None

LANE_NAMES = {0: "North Lane", 1: "East Lane", 2: "Ambulance Lane", 3: "DSP Lane"}

congestion_data = {i: {"level": random.randint(12, 70), "label": None} for i in range(4)}
CONGESTION_THRESHOLD = 65
serviced_lanes = set()
serial_running = True

# ------------------- TrafficLight Class -------------------
class TrafficLight:
    def _init_(self, parent, lane_name, lane_index):
        self.frame = tk.Frame(parent, bg="#2E3440")
        self.lane_index = lane_index

        tk.Label(self.frame, text=lane_name, font=("Helvetica", 14, "bold"),
                 bg="#2E3440", fg="#88C0D0").pack(pady=(0,5))

        self.canvas = tk.Canvas(self.frame, width=150, height=320,
                                bg="#2E3440", highlightthickness=0)
        self.canvas.pack()

        self.canvas.create_rectangle(20,10,130,310,
                                     fill="#3B4252", outline="#4C566A", width=2)
        self.red_light = self.canvas.create_oval(35,30,115,110,
                                                 fill="red", outline="#ECEFF4", width=2)
        self.green_light = self.canvas.create_oval(35,200,115,280,
                                                   fill="gray", outline="#ECEFF4", width=2)

        congestion_level = congestion_data[lane_index]["level"]
        color = "#BF616A" if congestion_level >= CONGESTION_THRESHOLD else "#A3BE8C"
        lbl = tk.Label(self.frame,
                       text=f"Congestion: {congestion_level}%",
                       font=("Helvetica",12), bg="#2E3440", fg=color)
        lbl.pack(pady=(5,0))
        congestion_data[lane_index]["label"] = lbl

    def set_green(self):
        self.canvas.itemconfig(self.red_light, fill="gray")
        self.canvas.itemconfig(self.green_light, fill="green")

    def set_red(self):
        self.canvas.itemconfig(self.red_light, fill="red")
        self.canvas.itemconfig(self.green_light, fill="gray")

    def update_congestion_display(self):
        level = congestion_data[self.lane_index]["level"]
        color = "#BF616A" if level >= CONGESTION_THRESHOLD else "#A3BE8C"
        congestion_data[self.lane_index]["label"].config(
            text=f"Congestion: {level}%", fg=color)

# ------------------- GUI Setup -------------------
root = tk.Tk()
root.title("Smart Traffic Management System")
root.configure(bg="#2E3440")

tk.Label(root,text="Smart Traffic Management System",
         font=("Helvetica",24,"bold"),bg="#2E3440",
         fg="#ECEFF4").pack(pady=(20,10))

timer_label=tk.Label(root,text="",font=("Helvetica",16),
                     bg="#2E3440",fg="#ECEFF4")
timer_label.pack(pady=(10,5))

priority_label=tk.Label(root,text="",font=("Helvetica",16,"bold"),
                        bg="#2E3440",fg="#BF616A")
priority_label.pack(pady=(0,10))

status_label=tk.Label(root,text="Initializing...",
                      font=("Helvetica",14),
                      bg="#2E3440",fg="#88C0D0")
status_label.pack(pady=(0,20))

lights_frame=tk.Frame(root,bg="#2E3440")
lights_frame.pack(pady=10)

traffic_lights=[]
for i in range(4):
    tl=TrafficLight(lights_frame,
                    LANE_NAMES[i],i)
    tl.frame.grid(row=i//2,column=i%2,padx=10,pady=10)
    traffic_lights.append(tl)

traffic_lights[active_light_index].set_green()

# ------------------- Helper Functions -------------------
def update_congestion_levels():
    for lane in congestion_data:
        congestion_data[lane]["level"]=random.randint(12,70)
        traffic_lights[lane].update_congestion_display()

def check_congestion():
    lanes=[(l,d["level"]) for l,d in congestion_data.items()
           if d["level"]>=CONGESTION_THRESHOLD and l not in serviced_lanes]
    return max(lanes,key=lambda x:x[1])[0] if lanes else None

def manage_cycle():
    global serviced_lanes
    if len(serviced_lanes)==4:
        serviced_lanes.clear()
    for lane in range(4):
        if lane not in serviced_lanes:
            serviced_lanes.add(lane)
            return lane
    serviced_lanes.clear()
    return 0

def alert_vehicle(vehicle,lane):
    freq,dur=(1000,500) if vehicle=="ambulance" else (700,500)
    winsound.Beep(freq,dur)
    priority_label.config(text=f"{vehicle.upper()} detected in {LANE_NAMES[lane]}!")
    root.after(3000,lambda:priority_label.config(text=""))

def set_priority(vehicle,lane):
    global ambulance_priority,dsp_priority
    if vehicle=="ambulance":
        ambulance_priority=True
    elif vehicle=="DSP":
        dsp_priority=True
    alert_vehicle(vehicle,lane)

def serial_monitor():
    global serial_running
    try:
        ser=serial.Serial(SERIAL_PORT,BAUD_RATE,timeout=1)
        status_label.config(text="RFID reader connected")
        while serial_running:
            line=ser.readline().decode().strip().lower()
            if "ambulance" in line:
                root.after(0,set_priority,"ambulance",2)
            elif "dsp" in line:
                root.after(0,set_priority,"DSP",3)
            time.sleep(0.1)
    except Exception as e:
        status_label.config(text=f"Serial error: {e}")

threading.Thread(target=serial_monitor,
                 daemon=True).start()

def update_timer():
    global countdown,in_priority_cycle,next_normal_index
    global active_light_index,dsp_priority,ambulance_priority

    timer_label.config(text=f"Time remaining: {countdown}s")
    if countdown>0:
        countdown-=1
        root.after(1000,update_timer)
    else:
        traffic_lights[active_light_index].set_red()

        if ambulance_priority:
            next_normal_index=(active_light_index+1)%4
            active_light_index,in_priority_cycle,countdown=2,True,25
            ambulance_priority=False

        elif dsp_priority and not ambulance_priority:
            next_normal_index=(active_light_index+1)%4
            active_light_index,in_priority_cycle,countdown=3,True,25
            dsp_priority=False

        elif in_priority_cycle:
            active_light_index,countdown,in_priority_cycle=next_normal_index,\
                random.randint(12,15),False

        else:
            congested_lane=check_congestion()
            active_light_index,countdown=(congested_lane or manage_cycle()),\
                random.randint(12,15)

        traffic_lights[active_light_index].set_green()
        update_congestion_levels()
        root.after(1000,update_timer)

def priority_handler(event):
    set_priority("ambulance",2)

root.bind("<Return>",priority_handler)

def on_closing():
    global serial_running
    serial_running=False;time.sleep(.5);root.destroy()

root.protocol("WM_DELETE_WINDOW",on_closing)

update_timer()
root.mainloop()