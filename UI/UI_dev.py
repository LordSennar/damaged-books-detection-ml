import tkinter as tk
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont
import subprocess



class ImageApp:
    OUTPUT_FOLDER = '../result/'
    training_script_path = 'train.py'
    INPUT_FOLDER = "../predicted_images/"
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 500
    no_images_left_placeholder = "../resources/placeholder.jpg"

    def __init__(self, root):
        self.draw = None
        self.root = root
        self.root.title("Auswertung Erkennung Buchschäden")
        self.root.geometry(f"{self.CANVAS_WIDTH}x{self.CANVAS_HEIGHT + 110}")

        self.image_index = 0
        self.image_paths = []
        self.current_image = None
        self.detected_damage_queue = []

        self.canvas = tk.Canvas(root, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT)
        self.canvas.pack()

        self.filename_label = tk.Label(root, text="", fg="gray", font=("Arial", 10))
        self.filename_label.pack()

        self.prev_button = tk.Button(root, text="Previous Image", command=self.prev_image)
        self.prev_button.pack(side="left")
        self.next_button = tk.Button(root, text="Next Image", command=self.next_image)
        self.next_button.pack(side="right")









        self.load_images_from_directory()

    def load_images_from_directory(self):
        self.image_paths = [os.path.join(self.INPUT_FOLDER, filename) for filename in os.listdir(self.INPUT_FOLDER) if
                            filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        print(self.image_paths)
        self.show_current_image()

    def show_current_image(self):
        if self.image_paths:
            image_path = self.image_paths[self.image_index]
            image = Image.open(image_path)
            width, height = image.size
            image.thumbnail((self.CANVAS_WIDTH, self.CANVAS_HEIGHT))

            # Create an ImageDraw object to draw on the image
            self.draw = ImageDraw.Draw(image)
            self.filename_label.config(text=os.path.basename(image_path))

            #if not self.detected_damage_queue:
                #self.detected_damage_queue = self.get_detected_damage(image_path, width, height)

            #self.draw_damage_info(self.draw, self.detected_damage_queue)
            
            image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
            self.canvas.image = image
            self.current_image = image
        else:
            self.show_placeholder()

    def show_placeholder(self):
        print("hi")
        placeholder = Image.open(self.no_images_left_placeholder)
        placeholder.thumbnail((self.CANVAS_WIDTH, self.CANVAS_HEIGHT))
        ph = ImageTk.PhotoImage(placeholder)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=ph)
        self.canvas.image = placeholder
        self.current_image = placeholder

    def prev_image(self):
        self.detected_damage_queue = []
        if self.image_paths:
            self.image_index = (self.image_index - 1) % len(self.image_paths)
            self.show_current_image()

    def next_image(self):
        self.detected_damage_queue = []
        if self.image_paths:
            self.image_index = (self.image_index + 1) % len(self.image_paths)
            self.show_current_image()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()