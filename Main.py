import sys
from PyQt5 import QtGui
import cv2
import numpy as np
import threading
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

from fchola import HiloEjemplo

bloqueo = threading.Lock()
hilo1 = HiloEjemplo(bloqueo)


def inicioHilos():
    hilo1.start()

def pararHilos():
    hilo1.detener_hilo()

def obtener_webcams():
        webcams = []
        index = 0

        while True:
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if not cap.isOpened():
                break

            _, frame = cap.read()
            if frame is not None:
                webcam_name = f"Webcam {index}"
                webcams.append(webcam_name)
            
            cap.release()
            index += 1

        cap.release()
        return webcams

class VentanaVideo(QMainWindow):
    def __init__(self):
        super().__init__()
        webcams = obtener_webcams()
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = 0
        self.label = QLabel(self)
        self.setCentralWidget(self.label)


        #inicioHilos()

        self.labelCamara = self.crear_label("Camara:",1290, 5, 50, 30)
        self.comboCamaras = self.crear_combobox(webcams, 1290, 35, 100, 30, 0)
        self.comboCamaras.currentIndexChanged.connect(self.cambio_camara)
        self.actualizar_video()

    def cambio_camara(self,index):
        opcion = self.comboCamaras.itemText(index)
        print(f"opcion seleccionada: {opcion}")
        numero = int(re.search(r'\d+', opcion).group())
        self.cap = cv2.VideoCapture(numero, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
    
    def closeEvent(self, event):
        pararHilos()
        event.accept()

    def crear_combobox(self, opciones, posX, posY, largo, ancho, default):
        # Crear instancia de QComboBox
        combo_box = QComboBox(self)
        # Configurar opciones del ComboBox
        combo_box.addItems(opciones)
        # Establecer posición y tamaño del ComboBox
        combo_box.setGeometry(posX, posY, largo, ancho)
        combo_box.setCurrentIndex(default)
        return combo_box
    
    def crear_label(self, texto, posX, posY, largo, ancho):
        # Crear instancia de QLabel
        label = QLabel(self)
        label.setText(texto)
        label.setGeometry(posX, posY, largo, ancho)
        return label
        
    def actualizar_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
            imagen = QPixmap.fromImage(imagen)
            self.label.setPixmap(imagen)
            
        self.frame_count += 1
        
        # Establecer el tiempo de espera en base a los fps del video
        tiempo_espera = 5
        QTimer.singleShot(tiempo_espera, self.actualizar_video)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    ventana = VentanaVideo()
    ventana.setFixedSize(1400,720)
    ventana.show()
    
    sys.exit(app.exec_())

