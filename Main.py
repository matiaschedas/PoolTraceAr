import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer


class VentanaVideo(QMainWindow):
    def __init__(self, video_path):
        super().__init__()
        
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = 0
        
        self.label = QLabel(self)
        self.setCentralWidget(self.label)
        
        self.actualizar_video()
        
    def actualizar_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
            imagen = QPixmap.fromImage(imagen)
            self.label.setPixmap(imagen)
            
        self.frame_count += 1
        
        # Establecer el tiempo de espera en base a los fps del video
        tiempo_espera = int(1000 / self.fps)
        QTimer.singleShot(tiempo_espera, self.actualizar_video)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    video_path = 'video.mp4'  # Reemplaza con la ruta a tu video
    ventana = VentanaVideo(video_path)
    ventana.show()
    
    sys.exit(app.exec_())
