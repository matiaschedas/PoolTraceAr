import sys
from PyQt5 import QtGui
import cv2
import numpy as np
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

from fchola import HiloEjemplo

bloqueo = threading.Lock()
hilo1 = HiloEjemplo(bloqueo)


def inicioHilos():
    hilo1.start()

def pararHilos():
    hilo1.detener_hilo()

class VentanaVideo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = 0
        self.label = QLabel(self)
        self.setCentralWidget(self.label)

        inicioHilos()

        self.actualizar_video()

    def closeEvent(self, event):
        pararHilos()
        event.accept()
        
    def actualizar_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
            imagen = QPixmap.fromImage(imagen)
            self.label.setPixmap(imagen)
            
        self.frame_count += 1
        
        # Establecer el tiempo de espera en base a los fps del video
        tiempo_espera = 1
        QTimer.singleShot(tiempo_espera, self.actualizar_video)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    ventana = VentanaVideo()
    ventana.setFixedSize(1400,720)
    ventana.show()
    
    sys.exit(app.exec_())

