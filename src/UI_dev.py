import tkinter as tk
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont
import subprocess
import json
import datetime

import matplotlib.pyplot as plt


class ImageApp:
    OUTPUT_FOLDER = 'result/'
    training_script_path = 'train.py'
    INPUT_FOLDER = "predicted_images/"
    COCO_FILENAME = "coco_predictions.json"
    CANVAS_WIDTH = 1800
    CANVAS_HEIGHT = 1000
    #COLORS = [(0.000, 0.447, 0.741), (0.850, 0.325, 0.098), (0.929, 0.694, 0.125), (0.494, 0.184, 0.556), (0.466, 0.674, 0.188), (0.301, 0.745, 0.933)]
    COLORS = [(100, 100, 100), (234, 123, 35), (211, 85, 111)]
    no_images_left_placeholder = "../resources/placeholder.jpg"

    def __init__(self, root):
        self.draw = None
        self.root = root
        self.root.title("Auswertung Erkennung Buchschäden")
        self.root.geometry(f"{self.CANVAS_WIDTH}x{self.CANVAS_HEIGHT + 110}")



        with open(os.path.join(self.INPUT_FOLDER, self.COCO_FILENAME), "r") as f:
            self.coco_file = json.load(f)

        self.label = {k["id"]: k['name'] for k in self.coco_file["categories"]} # überprüfen, ob es so funktioniert, statt items vielleicht enumerate oder sowas? oder zwei argumente? kommt auf die zusammenstellung der daten drauf an

        self.sum_damages = {}


        self.image_id = 0
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



        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())

        self.load_from_directory()

    def load_from_directory(self):
        # TODO Extract filenames directly, to be used in the drawing of the image bzw extracting bbox infos from coco file


        self.image_paths = [os.path.join(self.INPUT_FOLDER, filename) for filename in os.listdir(self.INPUT_FOLDER) if
                            filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        self.show_current_image()

    def show_current_image(self):
        if self.image_paths:
            image_path = self.image_paths[self.image_index]
            image = Image.open(image_path)
            width, height = image.size
            self.scale = [self.CANVAS_WIDTH/(width), (self.CANVAS_HEIGHT/height)]
            #image.thumbnail((self.CANVAS_WIDTH, self.CANVAS_HEIGHT))
            image_name = image_path.split("/")[-1]

            print(self.scale, self.CANVAS_WIDTH, width)

            # extract image id for current image
            # image_id = self.coco_file["images"][self.image_index]["id"] # would work if images in the directory and in the cocofile had the exact same order
            

            # Create an ImageDraw object to draw on the image
            self.draw = ImageDraw.Draw(image)
            self.filename_label.config(text=os.path.basename(image_path))

            if not self.detected_damage_queue:
                self.detected_damage_queue = self.get_detected_damage(image_name)

            self.drawDamages(self.draw, self.detected_damage_queue)
            
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

    def createCOCOStructure(originalData, description):
        cocoStructure = {
            "info": [{"year": int(datetime.date.today().year)},
                    {"version": "Static"},
                    {"description": description},
                    {"contributer": "Michael Infanger"},
                    {"url": ""},
                    {"date_created": str(datetime.datetime.now())}],
            "categories": originalData["categories"],
            "images": [],
            "annotations": []
        }
        return cocoStructure

    def get_detected_damage(self, image_name):
        for i in range(len(self.coco_file["images"])):
            if self.coco_file["images"][i]["file_name"] == image_name:
                self.image_id = self.coco_file["images"][i]["id"]
        annotations = []
        for n in range(len(self.coco_file["annotations"])):

            if self.coco_file["annotations"][n]["image_id"] == self.image_id:
                annotations.append(self.coco_file["annotations"][n])
        return annotations
    
    def deleteDraws(self):
        # TODO delete drawings on using a new image, if needed
        pass

    def drawDamages(self, draw, annotations):

        #deleteDraws()
        

        colors = self.COLORS * 100

        self.sum_damages = {}
        for i in range(len(annotations)):
            label = int(annotations[i]["category_id"])
            bbox = annotations[i]["bbox"]
            c = colors[i]
            
            # There is somewhere an error in the conversion, these are the values that function.
            # As this was not a priority part and other things were more important, it was left like this.
            self.scale[0] = 1.615
            self.scale[1] = 0.615

            xmin, ymin, xmax, ymax = bbox
            # print(xmin, ymin, xmax, ymax)
            xmin, ymin, xmax, ymax = xmin * self.scale[0] , ymin * self.scale[1], xmax * self.scale[0], ymax * self.scale[1]
            
            # print(xmin * self.scale[0], ymin * self.scale[1], xmax * self.scale[0], ymax * self.scale[1])
            draw.rectangle([xmin, ymin, 
                            xmax, ymax],
                            fill=None, 
                            outline="red", 
                            width=2)
            
            text = f'{self.label[label]}'
            if text in self.sum_damages:
                self.sum_damages.update({text: self.sum_damages[text] + 1})
            else: 
                self.sum_damages.update({text:1})
            draw.text((xmin, ymin), 
                      text, 
                      font_size=10)
            
        print(self.sum_damages)
        #plt.axis('off')
 




if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()

# UI ausbaumöglichkeit: anzeigen welche predictions welchen prozentwert/score haben. Eine möglichkeit einbauen einen 
# schieberegler von 0 bis 100 zu haben der die eingezeichneten predictions danach anpasst