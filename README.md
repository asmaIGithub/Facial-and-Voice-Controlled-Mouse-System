# 🖱️ Facial and Voice-Controlled Mouse System

A hands-free, AI-powered mouse control system that uses **facial gestures** and **voice commands** to control the mouse — ideal for accessibility, sterile environments, or hands-busy scenarios.

---

## 📌 Features

- 🎯 Real-time **facial landmark detection** using `dlib`
- 🧠 Cursor movement based on **nose direction**
- 👁️ Eye blink/wink detection for **clicks and scroll toggling**
- 🗣️ Voice command recognition using `speech_recognition`
- 🧩 Integrated **Chrome extension** to control system via UI
- 🌐 Backend API using **Flask** to handle extension inputs

---

## 🎥 Demo

> Control your computer just by looking around, blinking, and speaking!

- Blink left/right eye → Left/Right click
- Mouth open → Toggle Input Mode
- Head direction → Move mouse or scroll
- Voice command: "Click", "Scroll mode on", "Stop", etc.

---

## 🛠️ Technologies Used

| Category        | Libraries/Tools              |
|----------------|------------------------------|
| Computer Vision | OpenCV, dlib                 |
| Mouse Control   | pyautogui                    |
| Voice Input     | speech_recognition (Google API) |
| Backend API     | Flask, flask-cors            |
| UI Integration  | Chrome Extension (Manifest V3) |
| Others          | threading, numpy             |

---

## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt

