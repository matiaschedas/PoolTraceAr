import sys
import math
from PyQt5 import QtGui
import cv2
import numpy as np
import threading
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton, QCheckBox, QGridLayout, QWidget, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer

from fchola import HiloEjemplo

#bloqueo del hilo1 desde el main
bloqueo = threading.Lock()
hilo1 = HiloEjemplo(bloqueo)

ResolucionX = 1280
ResolucionY= 720


def inicioHilos():
    hilo1.start()

def pararHilos():
    hilo1.detener_hilo()

def parar_de_actualizar(self):
    self.seguirActualizando = False

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
    def __init__(self, ventanaProyeccion):
        super().__init__()
        webcams = obtener_webcams()
        self.setWindowTitle("PoolTraceAR")
        self.seguirActualizando = True
        self.ventanaProyeccion = ventanaProyeccion

        #Parametros del ROI
        self.verVerticesROI = False
        self.verROI = False
        self.XIROI, self.YIROI = 100, 100
        self.XDROI, self.YDROI = 1110, 600
        self.moverVertices = False
        self.verticeSeleccionado = None
        self.inicio = True
        self.creandoROI = False

        #coordenadas de huecos(troneras):
        self.tronera1 = [0, 0]
        self.tronera2 = [0, 0]
        self.tronera3 = [0, 0]
        self.tronera4 = [0, 0]
        self.tronera5 = [0, 0]
        self.tronera6 = [0, 0]
      

        #Parametros de reglas de juego
        self.BolaEnMano = False

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ResolucionX)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ResolucionY)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = 0

        self.label = QLabel(self)
        self.label.setGeometry(0, 0, ResolucionX, ResolucionY)
        #elf.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.label.move(0, 0) 

        # self.setCentralWidget(self.label)
        # self.label.setScaledContents(True)  # Escalar el contenido para ajustarse al QLabel

        # # Establecer la política de expansión
        # self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #creacion de interfaz

      

        self.labelCamara = self.crear_label("Camara:",1290, 5, 50, 30)
        self.comboCamaras = self.crear_combobox(webcams, 1290, 35, 100, 30, 0)
        self.botonROI = self.crear_boton("Configurar ROI", 1290,80,100,30)
        self.botonProyectar = self.crear_boton("Proyectar",1290,125,100,30)

        self.botonProyectar.clicked.connect(self.proyectar)
        self.comboCamaras.currentIndexChanged.connect(self.cambio_camara)
        self.botonROI.clicked.connect(self.crear_ROI)

        self.labelBolaEnMano = self.crear_label("Bola en mano: ",5,820,100,25)
        self.checkBolaEnMano = self.crear_checkbox(80,820,50,30)
        self.checkBolaEnMano.stateChanged.connect(self.bola_en_mano)
        
        self.widget = QWidget()
        self.layout = QGridLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0) 
        #nro fila, nro de col, cant filas, cant columnas
        self.layout.addWidget(self.label, 0, 0, 1, 2)
        self.layout.addWidget(self.labelCamara, 1, 0)
        self.layout.addWidget(self.comboCamaras, 2, 0)
        self.layout.addWidget(self.botonROI, 3, 0)
        self.layout.addWidget(self.botonProyectar, 3, 1)
        self.layout.addWidget(self.labelBolaEnMano, 4, 0)
        self.layout.addWidget(self.checkBolaEnMano, 5, 0)


        self.setCentralWidget(self.widget)
        #inicioHilos()
        self.actualizar_video()


    def cambio_camara(self,index):
        opcion = self.comboCamaras.itemText(index)
        print(f"opcion seleccionada: {opcion}")
        numero = int(re.search(r'\d+', opcion).group())
        self.cap.release()
        self.cap = cv2.VideoCapture(numero, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ResolucionX)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ResolucionY)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

    
    def distancia_media_entre_puntos(self, x1, x2):
        distancia = (x2 - x1)
        return math.floor(distancia/2)

    def proyectar(self):
        self.ventanaProyeccion.show()

    def closeEvent(self, event):
        parar_de_actualizar(self)
        if self.cap is not None:
             self.cap.release()
        pararHilos()
        event.accept()

    def bola_en_mano(self):
        estado_actual = self.checkBolaEnMano.isChecked()
        if estado_actual == True:
            self.BolaEnMano = True
            print("hay bola en mano")
        else:
            self.BolaEnMano = False
            print("No hay bola en mano")
        
    

    def crear_checkbox(self, posX, posY, largo, ancho):
        checkbox = QCheckBox(self)
        checkbox.setGeometry(posX, posY, largo, ancho)
        return checkbox

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
    
    def crear_boton(self, texto, x, y, ancho, alto):
        boton = QPushButton(texto, self)
        boton.setGeometry(x, y, ancho, alto)
        return boton
    
    def mousePressEvent(self, event):
        # Verificar si se hizo clic dentro de los vértices del ROI
        self.verticeSeleccionado = None
        if self.verVerticesROI:
            vertices = [(self.XIROI, self.YIROI), (self.XDROI, self.YDROI)]
            for i, vertice in enumerate(vertices):
                distancia = np.sqrt((event.x() - vertice[0])**2 + (event.y() - vertice[1])**2)
                if distancia <= 10:  # Si la distancia es menor o igual a 10 píxeles, se considera seleccionado
                    self.verticeSeleccionado = i
                    self.moverVertices = True
                    break
        

    def mouseMoveEvent(self, event):
        if self.moverVertices and self.verticeSeleccionado is not None:
            print(f"moviendo vertice: {self.verticeSeleccionado}")
            # Actualizar la posición del vértice seleccionado según la posición del mouse
            if  self.verticeSeleccionado == 0 and event.x() < self.XDROI-10 and event.y() < self.YDROI-10 and event.y() > 1 and event.x() > 1 and event.x() < ResolucionX and event.y() < ResolucionY:
                self.XIROI = event.x()
                self.YIROI = event.y()
            elif self.verticeSeleccionado == 1 and event.x() > self.XIROI+10 and event.y() > self.YIROI+10 and event.x() > 1 and event.y() >1 and event.x() < ResolucionX and event.y() < ResolucionY:
                self.XDROI = event.x()
                self.YDROI = event.y()

    
    def crear_ROI(self):
        if self.creandoROI == False:
            self.creandoROI=True
        elif self.creandoROI ==True:
            self.creandoROI = False
        
        if self.creandoROI:
            self.verROI = True
            self.verVerticesROI = True
        else:
            self.verROI = False
            self.verVerticesROI = False
       
        
    def actualizar_video(self):
        if not self.seguirActualizando:
            return
        
        ret, self.frame = self.cap.read()
        if self.inicio:
                self.XIROI, self.YIROI = 100, 100
                self.XDROI, self.YDROI = 1110, 600
                self.inicio=False

        roi = self.frame[self.YIROI+5:self.YDROI-5, self.XIROI+5:self.XDROI-5]
        if self.verROI:
            cv2.rectangle(self.frame, (self.XIROI, self.YIROI), (self.XDROI, self.YDROI), (0, 255, 0), 2)
            #grafica los huecos (troneras):
            mitadMesa = self.distancia_media_entre_puntos(self.XIROI,self.XDROI)
            troneras = [(self.XIROI-15,self.YIROI-15),(self.XDROI+15,self.YDROI+15),(self.XIROI-15, self.YDROI+15), (self.XDROI+15, self.YIROI-15),(self.XIROI+mitadMesa,self.YIROI-15),(self.XIROI+mitadMesa,self.YDROI+15)]
            self.tronera1 = (self.XIROI-15,self.YIROI-15)
            self.tronera2 = (self.XDROI+15,self.YDROI+15)
            self.tronera3 = (self.XIROI-15, self.YDROI+15)
            self.tronera4 = (self.XDROI+15, self.YIROI-15)
            self.tronera5 = (self.XIROI+mitadMesa,self.YIROI-15)
            self.tronera6 = (self.XIROI+mitadMesa,self.YDROI+15)
            for tronera in troneras:
                cv2.circle(self.frame, tronera, 20 , (255,255,0),2)

        if self.verVerticesROI:
            cv2.circle(self.frame, (self.XIROI, self.YIROI), 10, (0, 255, 0), 2)
            cv2.circle(self.frame, (self.XDROI, self.YDROI), 10, (0, 255, 0), 2)

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1, 15, param1=85, param2=11, minRadius=4, maxRadius=10)
        #limpiar ventana de proyeccion:
        self.ventanaProyeccion.limpiar_circulos()
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                mean_val = np.mean(gray[y - r:y + r, x - r:x + r])
                white_pixels = np.sum(gray[y - r:y + r, x - r:x + r] > mean_val)
                circle_area = np.pi * r * r
                white_ratio = white_pixels / circle_area
                #se dibujan los circulos en la interfaz:
                cv2.circle(self.frame, (x +  self.XIROI, y + self.YIROI), r + 12, (0, 255, 0), 3)
                #se dibujan los mismos circulos en la ventana de proyeccion
                self.ventanaProyeccion.dibujar_circulos(x +  self.XIROI, y + self.YIROI, r + 12, (0, 255, 0), 3)
                # if white_ratio > 0.5:
                #     cv2.putText(frame, f"Rayada {white_ratio:.1f}", (x + roi_x1 + 10, y + roi_y1),
                #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                # else:
                #     cv2.putText(frame, f"Lisa {white_ratio:.1f}", (x + roi_x1 + 10, y + roi_y1),
                #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        imagen = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
        imagen = QPixmap.fromImage(imagen)
        self.label.setPixmap(imagen)

        self.frame_count += 1
        # Establecer el tiempo de espera en base a los fps del video
        tiempo_espera = 13
        QTimer.singleShot(tiempo_espera, self.actualizar_video)


class VentanaVideo2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, ResolucionX, ResolucionY)
        self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.frame = np.zeros((ResolucionY, ResolucionX, 3), dtype=np.uint8)

    def dibujar_circulos(self, x, y, r, color, grosor): 
        self.frame = self.frame.copy()
        cv2.circle(self.frame, (x, y), r, color, grosor)
        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        imagen = QImage(frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
        imagen = QPixmap.fromImage(imagen)
        self.label.setPixmap(imagen)

    def limpiar_circulos(self):
        self.frame = np.zeros((ResolucionY, ResolucionX, 3), dtype=np.uint8)

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    ventana2 = VentanaVideo2()
    ventana2.setFixedSize(ResolucionX,ResolucionY)

    ventana = VentanaVideo(ventana2)
    ventana.setMinimumSize(800, 600)  # Establece el tamaño mínimo deseado
    ventana.setMaximumSize(1920, 1080)
    ventana.show()
    #ventana2.show()
    
    sys.exit(app.exec_())

