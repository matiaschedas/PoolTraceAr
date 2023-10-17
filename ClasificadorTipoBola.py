import tensorflow as tf 
import time
import numpy as np
from PIL import Image
import os
from datetime import datetime
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))

class clasificadorTipoBola():
    def __init__(self):
        self.img_height = 50
        self.img_width = 50
        self.class_names=['Blanca', 'Lisa', 'Negra', 'Rayada']
        self.model = tf.keras.models.load_model(script_dir + "\\classification-model\\v1.0\\", compile=False)
        self.id = 0

    def clasificar(self, img:Image, guardarHistorial):
        img_original=img.copy()    
        img=img.resize((self.img_height,self.img_width))
        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)

        predictions = self.model.predict(img_array)
        score = tf.nn.softmax(predictions[0])
        self.id = self.id+1
        fecha_hora_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombreImg = "crop_"+ str(self.id)+ "_" + fecha_hora_actual + " - " + self.class_names[np.argmax(score)] + " - " + str(100 * np.max(score)).replace(".","-") + ".png"
        carpeta = Path(script_dir + '/Capturas/Historial/')
        if not carpeta.exists():
            carpeta.mkdir(parents=True, exist_ok=True)
        if(guardarHistorial):
            img_original.save(script_dir + "\\Capturas\\Historial\\" + nombreImg)
        print(
            "{}. {:.2f}"
            .format(self.class_names[np.argmax(score)], 100 * np.max(score))
        )
        
        return self.class_names[np.argmax(score)], 100 * np.max(score)