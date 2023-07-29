import tensorflow as tf 
import time
import numpy as np
from PIL import Image
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

class clasificadorTipoBola():
    def __init__(self):
        self.img_height = 180
        self.img_width = 180
        self.class_names=['Blanca', 'Lisa', 'Negra', 'Rayada']
        self.model = tf.keras.models.load_model(script_dir + "\\classification-model\\v1.0\\")


    def clasificar(self, img:Image):    
        img=img.resize((self.img_height,self.img_width))
        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)

        predictions = self.model.predict(img_array)
        score = tf.nn.softmax(predictions[0])

        print(
            "{}. {:.2f}"
            .format(self.class_names[np.argmax(score)], 100 * np.max(score))
        )
        
        return self.class_names[np.argmax(score)], 100 * np.max(score)