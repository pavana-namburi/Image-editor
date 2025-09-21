import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import numpy as np
import cv2

class SketchArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image to Sketch Art 🎨")
        self.root.geometry("1200x700")
        self.root.configure(bg="#fdfdfd")

        # Variables
        self.image_path = None
        self.original_image = None
        self.sketch_image = None
        self.undo_stack = []
        self.zoom_factor = 1.0
        self.pan_start_x = 0
        self.pan_start_y = 0

        # Toolbar (center top)
        self.toolbar_frame = tk.Frame(self.root, bg="#fdfdfd")
        self.toolbar_frame.pack(side=tk.TOP, pady=15)

        # Button font size increased
        self.btn_font = ("Arial", 12, "bold")

        # Add toolbar buttons
        self.add_button("Upload", self.upload_image, "#ffe0e0", "black")
        self.add_button("Pencil Art", self.convert_to_sketch, "#d4f1d4", "black")
        self.add_button("Dark Sketch", self.convert_to_dark_sketch, "#e0e0ff", "black")
        self.add_button("Vintage", self.apply_vintage_filter, "#ffeccc", "black")
        self.add_button("Grayscale", self.apply_grayscale, "#eeeeee", "black")
        self.add_button("Brightness", self.open_brightness_dialog, "#fff9c4", "black")
        self.add_button("Undo", self.undo_action, "#cce7ff", "black")
        self.add_button("Clear", self.clear_image, "#ffd6cc", "black")
        self.add_button("Save", self.save_image, "#cce5ff", "black")
        self.add_button("Zoom In", lambda: self.adjust_zoom(1.1), "#d7ffd9", "black")
        self.add_button("Zoom Out", lambda: self.adjust_zoom(0.9), "#f8d7da", "black")

        # Canvases
        self.canvas_frame = tk.Frame(self.root, bg="#fdfdfd")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas_original = tk.Canvas(self.canvas_frame, bg="white", width=550, height=500, 
                                         highlightthickness=1, highlightbackground="#aaa")
        self.canvas_original.pack(side=tk.LEFT, expand=True, padx=10, pady=10)

        self.canvas_sketch = tk.Canvas(self.canvas_frame, bg="white", width=550, height=500, 
                                       highlightthickness=1, highlightbackground="#aaa")
        self.canvas_sketch.pack(side=tk.RIGHT, expand=True, padx=10, pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=1000, mode="determinate")
        self.progress.pack(pady=5)

        # Status bar
        self.status = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, 
                               bg="#eeeeee", font=("Arial", 11))
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        # Mouse bindings
        self.canvas_sketch.bind("<MouseWheel>", self.zoom_image)
        self.canvas_sketch.bind("<Button-1>", self.start_pan)
        self.canvas_sketch.bind("<B1-Motion>", self.pan_image)

    def add_button(self, text, command, bg, fg):
        button = tk.Button(self.toolbar_frame, text=text, command=command, bg=bg, fg=fg,
                           font=self.btn_font, relief="ridge", bd=2, padx=10, pady=4)
        button.pack(side=tk.LEFT, padx=5)

    def set_status(self, msg):
        self.status.config(text=msg)
        self.status.update_idletasks()

    def resize_image(self, image, max_width, max_height):
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height

        if original_width > max_width or original_height > max_height:
            if aspect_ratio > 1:
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            else:
                new_height = max_height
                new_width = int(max_height * aspect_ratio)
        else:
            new_width, new_height = original_width, original_height

        return image.resize((new_width, new_height), Image.LANCZOS)

    def upload_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if not self.image_path:
            return
        try:
            self.original_image = Image.open(self.image_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {e}")
            return
        resized_image = self.resize_image(self.original_image, 550, 500)
        self.zoom_factor = 1.0
        self.display_original_image(resized_image)
        self.sketch_image = None
        self.undo_stack.clear()
        self.set_status("Image uploaded.")

    def display_original_image(self, image):
        self.original_tk_image = ImageTk.PhotoImage(image)
        self.canvas_original.delete("all")
        self.canvas_original.create_image(0, 0, anchor=tk.NW, image=self.original_tk_image)

    def display_sketch_image(self, image):
        if image is None:
            self.canvas_sketch.delete("all")
            return
        self.sketch_tk_image = ImageTk.PhotoImage(image)
        self.canvas_sketch.delete("all")
        self.canvas_sketch.create_image(0, 0, anchor=tk.NW, image=self.sketch_tk_image)

    def adjust_zoom(self, scale_factor):
        if self.sketch_image:
            image_to_zoom = self.sketch_image
        elif self.original_image:
            image_to_zoom = self.original_image
        else:
            return
        self.zoom_factor *= scale_factor
        new_size = (max(1, int(image_to_zoom.width * self.zoom_factor)), max(1, int(image_to_zoom.height * self.zoom_factor)))
        resized_image = image_to_zoom.resize(new_size, Image.LANCZOS)
        self.display_sketch_image(resized_image)

    def zoom_image(self, event):
        if event.delta > 0:
            self.adjust_zoom(1.1)
        else:
            self.adjust_zoom(0.9)

    def start_pan(self, event):
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def pan_image(self, event):
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        self.canvas_sketch.move(tk.ALL, dx, dy)
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def convert_to_sketch(self):
        if not self.image_path:
            messagebox.showerror("Error", "Please upload an image first.")
            return
        self.progress["value"] = 10
        self.progress.update_idletasks()
        cv_image = cv2.imread(self.image_path)
        if cv_image is None:
            messagebox.showerror("Error", "Failed to read image with OpenCV.")
            return
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        self.progress["value"] = 30
        self.progress.update_idletasks()
        inverted_image = cv2.bitwise_not(gray_image)
        blurred_image = cv2.GaussianBlur(inverted_image, (21, 21), 0)
        self.progress["value"] = 60
        self.progress.update_idletasks()
        sketch_image = cv2.divide(gray_image, 255 - blurred_image, scale=256.0)
        sketch_image_pil = Image.fromarray(sketch_image)
        self.undo_stack.append(self.sketch_image if self.sketch_image is not None else None)
        self.display_sketch_image(sketch_image_pil)
        self.sketch_image = sketch_image_pil
        self.progress["value"] = 100
        self.progress.update_idletasks()
        self.set_status("Pencil sketch applied.")
        self.progress["value"] = 0

    def convert_to_dark_sketch(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first.")
            return
        self.undo_stack.append(self.sketch_image if self.sketch_image is not None else None)
        grayscale_image = self.original_image.convert("L")
        inverted_image = Image.eval(grayscale_image, lambda x: 255 - x)
        blurred_image = inverted_image.filter(ImageFilter.GaussianBlur(21))
        self.sketch_image = Image.blend(grayscale_image, blurred_image, alpha=0.7)
        self.display_sketch_image(self.sketch_image)
        self.set_status("Dark sketch applied.")

    def apply_vintage_filter(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first.")
            return
        self.undo_stack.append(self.sketch_image if self.sketch_image is not None else None)
        vintage_image = np.array(self.original_image).astype(np.float32)
        if vintage_image.ndim == 2 or vintage_image.shape[2] == 1:
            # Convert grayscale to RGB for filter
            vintage_image = np.stack([vintage_image]*3, axis=-1)
        vintage_image[..., 0] *= 0.9
        vintage_image[..., 1] *= 0.8
        vintage_image[..., 2] *= 0.7
        vintage_image = np.clip(vintage_image, 0, 255).astype(np.uint8)
        self.sketch_image = Image.fromarray(vintage_image)
        self.display_sketch_image(self.sketch_image)
        self.set_status("Vintage filter applied.")

    def apply_grayscale(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first.")
            return
        self.undo_stack.append(self.sketch_image if self.sketch_image is not None else None)
        self.sketch_image = self.original_image.convert("L")
        self.display_sketch_image(self.sketch_image)
        self.set_status("Grayscale applied.")

    def open_brightness_dialog(self):
        if self.original_image is None:
            messagebox.showerror("Error", "Please upload an image first.")
            return
        brightness_factor = simpledialog.askfloat("Brightness", "Enter factor (0.0 to 2.0):", minvalue=0.0, maxvalue=2.0)
        if brightness_factor is not None:
            self.undo_stack.append(self.sketch_image if self.sketch_image is not None else None)
            enhancer = ImageEnhance.Brightness(self.original_image)
            self.sketch_image = enhancer.enhance(brightness_factor)
            self.display_sketch_image(self.sketch_image)
            self.set_status(f"Brightness set to {brightness_factor}")

    def clear_image(self):
        self.canvas_original.delete("all")
        self.canvas_sketch.delete("all")
        self.original_image = None
        self.sketch_image = None
        self.undo_stack.clear()
        self.set_status("Canvas cleared.")

    def undo_action(self):
        if self.undo_stack:
            last = self.undo_stack.pop()
            self.sketch_image = last
            self.display_sketch_image(self.sketch_image)
            self.set_status("Undo successful.")
        else:
            messagebox.showinfo("Undo", "No actions to undo.")

    def save_image(self):
        if self.sketch_image is None:
            messagebox.showwarning("Save", "No sketch image to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg")])
        if file_path:
            try:
                # Convert grayscale to RGB if saving as JPEG
                if file_path.lower().endswith((".jpg", ".jpeg")) and self.sketch_image.mode != "RGB":
                    img_to_save = self.sketch_image.convert("RGB")
                else:
                    img_to_save = self.sketch_image
                img_to_save.save(file_path)
                self.set_status("Image saved successfully.")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save image: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SketchArtApp(root)
    root.mainloop()
