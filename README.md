# 🎸 Guitar Tuner System — Python

> A Python-based Guitar Tuner System that detects sound frequency from a microphone and determines whether a guitar string is correctly tuned.
>
> **Batangas State University | CC 102 — Advanced Computer Programming**
> **Student:** Soreta, Anthony S. 

---

## 🛠️ Dependencies Installation

Before running the Guitar Tuner, install the required dependencies based on your OS.

---

### Requirements

This project uses:

- **Python 3** — main programming language
- **tkinter** — GUI window and widgets *(built-in with Python)*
- **Pillow** — for displaying the guitar image
- **NumPy** — for FFT frequency analysis
- **SciPy** — for HPS (Harmonic Product Spectrum) signal processing
- **sounddevice** — for real-time microphone input
- **PortAudio** — required by sounddevice for audio I/O

---

## 📦 Installation Guide

### 🍎 macOS

Install dependencies using [Homebrew](https://brew.sh):

```bash
brew install python portaudio
```

Install Python libraries:

```bash
pip3 install pillow numpy scipy sounddevice
```

If tkinter is missing:

```bash
brew install python-tk
```

---

### 🪟 Windows

Install Python from [python.org](https://www.python.org/downloads/) then run:

```bash
pip install pillow numpy scipy sounddevice
```

> **Note:** tkinter is included by default in the Windows Python installer.

---

### 🐧 Linux

```bash
sudo apt install python3 python3-pip portaudio19-dev python3-tk
pip3 install pillow numpy scipy sounddevice
```

---

## ▶️ How to Run

Make sure `guitar.png` is in the same folder as `guitar_tuner.py`, then:

```bash
python3 guitar_tuner.py
```

---

## 🖥️ How to Use

| Action | Result |
|---|---|
| Click a string circle (D, A, E, G, B, E) | Manually select that string |
| Double-click anywhere | Return to **Auto mode** |
| Play a string near the mic | Tuner detects frequency automatically |

---

## 🎯 Features

- **display_menu()** — Displays tuning instructions in the terminal
- **Capture Audio** — Records real-time sound from the microphone
- **Detect Frequency** — Analyzes pitch using FFT + HPS algorithm
- **Identify String** — Compares detected frequency with standard tuning
- **Display Result** — Shows **FLAT ▼**, **SHARP ▲**, or **IN TUNE ✓**

---

## 🔬 Algorithm Used

This project uses the **Harmonic Product Spectrum (HPS)** algorithm based on the research by [chciken](https://www.chciken.com/digital/signal/processing/2020/05/13/guitar-tuner.html) for accurate pitch detection.

| Technique | Description |
|---|---|
| **Hann Window** | Reduces spectral leakage |
| **HPS** | Multiplies harmonics to find true fundamental frequency |
| **Mains Hum Suppression** | Removes noise below 62 Hz |
| **White Noise Suppression** | Per-octave band filtering |
| **Power Threshold** | Ignores silence or very quiet input |
| **Note Buffer (Majority Vote)** | Confirms note only if 2 readings agree |
| **Frequency Averaging** | Averages last 5 readings for stability |

---

## 🎸 Standard Guitar Tuning Frequencies

| String | Note | Frequency |
|--------|------|-----------|
| 6th (thickest) | E2 | 82.41 Hz |
| 5th | A2 | 110.00 Hz |
| 4th | D3 | 146.83 Hz |
| 3rd | G3 | 196.00 Hz |
| 2nd | B3 | 246.94 Hz |
| 1st (thinnest) | E4 | 329.63 Hz |

---

## 🗂️ Data Structures Used

| Data Structure | Purpose |
|---|---|
| `dict` — `strings` | Stores standard frequencies with string name as key |
| `list` — `frequency_buffer` | Stores last 5 frequency readings for averaging |
| `list` — `note_buffer` | Stores last 2 notes for majority vote |

---

## 📁 Project Structure

```
Guitar-Tuner-Python/
│
├── guitar_tuner.py   # Main program
├── guitar.png        # Guitar image used in the GUI
└── README.md         # This file
```

---

## 📚 References

- chciken. (2020). *Guitar Tuner using Digital Signal Processing*. https://www.chciken.com/digital/signal/processing/2020/05/13/guitar-tuner.html
- sounddevice documentation: https://python-sounddevice.readthedocs.io
- NumPy FFT documentation: https://numpy.org/doc/stable/reference/routines.fft.html

---

## 📄 License

This project was made for academic purposes only.
**Batangas State University — College of Informatics and Computing Sciences**
