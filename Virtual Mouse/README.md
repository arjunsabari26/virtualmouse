# Virtual Mouse Controller Using Hand Gestures

This project implements a touchless cursor controller allowing users to interact with their computers using hand gestures tracked in real-time by a webcam. 

Using **Python, MediaPipe Hands, OpenCV, and PyAutoGUI**, the system interprets specific physical signals—such as raising specific fingers and tracking their distances relative to one another—and translates them seamlessly into executable mouse events.

## Features
- **Real-time Cursor Movement:** Move your cursor around the screen by simply pointing and moving your index finger.
- **Gesture-based Clicking:** Intuitive left and right-clicking without physical buttons.
- **Gesture-based Scrolling:** Dynamic swiping with two fingers vertically to scroll web pages and documents effortlessly.
- **Smooth Object Tracking:** Uses movement smoothening algorithms alongside OpenCV frame reductions ensuring accurate translation minimizing cursor jittering.

---

## Gesture Mapping

| Action | Hand Gesture |
| :--- | :--- |
| **Move Cursor** | **Index Finger Up** (Middle, Ring, and Pinky down) |
| **Left Click** | **Index + Middle Finger Up AND close to each other** |
| **Right Click** | **Index + Middle + Ring Finger Up AND close to each other** |
| **Scroll** | **Index + Middle Finger Up (separated) AND moving vertically up/down** |

---

## 🛠️ Requirements & Installation

1. Clone or download the source code locally.
2. Open your terminal in the target directory (where `main.py` is located).
3. Ensure you have Python installed. If not, download it from [python.org](https://www.python.org/).
4. Create a virtual environment (Optional but Recommended):
   ```bash
   python -m venv venv
   # Activate it (Windows)
   venv\Scripts\activate
   # Activate it (Mac/Linux)
   source venv/bin/activate
   ```
5. Install the required dependencies using the provided `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Running The Application

To launch your Virtual Mouse Controller, run the python script using your terminal:
```bash
python main.py
```

### Tips for Best Use:
1. **Background & Lighting**: Ensure you are in a well-lit room for MediaPipe to comfortably analyze key points continuously. 
2. **Camera Positioning**: Face the webcam clearly with your hand fully inside the bounding border area visible in the tracking window.
3. **Escaping**: To immediately exit the background application securely, press the **`Esc`** key on your physical keyboard while focused on the Camera tracking window.

---

## Potential Limitations
- High dependence on steady environmental lighting. Low-light setups may negatively affect hand landmark point tracking.
- Lower webcam quality might induce minor gesture translation delays.
- Hand occlusion or complex background visuals behind your hand can interrupt accuracy metrics.
