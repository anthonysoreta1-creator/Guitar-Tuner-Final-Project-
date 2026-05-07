import copy
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import numpy.fft as fft
import sounddevice as sd

# ================= ADDED: display_menu() =================
def display_menu():
    print("=" * 50)
    print("       GUITAR TUNER SYSTEM")
    print("=" * 50)
    print("Standard Tuning Frequencies:")
    print("  E (low)  - 82.41 Hz")
    print("  A        - 110.00 Hz")
    print("  D        - 146.83 Hz")
    print("  G        - 196.00 Hz")
    print("  B        - 246.94 Hz")
    print("  E (high) - 329.63 Hz")
    print("=" * 50)
    print("Instructions:")
    print("  - Click a string circle to manually select it.")
    print("  - Double-click anywhere to return to AUTO mode.")
    print("  - Play your guitar string near the microphone.")
    print("  - Status will show: FLAT, SHARP, or IN TUNE.")
    print("=" * 50)
    print("Starting Guitar Tuner... Close the window to exit.")
    print() 

display_menu()


frequency_buffer = []
BUFFER_SIZE = 10

# ================= ADDED: HPS Settings (from research) =================
SAMPLE_FREQ        = 48000      
WINDOW_SIZE        = 48000      
WINDOW_STEP        = 12000
NUM_HPS            = 5          
POWER_THRESH       = 1e-6       
CONCERT_PITCH      = 440        
WHITE_NOISE_THRESH = 0.2        
DELTA_FREQ         = SAMPLE_FREQ / WINDOW_SIZE
OCTAVE_BANDS       = [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600]
HANN_WINDOW        = np.hanning(WINDOW_SIZE)

# ADDED: All chromatic notes (research formula covers any note, not just the 6 strings)
ALL_NOTES = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]

