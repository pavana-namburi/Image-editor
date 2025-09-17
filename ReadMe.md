# Image to Pencil Sketch Converter 🖼️✏️

Convert photos into realistic pencil sketches with a desktop GUI built in Python (Tkinter) and OpenCV.  
This app produces natural-looking lines and shading, suitable for fun edits or demo projects.

---

## ✨ Features
- Convert any photo to a pencil sketch effect  
- Dark sketch option, vintage filter, grayscale, brightness adjustment  
- Undo, save, zoom, and pan features  
- Works fully offline with Python  

---

## 📸 Demo
Input vs Sketch Example:  

| Original Image | Pencil Sketch |
|----------------|---------------|
| ![Input](demo.jpg) | ![Output](output.jpg) |

---

## ⚙️ Requirements
- Python 3.8+  
- Install dependencies:
  ```bash
  pip install opencv-python Pillow numpy
- tkinter (usually comes with Python; install separately if missing):
  ```bash
  sudo apt install python3-tk    # Linux (Debian/Ubuntu)

---

## 🚀 Run the Project
- Clone the repo:
    ```bash
    git clone https://github.com/pavana-namburi/Image-editor
    cd Image-editor

---

## 📂 Project Structure
    
    ```bash
        ├── index.py       # Main script
        ├── demo.png       # Sample input image
        ├── output.jpg     # Sample output sketch
        ├── README.md      # Documentation 

---

## ⚙️ How It Works
- The image is first converted to grayscale.
- An inverted copy is created and blurred using Gaussian blur.
- OpenCV’s cv2.divide() blends the grayscale image with the inverted blurred version.
- This produces a natural-looking pencil sketch effect.
- Tkinter GUI provides options like undo, save, zoom, and brightness adjustment.

---

## 🤝 Contributing
- Contributions are welcome!
- Fork this repo
- Create a new branch (feature-xyz)
- Commit your changes
- Submit a Pull Request 🚀

---

## 📌 Future Improvements:
- Add color sketch mode
- Support more image formats (PNG, BMP, TIFF)
- Export as standalone .exe or .app for easy use

