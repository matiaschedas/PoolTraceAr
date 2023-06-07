import sys
import threading
import time
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
import fchola as fc


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

        self.actualizar_video()

    def actualizar_video(self):
        ret, frame = self.cap.read()
        self.frame_count += 1
        roi_x1, roi_y1 = 100, 100
        roi_x2, roi_y2 = 1110, 600
        roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1, 17, param1=100, param2=12, minRadius=5, maxRadius=10)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                mean_val = np.mean(gray[y - r:y + r, x - r:x + r])
                white_pixels = np.sum(gray[y - r:y + r, x - r:x + r] > mean_val)
                circle_area = np.pi * r * r
                white_ratio = white_pixels / circle_area
                cv2.circle(frame, (x + roi_x1, y + roi_y1), r + 10, (0, 255, 0), 2)
                if white_ratio > 0.5:
                    cv2.putText(frame, f"Rayada {white_ratio:.1f}", (x + roi_x1 + 10, y + roi_y1),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                else:
                    cv2.putText(frame, f"Lisa {white_ratio:.1f}", (x + roi_x1 + 10, y + roi_y1),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagen = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
        imagen = QPixmap.fromImage(imagen)
        self.label.setPixmap(imagen)

        # Establecer el tiempo de espera en base a los fps del video
        tiempo_espera = 5
        # int(1000 / self.fps)
        QTimer.singleShot(tiempo_espera, self.actualizar_video)

def contar_segundos():
    fc.obtener_tiempo_transcurrido_formateado()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Crear un hilo para ejecutar la función contar_segundos
    hilo = threading.Thread(target=contar_segundos)
    hilo.start()

    ventana = VentanaVideo()
    ventana.show()

    sys.exit(app.exec_())