# ADDED: find_closest_note() from research — uses log2 formula for accurate note mapping
def find_closest_note(pitch):
    i = int(np.round(np.log2(pitch / CONCERT_PITCH) * 12))
    closest_note  = ALL_NOTES[i % 12] + str(4 + (i + 9) // 12)
    closest_pitch = CONCERT_PITCH * 2 ** (i / 12)
    return closest_note, closest_pitch

#  UI 
root = tk.Tk()
root.title("Guitar Tuner")
root.geometry("500x650")
root.configure(bg="black")

label = ttk.Label(
    root,
    text="Guitar Tuner",
    font=("Arial", 16),
    background="black",
    foreground="green"
)
label.pack(pady=20)

main_frame = tk.Frame(root, bg="black")
main_frame.pack(fill="both", expand=True)

left_frame = tk.Frame(main_frame, bg="black")
left_frame.pack(side="left", expand=True)

center_frame = tk.Frame(main_frame, bg="black")
center_frame.pack(side="left", expand=True)

right_frame = tk.Frame(main_frame, bg="black")
right_frame.pack(side="right", expand=True)

circles = {}
selected_string = None

def make_circle(parent, letter, display):
    canvas = tk.Canvas(parent, width=60, height=60,
                       bg="black", highlightthickness=0)
    canvas.pack(pady=22)

    circle = canvas.create_oval(5, 5, 55, 55,
                               fill="#808080",
                               outline="#808080")

    canvas.create_text(30, 30,
                       text=display,
                       font=("Arial", 20, "bold"),
                       fill="white")

    circles[letter] = (canvas, circle)

    def on_click(event):
        select_string(letter)

    canvas.bind("<Button-1>", on_click)

# Left
make_circle(left_frame, "D", "D")
make_circle(left_frame, "A", "A")
make_circle(left_frame, "E_low", "E")

# Center Image
img = Image.open("guitartuner.jpg")
img = img.resize((260, 360))
photo = ImageTk.PhotoImage(img)

img_label = tk.Label(center_frame, image=photo, bg="black")
img_label.image = photo
img_label.pack(expand=True)

# Right
make_circle(right_frame, "G", "G")
make_circle(right_frame, "B", "B")
make_circle(right_frame, "E_high", "E")

# STATUS LABEL
status_label = tk.Label(
    root,
    text="Listening...",
    font=("Arial", 16, "bold"),
    bg="black",
    fg="white"
)
status_label.pack(pady=20)

# ================= FUNCTIONS =================

def update_status(state):
    # ADDED: Updated wording to match proposal (Flat / Sharp / In Tune)
    if state == "high":
        status_label.config(text="SHARP ▲", fg="#00BFFF")
    elif state == "low":
        status_label.config(text="FLAT ▼", fg="#FFA500")
    elif state == "tuned":
        status_label.config(text="IN TUNE ✓", fg="#00FF7F")
    elif state == "silence":
        status_label.config(text="Listening...", fg="white")

def highlight(string, state):
    for key in circles:
        canvas, circle = circles[key]
        canvas.itemconfig(circle, fill="#808080")

    if string is None:
        return

    canvas, circle = circles[string]

    if state == "high":
        color = "#00BFFF"
    elif state == "low":
        color = "#FFA500"
    else:
        color = "#00FF7F"

    canvas.itemconfig(circle, fill=color)

def select_string(string):
    global selected_string
    selected_string = string

    for key in circles:
        canvas, circle = circles[key]
        canvas.itemconfig(circle, outline="#808080", width=1)

    canvas, circle = circles[string]
    canvas.itemconfig(circle, outline="yellow", width=3)

def reset_auto(event=None):
    global selected_string
    selected_string = None

    for key in circles:
        canvas, circle = circles[key]
        canvas.itemconfig(circle, outline="#808080", width=1)

root.bind("<Double-Button-1>", reset_auto)

# TUNER 

strings = {
    "E_low":  82.41,
    "A":     110.00,
    "D":     146.83,
    "G":     196.00,
    "B":     246.94,
    "E_high":329.63
}


NOTE_TO_STRING = {
    "E2": "E_low",
    "A2": "A",
    "D3": "D",
    "G3": "G",
    "B3": "B",
    "E4": "E_high",
}

def detect_string(freq):
    closest = None
    min_diff = 999
    for string, target in strings.items():
        diff = abs(freq - target)
        if diff < min_diff:
            min_diff = diff
            closest = string
    return closest

window_samples = [0.0] * WINDOW_SIZE
note_buffer    = ["1", "2"]  

def process_audio(indata, frames, time, status):
    global window_samples, note_buffer, frequency_buffer

    if status:
        print(status)
        return

    if not any(indata):
        root.after(0, update_status, "silence")
        root.after(0, highlight, None, None)
        return

    window_samples = np.concatenate((window_samples, indata[:, 0]))
    window_samples = window_samples[len(indata[:, 0]):]

    signal_power = (np.linalg.norm(window_samples, ord=2) ** 2) / len(window_samples)
    if signal_power < POWER_THRESH:
        root.after(0, update_status, "silence")
        root.after(0, highlight, None, None)
        return

    hann_samples   = window_samples * HANN_WINDOW
    magnitude_spec = np.abs(fft.fft(hann_samples)[:len(hann_samples) // 2])

    for i in range(int(62 / DELTA_FREQ)):
        magnitude_spec[i] = 0

    # ADDED: White noise suppression per octave band 
    for j in range(len(OCTAVE_BANDS) - 1):
        ind_start = int(OCTAVE_BANDS[j] / DELTA_FREQ)
        ind_end   = int(OCTAVE_BANDS[j + 1] / DELTA_FREQ)
        ind_end   = ind_end if len(magnitude_spec) > ind_end else len(magnitude_spec)
        avg_energy = (np.linalg.norm(magnitude_spec[ind_start:ind_end], ord=2) ** 2) / (ind_end - ind_start)
        avg_energy = avg_energy ** 0.5
        for i in range(ind_start, ind_end):
            if magnitude_spec[i] < WHITE_NOISE_THRESH * avg_energy:
                magnitude_spec[i] = 0

    mag_spec_ipol = np.interp(
        np.arange(0, len(magnitude_spec), 1 / NUM_HPS),
        np.arange(0, len(magnitude_spec)),
        magnitude_spec
    )
    mag_spec_ipol = mag_spec_ipol / np.linalg.norm(mag_spec_ipol, ord=2)

    hps_spec = copy.deepcopy(mag_spec_ipol)
    for i in range(NUM_HPS):
        tmp = np.multiply(
            hps_spec[:int(np.ceil(len(mag_spec_ipol) / (i + 1)))],
            mag_spec_ipol[::(i + 1)]
        )
        if not any(tmp):
            break
        hps_spec = tmp

    max_ind  = np.argmax(hps_spec)
    max_freq = max_ind * (SAMPLE_FREQ / WINDOW_SIZE) / NUM_HPS
 
    frequency_buffer.append(max_freq)
    if len(frequency_buffer) > BUFFER_SIZE:
        frequency_buffer.pop(0)
    avg_freq = sum(frequency_buffer) / len(frequency_buffer)

    closest_note, closest_pitch = find_closest_note(avg_freq)

    note_buffer.insert(0, closest_note)
    note_buffer.pop()
    if note_buffer.count(note_buffer[0]) != len(note_buffer):
        root.after(0, update_status, "silence")
        root.after(0, highlight, None, None)
        return

    if selected_string is not None:
        string = selected_string
    else:
        string = NOTE_TO_STRING.get(closest_note, detect_string(avg_freq))

    target = strings[string]

    TOLERANCE = 5

    if avg_freq > target + TOLERANCE:
        state = "high"
    elif avg_freq < target - TOLERANCE:
        state = "low"
    else:
        state = "tuned"

    root.after(0, update_status, state)
    root.after(0, highlight, string, state)

stream = sd.InputStream(
    channels=1,
    callback=process_audio,
    blocksize=WINDOW_STEP,
    samplerate=SAMPLE_FREQ
)
stream.start()

root.mainloop()