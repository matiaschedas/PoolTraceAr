import sys
import math
from PyQt5 import QtGui
import cv2
import numpy as np
import threading
import re
import datetime
import asyncio
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton, QCheckBox, QGridLayout, QWidget, QLineEdit, QVBoxLayout, QSplitter, QFileDialog, QDesktopWidget, QTextBrowser, QProgressBar
from PyQt5.QtGui import QImage, QPixmap, QIcon, QWindow, QScreen, QGuiApplication, QCursor
from PyQt5.QtCore import Qt, QTimer, QEvent
from HiloEtiquetador import ListaApareadaConEtiquetas, variable_compartida_lock
from HiloEtiquetador import Etiquetar
from Clases.ControlWindow import ControlWindow
from Clases.ParametrosSimulacionWindow import ParametrosSimulacionWindow
from Clases.PreprocesamientoWindow import PreprocesamientoWindow
from Clases.AyudaWindow import AyudaWindow
import win32con
import win32gui
import pyautogui
import os
import sys
import json
from screeninfo import get_monitors
from datetime import datetime
import ImageProcessor
from pathlib import Path
import random
import copy
from IA_Simulacion.utils import config
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from Clases.Fisicas import Fisicas
from Clases.IA_Handler import IA_Handler
from IA_Simulacion.SingletonCompartida import SingletonCompartida
from IA_Simulacion.SingletonRespuesta import SingletonRespuesta
from IA_Simulacion.VerMesa import VerMesa

from HiloCalculoTiro import miHilo

screen_width, screen_height = pyautogui.size()

computo = None
anguloRotar = 0
aspectRatio = 2
ResolucionX = 1280
ResolucionY = 720
resoluciones = [(426, 240), (640, 360), (800, 450), (896, 504), (912, 513), (928, 522), (960, 540), (1024, 576), (1152, 648),
                (1200, 675), (1248, 702), (1280, 720), (1440, 810), (1520, 855), (1560, 877), (1584, 891), (1600, 900), (1680, 945), (1920, 1080)]
radios       = [(4, 5), (5, 6), (6, 7), (7, 8),
          (8, 9), (9, 10), (10, 11), (11, 12),(12,13),(13,14),(14,15),(15,16),(16,17),(17,18),(18,19),(19,20),(20,21),(21,22),(22,23)]
radioMin = 4
radioMax = 16
tamPanelBotones = 140
Param1 = 50 
Param2 = 50
cerrarProyeccion = False
proyectando = False
script_dir = os.path.dirname(os.path.abspath(__file__))
display_monitor = 1

circles_prev = None
movimientoDetectado = False
resaltarBola = False
resaltarBolaCorreccion = False

aplicarBlur = True
aplicarHist = False
aplicarContraste = False
mostrarFrameRaw=False
Alpha = 1
Beta = 1
Blur = 1

N_PUNTOS_RASTRO = 50
bolas= []
# bloqueo del hilo1 desde el main
bloqueo = threading.Lock()

setearIDS = False

dp = 1  # El inverso de la resolución de acumulador. Por defecto es 1.
# La distancia mínima entre los centros de los círculos detectados. Por defecto es 25.
minDist = 25
# El umbral para la detección de bordes utilizando el algoritmo de Canny. Por defecto es 10.
cannyThreshold = 10
# El umbral de votos requeridos para la detección de círculos. Por defecto es 10.
votesThreshold = 10
# El radio mínimo de los círculos a detectar. Por defecto es 14.
minRadius = 14
# El radio máximo de los círculos a detectar. Por defecto es 16.
maxRadius = 16
# El número máximo de círculos a detectar. Por defecto es 100.
maxCircles = 100
hough = None
d_frame = None
d_circles = None
alpha = 0.0

distancia_railes = 1
distancia_troneras_esquinas = -2
distancia_troneras_medias = -21
limite_velocidad = 320
friccion_bolas = 0.9
friccion_railes = 0.5
tam_bolas_simulacion = 12
ancho_mesa = 1000
alto_mesa = 500
radio_troneras_IA = 20


def iniciar_GPU():
    global hough,d_frame,d_circles
    hough = cv2.cuda.createHoughCirclesDetector(dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles)
    # Crear el objeto cv2.cuda_GpuMat para el fotograma actual
    d_frame = cv2.cuda_GpuMat()
    # Crear el objeto cv2.cuda_GpuMat para el resultado de la detección
    d_circles = cv2.cuda_GpuMat()

start_time = time.time()
previous_time = start_time
frames = 0
frames_previos = 0


def inicioHilos():
    # hilo1.start()
    #hilo que se encarga de dar la imagen para el proyector
    #hiloProyeccion.start()
    print("se iniciaron los hilos")


def pararHilos():
    hiloProyeccion.detener_hilo()


def parar_de_actualizar(self):
    self.seguirActualizando = False


# Obtener el identificador de la ventana de PyQt5


def get_win_id(window):
    if sys.platform == 'win32':
        return window.winId()
    return None

#devuelve si el frame obtenido de la webcam es todo negro:
def is_frame_black(frame):
    if frame is None:
        return True
    # Convertir el frame a escala de grises
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calcular la suma de intensidades de píxeles
    sum_intensity = np.sum(gray_frame)
  
    # Verificar si la suma de intensidades es igual a cero
    if sum_intensity == 0:
        return True
    else:
        return False
    
# Configurar el estilo de la ventana para mostrar el botón de maximizar de Windows:
def enable_maximize_button(window):
    if sys.platform == 'win32':
        hwnd = get_win_id(window)
        if hwnd:
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            win32gui.SetWindowLong(
                hwnd, win32con.GWL_STYLE, style | win32con.WS_MAXIMIZEBOX)


class VentanaProyeccion(QMainWindow):
    def __init__(self):
        global script_dir, display_monitor
        super().__init__()
        self.setWindowTitle("Proyeccion")
        self.label = QLabel(self)
        global resXProy, resYProy
        self.frame_lock = threading.Lock()
        self.png_image = cv2.imread(script_dir+"\\images\\PoolTraceAr.png", cv2.IMREAD_UNCHANGED)
        
        self.nroMonitor = display_monitor
        self.frame_copy = None

        monitor = QDesktopWidget().screenGeometry(self.nroMonitor)
        self.move(monitor.left(), monitor.top())

        self.label.setGeometry(0, 0, 1920, 1080)
        self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.frame = np.zeros((resYProy, resXProy, 3), dtype=np.uint8)
        self.frame = cv2.resize(self.frame, (resXProy, resYProy), interpolation=cv2.INTER_LINEAR)
        self.resize(1920, 1080)
        # Establecer el icono de la ventana

        icon_path = os.path.join(script_dir, "images/proyector.png")
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)
        self.showFullScreen() 
        global cerrarProyeccion
        cerrarProyeccion=True
        self.close()

    def closeEvent(self, event):
        if(cerrarProyeccion):
            event.accept()
        else:
            event.ignore()

    #mueve la imagen del proyector al monitor de la pc que se elija:
    def set_nroMonitor(self, numero):
        global resXProy,resYProy
        self.nroMonitor = numero
        monitor = QDesktopWidget().screenGeometry(self.nroMonitor)        
        monitor_width = monitor.width()
        monitor_height = monitor.height()
        resXProy = monitor_width
        resYProy = monitor_height
        self.frame = np.zeros((resYProy, resXProy, 3), dtype=np.uint8)
        self.frame = cv2.resize(self.frame, (resXProy, resYProy), interpolation=cv2.INTER_LINEAR)
        self.move(monitor.left() + 7, monitor.top())

    def dibujar_circulos(self, x, y, r, color, grosor, frameDestino):
        with self.frame_lock:
            #cv2.circle(frameDestino, (x, y), r, color, grosor)
            cv2.rectangle(frameDestino, (x - (r + 10), y + (r + 10)), (x + (r + 10), y - (r + 10)), color, grosor)

    def dibujar_ROI(self, puntoA, puntoB, color, grosor, frameDestino):
        with self.frame_lock:
            cv2.rectangle(frameDestino, puntoA,
                          puntoB, color, grosor)

    def dibujar_trayectorias(self, trayectoriaBlanca, trayectorias, xiroi, yiroi, verTodasTrayectorias, frameDestino):
        with self.frame_lock:
            if(trayectoriaBlanca is not None):
                for i in range(len(trayectoriaBlanca)):
                    if(i == len(trayectoriaBlanca) - 1):
                        if isinstance(trayectoriaBlanca[i], tuple):  
                            punto = int(trayectoriaBlanca[i][0]), int(trayectoriaBlanca[i][1])
                        else:
                            punto = trayectoriaBlanca[i].int_tuple
                        x,y = punto
                        x = x + xiroi
                        y = y + yiroi
                        cv2.circle(frameDestino, (x,y), int(minRadius/2) , (0,255,0),thickness=-1)
                        break
                    if isinstance(trayectoriaBlanca[i], tuple):
                        puntoa = int(trayectoriaBlanca[i][0]), int(trayectoriaBlanca[i][1])
                    else:    
                        puntoa = trayectoriaBlanca[i].int_tuple
                    if isinstance(trayectoriaBlanca[i+1], tuple):
                        puntob = int(trayectoriaBlanca[i+1][0]), int(trayectoriaBlanca[i+1][1])
                    else:
                        puntob = trayectoriaBlanca[i+1].int_tuple
                    xa,ya = puntoa
                    xb,yb = puntob
                    xa = xa + xiroi
                    ya = ya + yiroi
                    xb = xb + xiroi
                    yb = yb + yiroi
                    if i == 0:
                        cv2.line(frameDestino,(xa,ya) , (xb,yb), (255,0,0), 2)
                    else:
                        cv2.line(frameDestino,(xa,ya) , (xb,yb), (0,255,0), 2)
            if(verTodasTrayectorias):
                if(trayectorias is not None):
                    for i in range(len(trayectorias)):
                        listaBola = trayectorias[i] 
                        if(len(listaBola)>0):
                            for x in range(len(listaBola)):
                                if(x == len(listaBola)-1):
                                    if isinstance(listaBola[x], tuple):
                                        punto = int(listaBola[x][0]), int(listaBola[x][1])
                                    else:
                                        punto = listaBola[x].int_tuple
                                    x,y = punto
                                    x = x + xiroi
                                    y = y + yiroi
                                    cv2.circle(frameDestino, (x,y), int(minRadius/2) , (0,0,255),thickness=-1)
                                    break
                                if isinstance(listaBola[x], tuple):
                                    puntoa = int(listaBola[x][0]), int(listaBola[x][1])
                                else:
                                    puntoa = listaBola[x].int_tuple
                                if isinstance(listaBola[x+1], tuple):
                                    puntob = int(listaBola[x+1][0]), int(listaBola[x+1][1])
                                else:
                                    puntob = listaBola[x+1].int_tuple
                                xa,ya = puntoa
                                xb,yb = puntob
                                xa = xa + xiroi
                                ya = ya + yiroi
                                xb = xb + xiroi
                                yb = yb + yiroi
                                cv2.line(frameDestino, (xa,ya),(xb,yb), (0,0,255), 2)
        
        
    def resize_frame(self):
        """
        Reescala un frame de imagen a una relación de aspecto específica.

        Args:
            frame: El frame de imagen que deseas reescalar (de tipo numpy.ndarray).
            new_aspect_ratio: La relación de aspecto deseada como una tupla (ancho, alto).

        Returns:
            El frame de imagen reescalado.
        """
        new_aspect_ratio = (2,1)
        height, width, _ = self.frame.shape  # Obtiene las dimensiones originales del frame
        new_width, new_height = new_aspect_ratio

        # Aplica la escala manteniendo la relación de aspecto
        if width / height > new_width / new_height:
            # La imagen es más ancha, ajustamos la altura
            scaled_height = int(new_width / width * height)
            frame_resized = cv2.resize(self.frame, (new_width, scaled_height))
            y_offset = (scaled_height - new_height) // 2
            frame_cropped = frame_resized[y_offset:y_offset + new_height, :, :]
        else:
            # La imagen es más alta, ajustamos el ancho
            scaled_width = int(new_height / height * width)
            frame_resized = cv2.resize(self.frame, (scaled_width, new_height))
            x_offset = (scaled_width - new_width) // 2
            frame_cropped = frame_resized[:, x_offset:x_offset + new_width, :]

        return frame_cropped
    
    def agregarImagen(self):
        # Crea un marco transparente para trabajar con él
        self.frame_copy = np.zeros((resYProy, resXProy, 3), dtype=np.uint8)

        # Achicar la imagen a las dimensiones deseadas
        desired_width = 800
        desired_height = 800
        resized_image = cv2.resize(self.png_image, (desired_width, desired_height), interpolation=cv2.INTER_LINEAR)

        # Calcula las coordenadas para centrar la imagen en el frame transparente
        img_height, img_width, _ = resized_image.shape
        x_start = (resYProy - img_width) // 2
        y_start = (resXProy - img_height) // 2

        # Copia la imagen achicada y transparente en frame_copy respetando la transparencia
        self.frame_copy[y_start:y_start+img_height, x_start:x_start+img_width, :] = resized_image

        # Convierte frame_copy en un QPixmap y muestra en self.label
        frame_rgb = cv2.cvtColor(self.frame_copy, cv2.COLOR_BGRA2RGBA)
        imagen = QImage(frame_rgb.data, resYProy, resXProy, QImage.Format_RGBA8888)
        imagen = QPixmap.fromImage(imagen)
        self.label.setPixmap(imagen)
        

    def dibujar(self):
        global resXProy,resYProy
        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        imagen = QImage(frame_rgb.data, resXProy,resYProy, QImage.Format_RGB888)
        imagen = QPixmap.fromImage(imagen)
        self.label.setPixmap(imagen)

    #limpia el frame para que no queden rastros de los circulos:
    def limpiar_circulos(self):
        with self.frame_lock:
            self.frame = np.zeros((resYProy, resXProy, 3), dtype=np.uint8)
            color_fondo = (255, 255, 255)
            self.frame[:] = color_fondo


class HiloProyeccion(threading.Thread):
    def __init__(self, bloqueo, ventanaProyeccion: VentanaProyeccion):
        super().__init__()
        # Inicializa un bloqueo
        self.bloqueo = bloqueo
        self.detener = False
        self.ventanaProyeccion = ventanaProyeccion
        self.circles = None
        self.height = None
        self.width = None
        self.trayectoriaBlanca = None
        self.trayectorias = None
        self.verTodasTrayectorias = True
        self.xiroi = 0  # Agrega estas líneas para evitar errores
        self.yiroi = 0
        self.xdroi = 0
        self.ydroi = 0
    
    def noHilo(self):
        try:
            # limpiar ventana de proyeccion:
            self.ventanaProyeccion.limpiar_circulos()

            if self.circles is not None and self.height is not None and self.width is not None:
                #Creamos un frame del tamaño del frame del video mostrado en ventanaVideo
                self.frameAntesDeReescalar = np.zeros((self.height, self.width, 3), dtype=np.uint8)        

                global minRadius, maxRadius
                radioProm = int((minRadius+maxRadius)/2)                
                for (x, y, r) in self.circles:
                    # se dibujan los circulos en la interfaz: 
                    self.ventanaProyeccion.dibujar_circulos(self.xiroi + x , self.yiroi + y , radioProm, (0, 255, 0), 2,self.frameAntesDeReescalar)
                    self.ventanaProyeccion.dibujar_ROI((self.xiroi, self.yiroi),(self.xdroi, self.ydroi),(0, 255, 0),5,self.frameAntesDeReescalar)
                self.ventanaProyeccion.dibujar_trayectorias(self.trayectoriaBlanca, self.trayectorias, self.xiroi, self.yiroi, self.verTodasTrayectorias,self.frameAntesDeReescalar)
                

                self.roi = self.frameAntesDeReescalar[self.yiroi:self.ydroi, self.xiroi:self.xdroi]
                global aspectRatio
                altoDestino = int(resXProy / aspectRatio)
                medidaFranja = int((resYProy - altoDestino)/2)
                self.roi = cv2.resize(self.roi, (resXProy, altoDestino), interpolation=cv2.INTER_LINEAR)
                # Superpone el pedazo de frame en el frame principal en las coordenadas especificadas
                self.ventanaProyeccion.frame[medidaFranja:altoDestino+medidaFranja, 0:resXProy] = self.roi
            self.ventanaProyeccion.dibujar()

        except Exception as e:
            print("Error en hilo de proyeccion: ", str(e))

    def run(self):
        while not self.detener:
            try:
                time.sleep(0.0167)
                # limpiar ventana de proyeccion:
                self.ventanaProyeccion.limpiar_circulos()
                if self.circles is not None and self.height is not None and self.width is not None:
                    #Creamos un frame del tamaño del frame del video mostrado en ventanaVideo
                    self.frameAntesDeReescalar = np.zeros((self.height, self.width, 3), dtype=np.uint8)        

                    global minRadius, maxRadius
                    radioProm = int((minRadius+maxRadius)/2)                
                    for (x, y, r) in self.circles:
                        # se dibujan los circulos en la interfaz: 
                        self.ventanaProyeccion.dibujar_circulos(self.xiroi + x , self.yiroi + y , radioProm, (0, 255, 0), 2,self.frameAntesDeReescalar)
                        self.ventanaProyeccion.dibujar_ROI((self.xiroi, self.yiroi),(self.xdroi, self.ydroi),(0, 255, 0),5,self.frameAntesDeReescalar)
                    self.ventanaProyeccion.dibujar_trayectorias(self.trayectoriaBlanca, self.trayectorias, self.xiroi, self.yiroi, self.verTodasTrayectorias,self.frameAntesDeReescalar)
                    

                    self.roi = self.frameAntesDeReescalar[self.yiroi:self.ydroi, self.xiroi:self.xdroi]
                    global aspectRatio
                    altoDestino = int(resXProy / aspectRatio)
                    medidaFranja = int((resYProy - altoDestino)/2)
                    self.roi = cv2.resize(self.roi, (resXProy, altoDestino), interpolation=cv2.INTER_LINEAR)
                    # Superpone el pedazo de frame en el frame principal en las coordenadas especificadas
                    self.ventanaProyeccion.frame[medidaFranja:altoDestino+medidaFranja, 0:resXProy] = self.roi
                self.ventanaProyeccion.dibujar()

                if self.detener:
                    break
            except Exception as e:
                print("Error en hilo de proyeccion: ", str(e))

    def actualizar_circles(self, circles):
        self.circles = circles

    def actualizar_trayectorias(self, trayectoriaBlanca, trayectorias):
        self.trayectoriaBlanca = trayectoriaBlanca
        self.trayectorias = trayectorias

    def actualizar_proporcion_interfaz(self, height, width):
        self.height = height
        self.width = width

    def actualizar_roi(self, xiroi, yiroi, xdroi, ydroi):
        self.xiroi = xiroi
        self.yiroi = yiroi
        self.xdroi = xdroi
        self.ydroi = ydroi

    def ver_todas_trayectorias(self, verTodasTrayectorias):
        self.verTodasTrayectorias = verTodasTrayectorias

    def detener_hilo(self):
        with self.bloqueo:
            self.detener = True

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton

class VentanaContrasena(QWidget):
    def __init__(self,ventanaControl):
        super().__init__()
        self.ventanaControl = ventanaControl
        self.init_ui()
        

    def init_ui(self):
        self.setWindowTitle('Ventana Principal')

        layout = QVBoxLayout()

        self.label_contraseña = QLabel('Contraseña:')
        self.edit_contraseña = QLineEdit()
        self.edit_contraseña.setEchoMode(QLineEdit.Password)

        self.btn_ingresar = QPushButton('Ingresar')
        self.btn_ingresar.clicked.connect(self.verificar_contrasena)

        layout.addWidget(self.label_contraseña)
        layout.addWidget(self.edit_contraseña)
        layout.addWidget(self.btn_ingresar)

        self.setLayout(layout)
        

    def verificar_contrasena(self):
        contraseña_correcta = "miContraseña"  # Reemplaza con tu contraseña

        if self.edit_contraseña.text() == contraseña_correcta:            
            self.ventanaControl.show()
            self.close()
        else:
            print("Contraseña incorrecta")


class VentanaVideo(QMainWindow):
    def __init__(self, ventanaProyeccion: VentanaProyeccion, ventanaParametros: ControlWindow, hiloProyeccion: HiloProyeccion, ventanaPreprocesamiento: PreprocesamientoWindow, ventanaParametrosSimulacion: ParametrosSimulacionWindow, ventanaContrasena: VentanaContrasena, ventanaAyuda: AyudaWindow):
        super().__init__()
        global script_dir
        self.ventanaContrasena = ventanaContrasena 
        self.ventanaAyuda = ventanaAyuda
        self.circlesCopy = None
        self.roi = None
        self.hiloEtiquetador = None
        self.hiloIA = None
        self.etiquetar = False
        self.etiquetando = False
        self.calculandoTiro = False
        self.hiloProyeccion = hiloProyeccion
        self.circles = None
        self.puntos_trayectoria_bola_blanca = None
        self.puntos_trayectorias_bolas = None
        self.puntos_trayectoria_bola_seleccionada = None
        
        self.velocidadRequerida = -0.1
        self.attrs = None
        self.best_player = None
        self.simulacionIA = False
        self.tiro_seleccionado = 0
        self.singletonRespuestaIA_1 = None
        self.singletonRespuestaIA_2 = None
        self.respuesta_hiloTiro = None
        self.repitiendo_simulacion = False
        self.bolaSeleccionada = None
        self.contadorProgressBar = 0
        self.valorMaxProgressBar = 0
        self.valorProgressBar = 0
        self.bolaSeleccionadaCorreccion = None
        self.moviendo_bola_correccion = False
        
        self.setMaximumSize(screen_width, screen_height)
        self.resize(ResolucionX, ResolucionY)
        self.setWindowTitle("PoolTraceAR")
        self.ventanaPrepro = ventanaPreprocesamiento
        self.ventanaParametrosSimulacion = ventanaParametrosSimulacion
        self.boton_ver_mesa = self.ventanaParametrosSimulacion.obtenerBotonVerMesa()
        self.boton_ver_mesa.clicked.connect(self.verMesa)
        self.controlWindow = ventanaParametros
        self.controlWindow.dpChanged.connect(self.onDpChanged)
        self.controlWindow.minDistChanged.connect(self.onMinDistChanged)
        self.controlWindow.cannyThresholdChanged.connect(
            self.onCannyThresholdChanged)
        self.controlWindow.votesThresholdChanged.connect(
            self.onVotesThresholdChanged)
        self.controlWindow.minRadiusChanged.connect(self.onMinRadiusChanged)
        self.controlWindow.maxRadiusChanged.connect(self.onMaxRadiusChanged)
        self.controlWindow.maxCirclesChanged.connect(self.onMaxCirclesChanged)
        self.controlWindow.anguloChanged.connect(self.onAnguloChanged)
        self.controlWindow.aspectRatioChanged.connect(self.onAspectRatioChanged)
        self.controlWindow.radioTroneraChanged.connect(self.onRadioTroneraChanged)

        icon_path = os.path.join(script_dir, "images/bola8.png")
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)

        self.init_ui()
        self.circlesProyeccion = None
        self.rastros = []
        self.seguirActualizando = True
        self.ventanaProyeccion = ventanaProyeccion
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        # region Parametros del ROI
        self.verVerticesROI = False
        self.verROI = False
        self.XIROI, self.YIROI = 100, 100
        self.XDROI, self.YDROI = 150, 150
        self.hiloProyeccion.actualizar_roi(xiroi=self.XIROI, yiroi=self.YIROI, xdroi=self.XDROI, ydroi=self.YDROI)
        self.moverVertices = False
        self.verticeSeleccionado = None
        self.inicio = True
        self.creandoROI = False
        self.cargarCoordenadas = True
      
        # endregion

        # region coordenadas de huecos(troneras):
        self.troneras =[(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)]
        self.troneras_labels = ["T1", "T2", "T3", "T4", "T5", "T6"]
        self.troneras_labels_usuario = ["T1", "T6", "T4", "T3", "T2", "T5"]
        self.puntos_paredes = [(0,0),(5,0),(10,0),(15,0),(0,5),(20,5),(0,10),(20,10),(0,15),(5,15),(10,15),(15,15)]
        self.puntos_paredes_labels =["1","2","3","4","5","6","7","8","9","10","11","12"]
        self.radioTronera = int(radioMax)+3
        self.selected_tronera = None
        self.selected_punto = None
        # endregion

        # region Parametros de reglas de juego
        self.BolaEnMano = False
        self.Hay2Tiros = False
        self.VerTodasTrayectorias = True
        self.hayMesaAbierta = False
        self.hayMovimiento = False
        self.bolaBlanca = None
        self.corregirFrame = False

        self.tiroFinal = False
        self.troneraTiroFinal=-1
        # endregion

        # region Configuraciones opencv
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ResolucionX)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ResolucionY)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = 0
        # endregion

        # region Configuracion de la ventana
        self.setMinimumSize(800, 600)  # Establece el tamaño mínimo deseado
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, ResolucionX, ResolucionY-tamPanelBotones)
        # elf.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.label.move(0, 0)
        self.tiempo_inicio = time.time()

        # self.setCentralWidget(self.label)
        # self.label.setScaledContents(True)  # Escalar el contenido para ajustarse al QLabel

        # # Establecer la política de expansión
        # self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # endregion

        self.botonProyectar, self.botonROI, self.botonPreprocesamientos, self.botonGuardarPreset, self.botonCargarPreset, self.botonParametrosSimulacion = ventanaParametros.obtenerBotones()
        self.comboCamaras = ventanaParametros.obtenerComboCamaras()
        self.comboMonitores = ventanaParametros.obtenerComboMonitores()
        #self.labelCamara = self.crear_label("Camara:", 1290, 5, 50, 30)
        #self.comboCamaras = self.crear_combobox(webcams, 1290, 35, 100, 30, 0)

        self.botonConfiguracion = self.crear_boton("Configuracion", 1290, 125, 100, 30)
        self.botonAyuda = self.crear_boton("Ayuda", 1290,125,100,30)
        self.fpsText = QLineEdit(self)
        self.fpsText.setReadOnly(True)
        self.labelFps = self.crear_label("FPS: ", 5, 820, 100, 25)
        self.labelFps.setAlignment(Qt.AlignCenter)

        self.botonConfiguracion.clicked.connect(self.configurar)
        self.botonAyuda.clicked.connect(self.ayuda)
        self.botonProyectar.clicked.connect(self.proyectar)
        self.comboCamaras.currentIndexChanged.connect(self.cambio_camara)
        self.comboMonitores.currentIndexChanged.connect(self.cambio_monitor)
        self.botonROI.clicked.connect(self.crear_ROI)
        self.botonPreprocesamientos.clicked.connect(self.abrir_preprocesamiento)
        self.botonParametrosSimulacion.clicked.connect(self.abrir_parametros_simulacion)
        self.labelBolaEnMano = self.crear_label("Bola en mano: ", 5, 820, 100, 25)
        self.label2Tiros = self.crear_label("2 Tiros: ", 5,820,100,25)
        self.labelMesaAbierta = self.crear_label("Mesa abierta: ", 5, 820, 100, 25)
        self.labelTrayectorias = self.crear_label("Ver Todas las Trayectorias: ",5,820,100,5)
        self.checkBolaEnMano = self.crear_checkbox(80, 820, 50, 30)
        self.checkBolaEnMano.stateChanged.connect(self.bola_en_mano)
        self.check2Tiros = self.crear_checkbox(80,820,50,30)
        self.check2Tiros.stateChanged.connect(self.dos_tiros)
        self.checkTrayectorias=self.crear_checkbox(80,820,50,30)
        self.checkTrayectorias.setChecked(True)
        self.checkTrayectorias.stateChanged.connect(self.ver_todas_trayectorias)
        self.checkMesaAbierta = self.crear_checkbox(80,820,50,30)
        self.checkMesaAbierta.stateChanged.connect(self.mesa_abierta)
        

        self.botonVerSimulacion = self.crear_boton("Ver Simulacion", 1290, 125, 100, 30)
        self.botonVerSimulacion.setEnabled = False
        
        self.botonCalcularTiroConfirmar = self.crear_boton("Calcular tiro", 1290, 125, 100, 30)        
        self.botonCalcularTiroConfirmar.clicked.connect(self.botonCalcularTiroConfirmarPressed)
        self.botonCalcularTiroConfirmar.setDisabled(True)

        self.botonCancelar = self.crear_boton("Cancelar", 1290, 125, 100, 30)
        self.botonCancelar.setDisabled(True)
        self.botonCancelar.clicked.connect(self.botonCancelarPressed)

        self.botonVerSimulacion.clicked.connect(self.ver_simulacion)
        self.labelTiroFinal = self.crear_label("Tiro Final: ", 5, 820, 100, 25)
        self.checkTiroFinal = self.crear_checkbox(80, 820, 50, 30)
        self.checkTiroFinal.stateChanged.connect(self.tiro_final)
        self.comboTroneraTiroFinal=self.crear_combobox(self.troneras_labels,80,820,40,30,0)
        self.comboTroneraTiroFinal.currentIndexChanged.connect(self.cambio_tronera_tiro_final)
        self.comboTroneraTiroFinal.adjustSize()
        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setAcceptRichText(True)        
        self.progressBar = QProgressBar(self)
        self.progressBar.setValue(0)

        self.botonGuardarPreset.clicked.connect(self.guardar_preset)
        self.botonCargarPreset.clicked.connect(self.cargar_preset)
        # Crear el widget principal y asignarle un layout vertical
        widgetPrincipal = QWidget()
        layoutPrincipal = QVBoxLayout()
        widgetPrincipal.setLayout(layoutPrincipal)
        layoutPrincipal.setContentsMargins(0, 0, 0, 0)

        # Crear el widget1 y asignarle el layout1 como QGridLayout
        self.widget1 = QWidget()
        self.layout1 = QGridLayout(self.widget1)
        self.layout1.setContentsMargins(0, 0, 0, 0)
        self.layout1.setSpacing(5)  # Opcional: eliminar el espacio entre los widgets

        # Crear el widget2 y asignarle el layout2
        self.widget2 = QWidget()
        self.layout2 = QGridLayout(self.widget2)
        self.layout2.setContentsMargins(5, 0, 5, 5)
        self.widget2.setFixedHeight(tamPanelBotones)
        self.fpsText.setMaximumWidth(50)
        self.botonConfiguracion.setMaximumWidth(100)  # Ancho fijo
        self.botonAyuda.setMaximumWidth(100)
        self.layout2.setSpacing(0)

        # Agregar los widgets al layout principal
        layoutPrincipal.addWidget(self.widget1)
        layoutPrincipal.addWidget(self.widget2)

        # Agregar los widgets al layout1 y layout2 con sus respectivas posiciones
        self.layout1.addWidget(self.label, 0, 0, 1, 1, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.layout2.addWidget(self.botonConfiguracion, 0, 0)
        self.layout2.addWidget(self.botonAyuda,0 ,1)
        self.layout2.addWidget(self.labelBolaEnMano, 2, 0)
        self.layout2.addWidget(self.label2Tiros,2,1)
        self.layout2.addWidget(self.labelMesaAbierta, 2 ,2)
        self.layout2.addWidget(self.labelTrayectorias, 2,3)
        self.layout2.addWidget(self.checkBolaEnMano, 3, 0)
        self.layout2.addWidget(self.check2Tiros,3,1)
        self.layout2.addWidget(self.checkMesaAbierta, 3, 2)
        self.layout2.addWidget(self.checkTrayectorias,3,3)
        self.layout2.addWidget(self.labelTiroFinal, 2, 4)
        self.layout2.addWidget(self.checkTiroFinal, 3, 4)
        self.layout2.addWidget(self.comboTroneraTiroFinal, 3, 5)
        self.layout2.addWidget(self.progressBar, 4, 0, 1, 5)
        self.layout2.addWidget(self.botonVerSimulacion, 4, 5, 1, 2)
        self.layout2.addWidget(self.botonCalcularTiroConfirmar, 5, 5, 1, 1)
        self.layout2.addWidget(self.botonCancelar, 5, 6, 1, 1)
        
        self.layout2.addWidget(self.textBrowser, 5, 0, 2, 5)

        self.comboTroneraTiroFinal.hide()

        # Agregar el contador de FPS con alineación a la esquina inferior derecha
        self.layout2.addWidget(self.labelFps, 2, 6)
        self.layout2.addWidget(self.fpsText, 3, 6)

        self.setCentralWidget(widgetPrincipal)
        
        #componenetes de la ventana de preprocesamiento
        self.ventanaPrepro.view_frame_button.clicked.connect(self.ver_frame)
        self.ventanaPrepro.alphaChanged.connect(self.onAlphaChanged)
        self.ventanaPrepro.betaChanged.connect(self.onBetaChanged)
        self.ventanaPrepro.blurChanged.connect(self.onBlurChanged)

        self.ventanaParametrosSimulacion.distRailesChanged.connect(self.setDistRailes)
        self.ventanaParametrosSimulacion.distTronerasEsquinasChanged.connect(self.setDistTronerasEsquinas)
        self.ventanaParametrosSimulacion.distTronerasMediasChanged.connect(self.setDistTronerasMedias)
        self.ventanaParametrosSimulacion.limiteVelocidadChanged.connect(self.setLimiteVelocidad)
        self.ventanaParametrosSimulacion.friccionRailesChanged.connect(self.setFriccionRailes)
        self.ventanaParametrosSimulacion.friccionBolasChanged.connect(self.setFriccionBolas)
        self.ventanaParametrosSimulacion.anchoMesaChanged.connect(self.setAnchoMesa)
        self.ventanaParametrosSimulacion.altoMesaChanged.connect(self.setAltoMesa)
        self.ventanaParametrosSimulacion.tambBolasChanged.connect(self.setTamBolasSimulacion)
        self.ventanaParametrosSimulacion.radioTronerasChanged.connect(self.setRadioTronerasIA)

        self.ventanaPrepro.blurChecked.connect(self.aplicarBlur)
        self.ventanaPrepro.contrastChecked.connect(self.aplicarContraste)
        self.ventanaPrepro.histChecked.connect(self.aplicarHist)

        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.on_resize_timeout)
        self.poligonos = None
        self.poligonosImposibles = None
        self.tronerasPosibles = None
        self.roiRAW = None
        self.frame = None
        self.current_camera_index = 0
        self.fisicas = None
        self.algunaEstaSeleccionada = False
        self.velXBlanca = None
        self.velYBlanca = None
        self.listaEtiquetada = None
        self.ultimaListaEtiquetada = None
        self.repetirSimulacion = False
        self.embocarNegra = False
        self.cursor_position = (0,0)

        self.timer_clic_largo = QTimer()
        self.timer_clic_largo.setSingleShot(True)
        self.timer_clic_largo.timeout.connect(self.clic_largo)
        self.tiempo_minimo_clic_largo = 2000  # 2 segundos

        inicioHilos()
        self.initCameras()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            print("La tecla Supr fue presionada")
        elif event.key() == Qt.Key_Plus:
            print("La tecla + fue presionada")
        elif event.key() == Qt.Key_Q:
            if(self.corregirFrame):
                print("La tecla 'q' fue presionada")

    def borrandoSeleccionada(self):
        if self.bolaSeleccionada is None:
            return False
        xs,ys,rs = self.bolaSeleccionada
        xs = xs - self.XIROI
        ys = ys - self.YIROI
        xsc, ysc, rsc = self.bolaSeleccionadaCorreccion
        dist = math.sqrt((xs - xsc)**2 + (ys - ysc)**2)
        if (dist <= rs):
            return True
        return False

    def verMesa(self):
        objetoVerMesa = VerMesa(distancia_railes, distancia_troneras_medias, distancia_troneras_esquinas,limite_velocidad, friccion_bolas, friccion_railes,ancho_mesa,tam_bolas_simulacion, alto_mesa, radio_troneras_IA)
        self.hiloCalculoTiro = miHilo(distancia_railes, distancia_troneras_medias, distancia_troneras_esquinas,limite_velocidad, friccion_bolas, friccion_railes,ancho_mesa,tam_bolas_simulacion, alto_mesa, radio_troneras_IA)
        self.hiloCalculoTiro.VerMesa(objetoVerMesa)
        objetoVerMesa = None
        # self.hiloCalculoTiro.join(timeout=0.01)
        # if  self.hiloCalculoTiro.is_alive():
        #     print("Simulando tiro...")
    def botonCalcularTiroConfirmarPressed(self):
            if(self.botonCalcularTiroConfirmar.text()=="Confirmar"):
                global resaltarBolaCorreccion
                self.circles = self.eliminar_circulos_repetidos(self.circles)
                self.etiquetar = True
                self.botonCalcularTiroConfirmar.setText("Calcular tiro")
                self.botonCalcularTiroConfirmar.setDisabled(True)
                self.bolaSeleccionadaCorreccion= None
                resaltarBolaCorreccion = False
            else:
                self.corregirFrame = True
                self.botonCalcularTiroConfirmar.setText("Confirmar")
                self.botonCancelar.setDisabled(False)
                if(self.circles is not None):
                    self.circlesCopy = self.circles.copy()
                (xs,ys,rs) = self.bolaSeleccionada
                indice = self.encontrar_indice_por_coordenadas(xs-self.XIROI,ys-self.YIROI)
                if (indice == -1):
                    self.circlesCopy.append((xs-self.XIROI,ys-self.YIROI,rs))
                else:
                    self.circlesCopy[indice] = (xs-self.XIROI,ys-self.YIROI,radioMax)

    def botonCancelarPressed(self):
        global resaltarBolaCorreccion
        self.corregirFrame = False
        self.botonCalcularTiroConfirmar.setText("Calcular tiro")
        self.botonCancelar.setDisabled(True)
        self.botonCalcularTiroConfirmar.setDisabled(False)
        self.bolaSeleccionadaCorreccion= None
        resaltarBolaCorreccion = False

    def tiro_final(self):
        estado_actual = self.checkTiroFinal.isChecked()
        if estado_actual == True:
            self.tiroFinal=True
            self.comboTroneraTiroFinal.show()
            self.troneraTiroFinal=self.comboTroneraTiroFinal.currentIndex()+1
            print("Hay Tiro Final")
        else:
            self.tiroFinal = False
            self.comboTroneraTiroFinal.hide()
            self.troneraTiroFinal=-1
            print("No Hay Tiro Final")

    def cambio_tronera_tiro_final(self):
        self.troneraTiroFinal=self.comboTroneraTiroFinal.currentIndex()+1
        print("Tronera seleccionada para tiro final: "+str(self.troneraTiroFinal))
        self.printUI("Tronera seleccionada para tiro final: "+str(self.troneraTiroFinal))
    
    def initCameras(self):
        self.cambio_camara(self.current_camera_index)  # Llamar al método para mostrar la primera cámara

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_video)
        self.timer.start(16)  # 30 ms (30 FPS)



    #comprueba si el nombre con el que el usuario intenta guardar un preset es valido:
    def es_nombre_archivo_valido(self, texto):
        patron = r"^(?!^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$)[^\x00-\x1f\\?*:\";|/<>]+$"
        coincide = re.match(patron, texto, re.IGNORECASE)
        return coincide is not None
    
    #guardar presets de configuraciones:
    def guardar_preset(self):
        global dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles, anguloRotar, distancia_railes, distancia_troneras_esquinas, distancia_troneras_medias, limite_velocidad, friccion_bolas, friccion_railes, tam_bolas_simulacion, ancho_mesa, alto_mesa, radio_troneras_IA
        nombreArchivo = self.controlWindow.textNombrePreset.text()
        valido = self.es_nombre_archivo_valido(nombreArchivo)
        if valido:
            nombreArchivo = nombreArchivo + ".json"
            carpeta = Path(script_dir + '/presets/')
            if not carpeta.exists():
            # Creamos la carpeta
                carpeta.mkdir(parents=True, exist_ok=True)
            path = script_dir + "\\presets\\" + nombreArchivo
            datos = {
                "dp": dp,
                "minDist": minDist,
                "cannyThreshold": cannyThreshold,
                "votesThreshold": votesThreshold,
                "minRadius": minRadius,
                "maxRadius": maxRadius,
                "maxCircles": maxCircles,
                "coordPunto1": self.puntos_paredes[0],
                "coordPunto2": self.puntos_paredes[1],
                "coordPunto3": self.puntos_paredes[2],
                "coordPunto4": self.puntos_paredes[3],
                "coordPunto5": self.puntos_paredes[4],
                "coordPunto6": self.puntos_paredes[5],
                "coordPunto7": self.puntos_paredes[6],
                "coordPunto8": self.puntos_paredes[7],
                "coordPunto9": self.puntos_paredes[8],
                "coordPunto10": self.puntos_paredes[9],
                "coordPunto11": self.puntos_paredes[10],
                "coordPunto12": self.puntos_paredes[11],
                "XIROI":self.XIROI,
                "YIROI":self.YIROI,
                "XDROI":self.XDROI,
                "YDROI":self.YDROI,
                "tronera1":self.troneras[0],
                "tronera2":self.troneras[1],
                "tronera3":self.troneras[2],
                "tronera4":self.troneras[3],
                "tronera5":self.troneras[4],
                "tronera6":self.troneras[5],
                "angulo": anguloRotar,
                "radioTroneras": self.radioTronera,
                "distanciaRailes": distancia_railes,
                "distanciaTronerasEsquinas": distancia_troneras_esquinas,
                "distanciaTronerasMedias": distancia_troneras_medias,
                "limiteVelocidad": limite_velocidad,
                "friccionBolas": friccion_bolas,
                "friccionRailes": friccion_railes,
                "tamBolasSimulacion": tam_bolas_simulacion,
                "anchoAltoMesa": ancho_mesa,
                "altoMesa": alto_mesa,
                "radioTronerasIA": radio_troneras_IA
            }
            with open(path, "w") as archivo:
                json.dump(datos, archivo)

    #cargar presets de configuraciones:
    def cargar_preset(self, path=None):
        global dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles, anguloRotar, distancia_railes, distancia_troneras_esquinas, distancia_troneras_medias,limite_velocidad,friccion_bolas,friccion_railes,tam_bolas_simulacion,ancho_mesa,alto_mesa, radio_troneras_IA
        campos = ['dp','minDist','cannyThreshold','votesThreshold','minRadius','maxRadius','maxCircles', 
                  'coordPunto1', 'coordPunto2','coordPunto3','coordPunto4','coordPunto5','coordPunto6',
                  'coordPunto7','coordPunto8','coordPunto9','coordPunto10','coordPunto11','coordPunto12',
                  'XIROI','YIROI','XDROI','YDROI','tronera1','tronera2','tronera3','tronera4','tronera5','tronera6',
                  'angulo','radioTroneras', 'distanciaRailes','distanciaTronerasEsquinas','distanciaTronerasMedias',
                   'limiteVelocidad','friccionBolas','friccionRailes','tamBolasSimulacion','anchoAltoMesa', 'altoMesa', 'radioTronerasIA']
        
        valido = False
        if path is False:
            file_dialog = QFileDialog()

            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog

            file_path, _ = file_dialog.getOpenFileName(None, "Seleccionar archivo", "", "Todos los archivos (*.*)", options=options)
        else:
            file_path = path
 
        if file_path:
            print("Archivo seleccionado:", file_path)
            _, extension = os.path.splitext(file_path)
            if extension == ".json":
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                    for campo in campos:
                        valido = True
                        if campo not in data:
                            print(f"El campo '{campo}' no está presente en el JSON.")
                            valido = False
                except Exception:
                    print("Error al levantar archivo seleccionado")
                    valido=False
        if valido:
            dp = data["dp"]
            minDist =data["minDist"]
            cannyThreshold =data["cannyThreshold"]
            votesThreshold =data["votesThreshold"]
            minRadius =data["minRadius"]
            maxRadius =data["maxRadius"]
            maxCircles = data["maxCircles"]
            self.puntos_paredes[0] = data["coordPunto1"]
            self.puntos_paredes[1] = data["coordPunto2"]
            self.puntos_paredes[2] = data["coordPunto3"]
            self.puntos_paredes[3] = data["coordPunto4"]
            self.puntos_paredes[4] = data["coordPunto5"]
            self.puntos_paredes[5] = data["coordPunto6"]
            self.puntos_paredes[6] = data["coordPunto7"]
            self.puntos_paredes[7] = data["coordPunto8"]
            self.puntos_paredes[8] = data["coordPunto9"]
            self.puntos_paredes[9] = data["coordPunto10"]
            self.puntos_paredes[10] = data["coordPunto11"]
            self.puntos_paredes[11] = data["coordPunto12"]
            self.XIROI = data["XIROI"]
            self.YIROI = data["YIROI"]
            self.XDROI = data["XDROI"]
            self.YDROI = data["YDROI"]
            self.troneras[0]=data["tronera1"]
            self.troneras[1]=data["tronera2"]
            self.troneras[2]=data["tronera3"]
            self.troneras[3]=data["tronera4"]
            self.troneras[4]=data["tronera5"]
            self.troneras[5]=data["tronera6"]
            anguloRotar = data["angulo"]
            self.radioTronera = data["radioTroneras"]
            distancia_railes = data["distanciaRailes"]
            distancia_troneras_esquinas = data["distanciaTronerasEsquinas"]
            distancia_troneras_medias = data["distanciaTronerasMedias"]
            limite_velocidad = data["limiteVelocidad"]
            friccion_bolas = data["friccionBolas"]
            friccion_railes = data["friccionRailes"]
            tam_bolas_simulacion = data["tamBolasSimulacion"]
            ancho_mesa = data["anchoAltoMesa"]
            alto_mesa = data["altoMesa"]
            radio_troneras_IA = data["radioTronerasIA"]

            self.controlWindow.actualizarParametros(
            dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles, anguloRotar,self.radioTronera)
            self.ventanaParametrosSimulacion.actualizarParametros(distancia_railes, distancia_troneras_esquinas,distancia_troneras_medias,limite_velocidad,friccion_bolas,friccion_railes,tam_bolas_simulacion,ancho_mesa, alto_mesa, radio_troneras_IA)

    def aplicar_preset_default(self, nombreArchivo=""):
        if nombreArchivo == "":
            nombreArchivo = "Default.json"
        carpeta = Path(script_dir + '/presets/')
        if not carpeta.exists():
        # Creamos la carpeta
            carpeta.mkdir(parents=True, exist_ok=True)
        path = script_dir + "\\presets\\" + nombreArchivo
        if (os.path.exists(path)):
            self.cargar_preset(path)
    
    # region cambios para preprocesamiento de imagen:     
    def onAlphaChanged(self, value):
        global Alpha
        Alpha = value
    
    def onBetaChanged(self, value):
        global Beta
        Beta = value

    def onBlurChanged(self, value):
        global Blur
        Blur = value

    def aplicarBlur(self, value):
        global aplicarBlur
        aplicarBlur = value
    
    def aplicarHist(self, value):
        global aplicarHist
        aplicarHist = value

    def aplicarContraste(self, value):
        global aplicarContraste
        aplicarContraste = value
    #endregion

    #region cambios para parametros de simulacion:
    def setDistRailes(self, value):
        global distancia_railes
        distancia_railes= value
    def setDistTronerasEsquinas(self, value):
        global distancia_troneras_esquinas
        distancia_troneras_esquinas= value
    def setDistTronerasMedias(self, value):
        global distancia_troneras_medias
        distancia_troneras_medias= value
    def setLimiteVelocidad(self, value):
        global limite_velocidad
        limite_velocidad= value
    def setRadioTronerasIA(self, value):
        global radio_troneras_IA
        radio_troneras_IA = value
    def setFriccionRailes(self, value):
        global friccion_railes
        friccion_railes= value
    def setFriccionBolas(self, value):
        global friccion_bolas
        friccion_bolas= value
    def setAnchoMesa(self, value):
        global ancho_mesa
        ancho_mesa = value
    def setAltoMesa(self, value):
        global alto_mesa
        alto_mesa = value
    def setTamBolasSimulacion(self, value):
        global tam_bolas_simulacion
        tam_bolas_simulacion = value
    #endregion

    def ver_frame(self):
        global mostrarFrameRaw
        if mostrarFrameRaw  == True:
            mostrarFrameRaw = False
            if cv2.getWindowProperty("Frame", cv2.WND_PROP_VISIBLE) > 0:
                cv2.destroyWindow("Frame")
        else:
            mostrarFrameRaw = True

    #actualiza los parametros con los cuales se detectan las bolas en opencv con cuda:
    def actualizarHough(self):
        global hough, dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles, computo, anguloRotar
        self.controlWindow.actualizarParametros(
            dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles, anguloRotar,self.radioTronera)
        print(f"dp: {dp}, minDist: {minDist}, cannyThreshold: {cannyThreshold}, votesThreshold: {votesThreshold}, minRadius: {minRadius}, maxRadius: {maxRadius}, maxCircles: {maxCircles}")
        try:
            if (computo == "GPU"):
                hough = cv2.cuda.createHoughCirclesDetector(
                    dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles)
        except cv2.error as e:
            pass

    #region cambios en los parametros de deteccion de circulos:
    def onDpChanged(self, newDP):
        global dp
        dp = newDP
        self.actualizarHough()

    def onMinDistChanged(self, minDistNew):
        global minDist
        minDist = minDistNew
        self.actualizarHough()

    def onCannyThresholdChanged(self, cannyThresholdNew):
        global cannyThreshold
        cannyThreshold = cannyThresholdNew
        self.actualizarHough()

    def onVotesThresholdChanged(self, votesThresholdNew):
        global votesThreshold
        votesThreshold = votesThresholdNew
        self.actualizarHough()

    def onMinRadiusChanged(self, minRadiusNew):
        global minRadius
        minRadius = minRadiusNew
        self.actualizarHough()

    def onMaxRadiusChanged(self, maxRadiusNew):
        global maxRadius
        maxRadius = maxRadiusNew
        self.actualizarHough()

    def onMaxCirclesChanged(self, maxCirclesNew):
        global maxCircles
        maxCircles = maxCirclesNew
        self.actualizarHough()
    #endregion

    #cambio del angulo del video: 
    def onAnguloChanged(self, anguloNew):
        global anguloRotar
        anguloRotar = anguloNew

    def onAspectRatioChanged(self, aspectRatioNew):
        global aspectRatio
        aspectRatio = aspectRatioNew

    #cambio del radio de todas las troneras:
    def onRadioTroneraChanged(self, radioTroneraNew):
        global anguloRotar
        self.radioTronera = radioTroneraNew    

    def init_ui(self):
        # Configurar la ventana para mostrar el botón de maximizar de Windows
        enable_maximize_button(self)

    #evento maximizar ventana:
    def event(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMaximized:
                ResolucionX = self.size().width()
                ResolucionY = self.size().height()
                print(f"resMX: {ResolucionX} resMY: {ResolucionY}")
        return super().event(event)

    # Metodo para realizar el ajuste de resolucion en el evento de maximizar/desmaximizar la ventana
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            if event.spontaneous():
                # Código que se ejecuta al inicio del evento de redimensionamiento
                print("Inicio del evento de redimensionamiento")
                if self.cap is not None and self.cap.isOpened():
                    self.cap.release()

        return super().eventFilter(obj, event)

    #evento que se ejecuta cuando el usuario agranda o achica la ventana
    def resizeEvent(self, event):
        super().resizeEvent(event)
        minimum_size = self.minimumSize()
        if event.size().width() < minimum_size.width() or self.size().height() < minimum_size.height():
            # Restaurar el tamaño anterior de la ventana
            self.setFixedSize(minimum_size)

         # Reiniciar el temporizador en cada redimensionamiento
        self.resize_timer.start(500)  # Establecer un tiempo de espera adecuado
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        global ResolucionX, ResolucionY
        ResolucionX = event.size().width()
        ResolucionY = event.size().height()

    #encuentra la resolucion de video para el tamaño de la ventana:
    def encontrar_resolucion(self, resoluciones, ResolucionX, ResolucionY):
        print(f"resX: {ResolucionX} resY: {ResolucionY}")
        ancho, alto = resoluciones[len(resoluciones)-1]
        if(ResolucionX > ancho or ResolucionY > alto):
            return resoluciones[len(resoluciones)-1]
        for i in range(len(resoluciones)):
            ancho, alto = resoluciones[i]
            if ResolucionX > ancho and ResolucionY-tamPanelBotones > alto:
                elegida = resoluciones[i]
            else:
                return elegida
        return None

    #encuentra un radio de los circulos para el tamaño del video:
    def encontrar_radio(self, resolucion_encontrada):
        global resoluciones, radios
        indiceResolucion = resoluciones.index(resolucion_encontrada)
        
        indice_radio = indiceResolucion
        radio = radios[indice_radio]
        return radio

    #metodo que se ejecuta cuando termina el evento de resize de la ventana:
    def on_resize_timeout(self):
        # Código a ejecutar cuando finaliza el evento de redimensionamiento
        print("Final del evento de redimensionamiento")
        global ResolucionX, ResolucionY, resoluciones, radioMax, radioMin, computo
        resolucion_encontrada = self.encontrar_resolucion(
            resoluciones, ResolucionX, ResolucionY)
        ResolucionX = resolucion_encontrada[0]
        ResolucionY = resolucion_encontrada[1]
        if self.frame is not None:
            self.frame = cv2.resize(self.frame, (ResolucionX, ResolucionY), interpolation=cv2.INTER_LINEAR)
            # ventanaProyeccion.frame = cv2.resize(ventanaProyeccion.frame, (resYProy, resXProy), interpolation=cv2.INTER_LINEAR)
        self.XIROI, self.YIROI = 10, 10
        self.XDROI, self.YDROI = 20, 20
        radioElegido = self.encontrar_radio(resolucion_encontrada)
        radioMin = radioElegido[0]
        radioMax = radioElegido[1]
        print(f"radio elegido: {radioMin} - {radioMax}")
        print(f"res seleccionada: {ResolucionX}x{ResolucionY}")

        global minRadius, maxRadius
        if minRadius < maxRadius:
            minRadius = radioMin
            maxRadius = radioMax
        if(computo == "GPU"):
            self.actualizarHough()
        self.cambio_camara(self.comboCamaras.currentIndex())
        self.hiloProyeccion.actualizar_roi(xiroi=self.XIROI, yiroi=self.YIROI, xdroi=self.XDROI, ydroi=self.YDROI)
        
        self.hiloProyeccion.actualizar_proporcion_interfaz(ResolucionY,ResolucionX)
        if self.isMaximized():
            self.aplicar_preset_default(nombreArchivo="DefaultMaximizado.json")
        else:
            self.aplicar_preset_default()
        

    #cambia la webcam a la que selecciono el usuario:
    def cambio_camara(self, index):
        opcion = self.comboCamaras.itemText(index)
        print(f"opcion seleccionada: {opcion}")    
        try:
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
            self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ResolucionX)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ResolucionY)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            ret, self.frame = self.cap.read()
            s_img = cv2.imread(script_dir + '\\images\\PoolTraceAr.png', cv2.IMREAD_UNCHANGED)

            if self.isMaximized():
                self.aplicar_preset_default(nombreArchivo="DefaultMaximizado.json")
            else:
                self.aplicar_preset_default()

        except Exception as ex:
            self.frame = None
            self.cap = None
            print("Error", ex)

    #cambia el monitor al que selecciono el usuario:
    def cambio_monitor(self, index):
        global display_monitor
        opcion = self.comboMonitores.itemText(index)
        print(f"monitor: {opcion}")
        if opcion != '':
            numero = int(re.search(r'\d+', opcion).group())
            numero = numero -1
            display_monitor = numero
            self.ventanaProyeccion.set_nroMonitor(display_monitor)

    def distancia_media_entre_puntos(self, x1, x2):
        distancia = (x2 - x1)
        return math.floor(distancia/2)

    #define si se esta proyectando en otro monitor o solo se esta viendo la interfaz principal:
    def proyectar(self):
        global proyectando, cerrarProyeccion, display_monitor
        self.cambio_monitor(display_monitor-1)
        if(proyectando==False):
            proyectando = True
            self.ventanaProyeccion.show()
            cerrarProyeccion=False
        else:
            proyectando=False
            cerrarProyeccion = True
            ventanaProyeccion.close()
        
    #abre la ventana de configuracion de parametros:
    def configurar(self):        
        self.ventanaContrasena.show()

    def ayuda(self):
       self.ventanaAyuda.show()
        
    def closeEvent(self, event):
        global cerrarProyeccion
        parar_de_actualizar(self)
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        pararHilos()
        cerrarProyeccion=True
        self.ventanaProyeccion.close()
        self.controlWindow.close()
        if cv2.getWindowProperty("Frame", cv2.WND_PROP_VISIBLE) > 0:
            cv2.destroyWindow("Frame")
        self.ventanaPrepro.close()
        self.ventanaParametrosSimulacion.close()
        event.accept()

    #en base al checkbox determina si hay o no bola en mano para el turno:
    def bola_en_mano(self):
        estado_actual = self.checkBolaEnMano.isChecked()

        if estado_actual == True:
            self.BolaEnMano = True
            print("Hay bola en mano")
        else:
            self.BolaEnMano = False
            print("No hay bola en mano")
        
    def ver_simulacion(self):
        if(self.algunaEstaSeleccionada == True and self.botonVerSimulacion.isEnabled()):
           self.repetirSimulacion = True

    #en base al checkbox determina si hay o no dos tiros para el turno:
    def dos_tiros(self):
        estado_actual = self.check2Tiros.isChecked()
        if estado_actual == True:
            self.Hay2Tiros = True
            print("Hay 2 tiros")
        else:
            self.Hay2Tiros = False
            print("No hay 2 tiros")

    def ver_todas_trayectorias(self):
        estado_actual = self.checkTrayectorias.isChecked()
        if estado_actual == True:
            self.VerTodasTrayectorias = True
            print("Se visualizan todas las trayectorias")
        else:
            self.VerTodasTrayectorias = False
            print("No se visualizan todas las trayectorias")
        self.hiloProyeccion.ver_todas_trayectorias(self.VerTodasTrayectorias)

    #en base al checkbox determina si hay o no mesa abierta para el turno:
    def mesa_abierta(self):
        estado_actual = self.checkMesaAbierta.isChecked()
        if estado_actual == True:
            self.hayMesaAbierta = True
            print ("Hay Mesa Abierta")
        else:
            self.hayMesaAbierta = False
            print("Hay Mesa Cerrada")

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
    
    def point_inside_roi(self, x, y, roi_x_min, roi_y_min, roi_x_max, roi_y_max):
        if roi_x_min <= x <= roi_x_max and roi_y_min <= y <= roi_y_max:
            return True
        else:
            return False
        

    def clic_largo(self):
        #clic izquierdo manteniendo 2 segundos 
        global clickEnBola
        if (self.corregirFrame == False):
            clickEnBola = True
            (x,y) = self.cursor_position
            self.bolaSeleccionada=(x,y,maxRadius)
            self.resaltar_bola_seleccionada()
            print("Se fuerza seleccion de bola")

    #evento que se ejecuta cuando se hace click en cualquier lugar:
    #maneja: movimiento de troneras, movimiento del roi, seleccion de bola para el turno
    def mousePressEvent(self, event):
            global resaltarBolaCorreccion
            self.cursor_position = (event.x(), event.y())
            if event.buttons() & Qt.RightButton:
                if(self.corregirFrame):
                    self.bolaSeleccionadaCorreccion = None
                    resaltarBolaCorreccion = False
                    x, y = self.cursor_position
                    self.circles.append((x-self.XIROI, y-self.YIROI, radioMax))
            else:
                self.timer_clic_largo.start(self.tiempo_minimo_clic_largo)
                if(self.corregirFrame == False):
                    # Verificar si se hizo clic dentro de los vértices del ROI
                    self.verticeSeleccionado = None
                    self.moverVertices = False
                    clickEnBola = False
                    if self.verVerticesROI:
                        vertices = [(self.XIROI, self.YIROI), (self.XDROI, self.YDROI)]
                        for i, vertice in enumerate(vertices):
                            distancia = np.sqrt(
                                (event.x() - vertice[0])**2 + (event.y() - vertice[1])**2)
                            if distancia <= 10:  # Si la distancia es menor o igual a 10 píxeles, se considera seleccionado
                                self.verticeSeleccionado = i
                                self.moverVertices = True
                                break           

                        # Verificar si el click está dentro de alguna de las troneras
                        x, y = event.x(), event.y()
                        for i, tronera in enumerate(self.troneras):
                            tronera_x, tronera_y = tronera
                            distance = np.sqrt((x - tronera_x) ** 2 + (y - tronera_y) ** 2)
                            if distance < self.radioTronera:  # Radio del círculo
                                self.selected_tronera = i
                                break

                        #Verificar si el click está dentro de alguna de los puntos de paredes
                        x,y = event.x(), event.y()
                        for i, punto in enumerate(self.puntos_paredes):
                            px, py = punto
                            distance = np.sqrt((x - px) ** 2 + (y - py) ** 2)
                            if distance <= 10:
                                self.selected_punto = i
                                break

                    if self.moverVertices == False and self.etiquetando==False and self.calculandoTiro == False:
                        if self.circles is not None:
                            for (x, y, r) in self.circles:
                                x = (x+self.XIROI)
                                y = (y+self.YIROI)
                                distancia = np.sqrt( (event.x()-x)**2 + (event.y()- y)**2)
                                if distancia <=10:
                                    print(f"bola {x},{y}")
                                    clickEnBola = True
                                    self.bolaSeleccionada=(x,y,r)
                                    self.resaltar_bola_seleccionada()
                                    # self.etiquetar=True
                                    self.tronerasPosibles = self.calcular_posibles_troneras()
                    if (self.etiquetando==True or self.calculandoTiro):
                        print("Espere por favor, se esta calculando el tiro")

                    if clickEnBola == False and self.moverVertices == False and self.etiquetando==False and self.calculandoTiro == False:
                        if self.point_inside_roi(event.x(),event.y(), self.XIROI, self.YIROI, self.XDROI,self.YDROI)==True:
                            self.deseleccionar_bola()
                else:           
                    clickEnBola = False
                    if(self.moviendo_bola_correccion == False):
                        if self.circles is not None:
                            for (x, y, r) in self.circles:
                                x = (x+self.XIROI)
                                y = (y+self.YIROI)
                                distancia = np.sqrt( (event.x()-x)**2 + (event.y()- y)**2)
                                if distancia <=10:
                                    print(f"bola {x},{y}")
                                    clickEnBola = True
                                    self.bolaSeleccionadaCorreccion=(x - self.XIROI,y - self.YIROI,r)
                                    self.resaltar_bola_seleccionada_correccion()
                    if clickEnBola == False and self.moviendo_bola_correccion == False:
                        print("entra aca")
                        if self.point_inside_roi(event.x(),event.y(), self.XIROI, self.YIROI, self.XDROI,self.YDROI)==True:
                            self.deseleccionar_bola_correccion()

    def resaltar_bola_seleccionada_correccion(self):        
        global resaltarBolaCorreccion        
        if self.bolaSeleccionadaCorreccion is not None:
            resaltarBolaCorreccion = True

    def deseleccionar_bola_correccion(self):
        global resaltarBolaCorreccion
        resaltarBolaCorreccion = False
        self.bolaSeleccionadaCorreccion = None

    def resaltar_bola_seleccionada(self):
        self.reiniciarProgressBar()
        global resaltarBola
        SingletonCompartida.delete_instance()
        self.botonCalcularTiroConfirmar.setDisabled(False)
        if self.bolaSeleccionada is not None:
            resaltarBola = True
            
            self.puntos_trayectoria_bola_blanca = None
            self.puntos_trayectorias_bolas = None
            self.puntos_trayectoria_bola_seleccionada = None


    def deseleccionar_bola(self):
        global resaltarBola
        resaltarBola = False
        self.bolaSeleccionada = None
        self.algunaEstaSeleccionada = False
        self.attrs = None
        self.best_player = None
        SingletonCompartida.delete_instance()
        self.botonCalcularTiroConfirmar.setDisabled(True)

    def obtener_troneras(self):
            return self.troneras
    
    def distance_between_points(self, punto1, punto2):
        x1, y1 = punto1
        x2, y2 = punto2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    #devuelve una linea paralela a la del input pero con una distancia dada:
    def parallel_line(self, punto1, punto2, distancia):
        # Desempaquetar los puntos en coordenadas (x, y)
        x1, y1 = punto1
        x2, y2 = punto2

        # Calcular la longitud y dirección de la línea original
        original_length = self.distance_between_points(punto1, punto2)
        dx = (x2 - x1) / original_length
        dy = (y2 - y1) / original_length

        # Calcular los nuevos puntos de la recta paralela desplazada
        new_x1 = x1 + distancia * dy
        new_y1 = y1 - distancia * dx
        new_x2 = x2 + distancia * dy
        new_y2 = y2 - distancia * dx

        new_punto1 = (new_x1, new_y1)
        new_punto2 = (new_x2, new_y2)
        # Devolver los dos puntos de la nueva recta paralela desplazada
        return new_punto1, new_punto2

    #calcula cuales troneras tienen camino libre para la bola seleccionada:
    def calcular_posibles_troneras(self):
        self.poligonos = []
        self.poligonosImposibles = []
        if self.bolaSeleccionada is None:
            return
        troneras = self.obtener_troneras()
        tronerasPosibles = []
        for tronera in troneras:
            (xb,yb,rb)=self.bolaSeleccionada
            (x,y)=tronera
            vertices = []

            (xp1,yp1), (xp2,yp2) = self.parallel_line((xb,yb),(x,y),rb)
            (xp3,yp3), (xp4,yp4) = self.parallel_line((xb,yb),(x,y),-rb)

            vertices.append((xp1,yp1))
            vertices.append((xp2,yp2))
            vertices.append((xp3,yp3))
            vertices.append((xp4,yp4))

            verticesOrdenados = self.sort_vertices(vertices)
            puntos = np.array(verticesOrdenados, np.int32)
            puntos = puntos.reshape((-1, 1, 2))

            posible = self.revisar_circulos(verticesOrdenados,self.circles)

            puntos = np.array(verticesOrdenados, np.int32)
            puntos = puntos.reshape((-1, 1, 2))            
            if posible:
                self.poligonos.append(puntos)
                tronerasPosibles.append(tronera)
            else:
                self.poligonosImposibles.append(puntos)
        return tronerasPosibles        

    #ordena los vertices dados para determinar un trapecio valido 
    def sort_vertices(self,vertices):
        # Calcula el centroide del polígono
        cx = int(sum(x for x, y in vertices) / len(vertices))
        cy = int(sum(y for x, y in vertices) / len(vertices))
        centroid = (cx, cy)

        # Calcula los ángulos de los puntos respecto al centroide
        angles = []
        for x, y in vertices:
            angle = np.arctan2(cy - y, cx - x)
            angles.append(angle)

        # Ordena los puntos en función de sus ángulos y el producto cruzado con el vector (-1, 0)
        sorted_vertices = [v for _, v in sorted(zip(angles, vertices), key=lambda x: (x[0], np.cross(centroid, x[1])))]
        
        return sorted_vertices


    def distancia_puntos(self,punto1, punto2):
        x1, y1 = punto1
        x2, y2 = punto2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    #determina si un circulo esta dentro de un trapecio o no:
    def esta_dentro_del_trapecio(self, trapecio, centro_circulo, radio_circulo):
        x, y = centro_circulo
        x1, y1 = trapecio[0]
        x2, y2 = trapecio[1]
        x3, y3 = trapecio[2]
        x4, y4 = trapecio[3]

        # Función para calcular la distancia entre dos puntos
        def distancia_entre_puntos(x1, y1, x2, y2):
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        # Proyectar el punto (x, y) sobre el segmento definido por los puntos (x1, y1) y (x2, y2)
        def proyectar_punto_en_segmento(x, y, x1, y1, x2, y2):
            vx, vy = x2 - x1, y2 - y1
            wx, wy = x - x1, y - y1
            c1 = max(0, min(vx * wx + vy * wy, vx * vx + vy * vy))
            px = x1 + (c1 * vx) / (vx * vx + vy * vy)
            py = y1 + (c1 * vy) / (vx * vx + vy * vy)
            return px, py

        # Verificar si el centro del círculo está dentro de cada segmento definido por los lados del trapecio
        proy_1 = proyectar_punto_en_segmento(x, y, x1, y1, x2, y2)
        proy_2 = proyectar_punto_en_segmento(x, y, x2, y2, x3, y3)
        proy_3 = proyectar_punto_en_segmento(x, y, x3, y3, x4, y4)
        proy_4 = proyectar_punto_en_segmento(x, y, x4, y4, x1, y1)

        # Verificar si las proyecciones están dentro del segmento que define cada lado
        def esta_dentro_del_segmento(x, y, x1, y1, x2, y2):
            return (min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2))

        if esta_dentro_del_segmento(*proy_1, x1, y1, x2, y2) and \
        esta_dentro_del_segmento(*proy_2, x2, y2, x3, y3) and \
        esta_dentro_del_segmento(*proy_3, x3, y3, x4, y4) and \
        esta_dentro_del_segmento(*proy_4, x4, y4, x1, y1):

            # Verificamos si está completamente dentro o parcialmente dentro
            distancia_minima = min(
                distancia_entre_puntos(x, y, x1, y1),
                distancia_entre_puntos(x, y, x2, y2),
                distancia_entre_puntos(x, y, x3, y3),
                distancia_entre_puntos(x, y, x4, y4)
            )

            if distancia_minima <= radio_circulo:
                # La distancia mínima es menor o igual al radio del círculo, entonces el círculo está parcialmente dentro del trapecio
                return "Partially Inside"
            else:
                # El centro del círculo está completamente dentro del trapecio
                return "Entirely Inside"
        else:
            # El centro del círculo está fuera del trapecio
            return "Outside"

    #determina si el trapecio hacia la tronera es o no valido (tiene o no bolas interseptando el camino):
    def revisar_circulos(self,trapecio_vertices, circulos):
        trapecio_valido = True
        for circulo in circulos:
            x, y, radio = circulo
            x=x+self.XIROI
            y=y+self.YIROI
            distancia = math.sqrt((self.bolaSeleccionada[0]-x)**2 + (self.bolaSeleccionada[1]-y)**2)
            #se saltea a si misma (la seleccionada)
            if distancia < radio + 1:
                continue  
            centro_circulo = (x, y)
            # print("Circulo :"+ str(centro_circulo) +" "+ str(self.esta_dentro_del_trapecio(trapecio_vertices,centro_circulo,radio)))
            # print("Vertices de trapecio " + str(trapecio_vertices) )
            # print("Radio: "+str(radio))
            
            if self.esta_dentro_del_trapecio(trapecio_vertices,centro_circulo,radio):
                trapecio_valido = False
                return trapecio_valido
        return trapecio_valido
    
    def calcular_area(self,x1, y1, x2, y2, x3, y3):
        return abs((x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)) / 2.0)

    def esta_dentro_del_trapecio(self, trapecio, centro_circulo, radio_circulo):
        x, y = centro_circulo
        if (self.punto_dentro_del_trapecio(trapecio,(x,y))== False):
            return self.circulo_barely_inside_trapecio(trapecio,centro_circulo,radio_circulo)
        else:
            return True
        
    def circulo_barely_inside_trapecio(self, trapecio, centro_circulo, radio_circulo):
        x, y = centro_circulo
        x1, y1 = trapecio[0]
        x2, y2 = trapecio[1]
        x3, y3 = trapecio[2]
        x4, y4 = trapecio[3]

        # Función para calcular la distancia entre dos puntos
        def distancia_entre_puntos(x1, y1, x2, y2):
            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        # Función para calcular la distancia mínima entre un punto (x, y) y un segmento definido por dos puntos (x1, y1) y (x2, y2)
        def distancia_minima_punto_segmento(x, y, x1, y1, x2, y2):
            A = x - x1
            B = y - y1
            C = x2 - x1
            D = y2 - y1

            dot = A * C + B * D
            len_sq = C * C + D * D
            param = dot / len_sq

            if param < 0:
                xx = x1
                yy = y1
            elif param > 1:
                xx = x2
                yy = y2
            else:
                xx = x1 + param * C
                yy = y1 + param * D

            dx = x - xx
            dy = y - yy
            return (dx ** 2 + dy ** 2) ** 0.5

        # Calcular las distancias mínimas desde el centro del círculo a cada uno de los lados del trapecio
        distancias_minimas = [
            distancia_minima_punto_segmento(x, y, x1, y1, x2, y2),
            distancia_minima_punto_segmento(x, y, x2, y2, x3, y3),
            distancia_minima_punto_segmento(x, y, x3, y3, x4, y4),
            distancia_minima_punto_segmento(x, y, x4, y4, x1, y1)
        ]

        # Verificar si la distancia mínima es mayor que el radio del círculo
        distancia_minima = min(distancias_minimas)
        if distancia_minima > radio_circulo:
            return False
        else:
            return True

    def punto_dentro_del_trapecio(self,trapecio, punto):
        x, y = punto
        vertices = trapecio + [trapecio[0]]  # Añadir el primer vértice al final para cerrar el trapecio

        def producto_cruzado(p1, p2, p3):
            return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])

        # Verificar si el punto está dentro del trapecio
        for i in range(4):
            if producto_cruzado(vertices[i], vertices[i + 1], (x, y)) < 0:
                return False
        return True

    #determina la distancia minima desde un punto hacia una recta:
    def distancia_punto_a_linea(self,x, y, x1, y1, x2, y2):
        # Calcula la distancia entre el punto (x, y) y la línea definida por los puntos (x1, y1) y (x2, y2)
        return abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
    
    def mouseDoubleClickEvent(self, event):
        if(self.corregirFrame):
                if(self.bolaSeleccionadaCorreccion is not None):
                    if (self.borrandoSeleccionada()==False):
                        x,y,r = self.bolaSeleccionadaCorreccion
                        indice = self.encontrar_indice_por_coordenadas(x ,y)
                        if indice != -1:
                            del self.circles[indice]
                            self.bolaSeleccionadaCorreccion = None
        print("Doble clic detectado")

    def contextMenuEvent(self, event):
        # if(self.corregirFrame):
        #         if (self.bolaSeleccionadaCorreccion is None):
        #             x, y = self.cursor_position
        #             self.circles.append((x-self.XIROI, y-self.YIROI, radioMax))
        print("Clic derecho detectado")
    
    def mouseMoveEvent(self, event):
            if(self.corregirFrame == False):
                if self.moverVertices and self.verticeSeleccionado is not None:
                    print(f"moviendo vertice: {self.verticeSeleccionado}")
                    # Actualizar la posición del vértice seleccionado según la posición del mouse
                    if self.verticeSeleccionado == 0 and event.x() < self.XDROI-10 and event.y() < self.YDROI-10 and event.y() > 1 and event.x() > 1 and event.x() < ResolucionX and event.y() < ResolucionY:
                        self.XIROI = event.x()
                        self.YIROI = event.y()
                    elif self.verticeSeleccionado == 1 and event.x() > self.XIROI+10 and event.y() > self.YIROI+10 and event.x() > 1 and event.y() > 1 and event.x() < ResolucionX and event.y() < ResolucionY:
                        self.XDROI = event.x()
                        self.YDROI = event.y()
                    self.hiloProyeccion.actualizar_roi(xiroi=self.XIROI, yiroi=self.YIROI, xdroi=self.XDROI, ydroi=self.YDROI)
                    self.actualizar_roi()
                if self.selected_tronera is not None:
                    x, y = event.x(), event.y()
                    self.troneras[self.selected_tronera] = (x, y)
                    self.update()
                if self.selected_punto is not None: 
                    x,y = event.x(), event.y()
                    self.puntos_paredes[self.selected_punto] = (x,y)
                    self.update()
            else:           
                x, y = event.x(), event.y()
                moviendoSeleccionada = False
                if self.bolaSeleccionada is not None:
                    (xs,ys,rs) = self.bolaSeleccionada
                    dist = math.sqrt((xs-x)**2 + (ys-y)**2)
                    if(dist < rs*2):
                        moviendoSeleccionada = True
                indice = self.encontrar_indice_por_coordenadas(x- self.XIROI,y- self.YIROI)
                if(indice != -1):
                    _,_,aux = self.circles[indice]
                    self.circles[indice] = (x - self.XIROI, y - self.YIROI,aux)                
                    self.moviendo_bola_correccion = True
                    self.bolaSeleccionadaCorreccion = (x - self.XIROI, y - self.YIROI, aux)
                    if moviendoSeleccionada:
                        self.bolaSeleccionada = (x , y, maxRadius)
                    global resaltarBolaCorreccion
                    resaltarBolaCorreccion = True
                    self.update()

    def encontrar_indice_por_coordenadas(self, x, y):
        for i, circle in enumerate(self.circlesCopy):
            x_circle, y_circle, r_circle = circle
            distancia = math.sqrt((x_circle- x)**2 + (y_circle-y)**2)
            if distancia <= r_circle:                
                    return i  # Devuelve el índice si encuentra coincidencia
        return -1  # Devuelve -1 si no encuentra coincidencia
    
    
    def mouseReleaseEvent(self, event):
        self.selected_tronera = None
        self.selected_punto = None
        self.moviendo_bola_correccion = False
        if event.button() == Qt.LeftButton:
            self.timer_clic_largo.stop()

    def actualizar_roi(self):
        mitadMesa = self.distancia_media_entre_puntos(self.XIROI, self.XDROI)
        self.troneras[0] = (self.XIROI,self.YIROI)
        self.troneras[1] = (self.XDROI,self.YDROI)
        self.troneras[2] = (self.XIROI,self.YDROI)
        self.troneras[3] = (self.XDROI,self.YIROI)
        self.troneras[4] = (self.XIROI+mitadMesa,self.YIROI)
        self.troneras[5] = (self.XIROI+mitadMesa,self.YDROI)    
    def crear_ROI(self):
        if self.creandoROI == False:
            self.creandoROI = True
        elif self.creandoROI == True:
            self.creandoROI = False

        if self.creandoROI:
            self.verROI = True
            self.verVerticesROI = True
        else:
            self.verROI = False
            self.verVerticesROI = False

    def hay_movimiento(self, movimiento):
        self.hayMovimiento = movimiento
    
    #abre la ventana de configuracion de preprocesamiento de imagen:
    def abrir_preprocesamiento(self):
        self.ventanaPrepro.show()

    def abrir_parametros_simulacion(self):
        self.ventanaParametrosSimulacion.show()

    #aplica los preprocesamientos que el usuario determine:
    def aplicar_preprocesamientos(self, image):
        global aplicarBlur,aplicarBrillo,aplicarContraste,aplicarHist,mostrarFrameRaws
        if aplicarBlur:
            global Blur
            image = cv2.GaussianBlur(image, (Blur, Blur), 0)
        if aplicarHist:
            image = cv2.equalizeHist(image)
        if aplicarContraste:
            global Alpha, Beta
            image = cv2.convertScaleAbs(image, alpha=Alpha, beta=Beta)
        if mostrarFrameRaw:
            cv2.imshow("Frame",image)
            cv2.resizeWindow("Frame", ResolucionX, ResolucionY)
        return image

    #deprecated
    # def agregar_o_actualizar_bola(self,x,y,r):
    #         global bolas
    #         actualizada = False
    #         encontrada = False
    #         for bola in bolas:
    #             distancia = math.sqrt((bola.x- x)**2 + (bola.y-y)**2)
    #             if distancia <= 30:
    #                 bola.actualizar_posicion(x,y,r)
    #                 actualizada = True
    #                 break
    #         if actualizada==False:
    #             bolas.append(Bola(x,y,r))
    #         for bola in bolas:
    #             for (xd,yd,rd) in self.circles:
    #                 distancia = math.sqrt((bola.x - xd)**2 + (bola.y - yd)**2)
    #                 if distancia <= 30:
    #                     encontrada = True
    #                     break
    #             if encontrada == False:
    #                 bolas.remove(bola)
    #             encontrada = False


    #deprecated
    def obtener_id_bola(self,x,y):
        global bolas
        encontrada = False
        for bola in bolas:
            distancia = math.sqrt((bola.x- x)**2 + (bola.y-y)**2)
            if distancia <= 4:
                encontrada = True
                return bola.id
        if encontrada == False:
            return -1
    
    def eliminar_circulos_repetidos(self, circulos):
    # Creamos un diccionario para agrupar los círculos por sus coordenadas (x, y).
        circulos_dict = {}
        
        for x, y, radio in circulos:
            # Redondeamos las coordenadas al entero más cercano dividido por 3 (margen).
            # Esto nos permite agrupar los círculos que estén cerca.
            x_key = round(x / 3)
            y_key = round(y / 3)
            
            # Si no existe la clave en el diccionario, la creamos con el círculo actual.
            if (x_key, y_key) not in circulos_dict:
                circulos_dict[(x_key, y_key)] = (x, y, radio)
            else:
                # Si ya existe la clave, comparamos los radios y conservamos el círculo con el radio más grande.
                if radio > circulos_dict[(x_key, y_key)][2]:
                    circulos_dict[(x_key, y_key)] = (x, y, radio)
        
        # Convertimos los valores del diccionario de nuevo en una lista para obtener los círculos únicos.
        círculos_únicos = list(circulos_dict.values())
        
        return círculos_únicos
    
    #bucle principal de ejecucion:
    def actualizar_video(self):
        try:
            global resaltarBola, resaltarBolaCorreccion, minRadius, maxRadius
            if not self.seguirActualizando:
                return
            if self.cap is not None and not is_frame_black(self.frame):
                ret, self.frame = self.cap.read()
            else:
                ret = False
                width, height = ResolucionX, ResolucionY
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.label.setPixmap(QPixmap.fromImage(q_image)) 
            if ret and not is_frame_black(self.frame):
                
                if self.inicio:
                    self.XIROI, self.YIROI = 100, 100
                    self.XDROI, self.YDROI = 150, 150
                    self.inicio = False
                    self.hiloProyeccion.actualizar_roi(xiroi=self.XIROI, yiroi=self.YIROI, xdroi=self.XDROI, ydroi=self.YDROI)
                    self.actualizar_roi()
            
                altura, ancho = self.frame.shape[:2]

                # Calcular el centro del frame para utilizarlo como punto de rotación
                centro = (ancho // 2, altura // 2)
                matriz_rotacion = cv2.getRotationMatrix2D(centro, anguloRotar, 1.0)
                self.frame = cv2.warpAffine(self.frame,matriz_rotacion,(ancho,altura))
                self.roi = self.frame[self.YIROI:self.YDROI 
                                , self.XIROI:self.XDROI]
                
                if self.etiquetar:
                    #se generan las imagenes de cada bola:
                    if self.etiquetando == False:
                        fecha_hora_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
                        nombre_archivo = f"Mesa_{fecha_hora_actual}.png"
                        ret, frame = self.cap.read()
                        roi = frame[self.YIROI:self.YDROI 
                                , self.XIROI:self.XDROI]
                        carpeta = Path(script_dir + '\\Capturas\\')

                        # Verificamos si la carpeta no existe
                        if not carpeta.exists():
                            # Creamos la carpeta
                            carpeta.mkdir(parents=True, exist_ok=True)
                            carpeta = Path(script_dir + '\\Capturas\\Bolas\\')
                            carpeta.mkdir(parents=True, exist_ok=True)
                            
                        pathCaptura = script_dir + "\\Capturas\\" + nombre_archivo
                        pathOutput = script_dir + "\\Capturas\\Bolas\\" 
                        cv2.imwrite(pathCaptura, roi)
                        ListaApareada = ImageProcessor.crop_circles(pathCaptura,self.circles,pathOutput)

                    #se manda un hilo a etiquetar cada bola de las imagenes generadas:
                    if self.etiquetando == False:
                        #en prod pasarle True para que borre las capturas que usa:
                        self.hiloEtiquetador = threading.Thread(target=Etiquetar, args=(pathOutput,ListaApareada,True,True))
                        self.hiloEtiquetador.start()
                        self.etiquetando = True
                    
                    self.hiloEtiquetador.join(timeout=0.01)

                    if  self.hiloEtiquetador.is_alive():
                        #aca se puede poner un spin en la interfaz:
                        #print("etiquetando...")
                        self.printUI("Ejecutando IA...")
                        self.avanzarProgressBar(30)
                    else:
                        print("fin de etiquetado")
                        self.etiquetar = False
                        self.etiquetando = False
                        with variable_compartida_lock:
                            self.listaEtiquetada = ListaApareadaConEtiquetas
                            self.bolaBlanca = self.obtenerBolaBlanca(self.listaEtiquetada)
                        
                if( self.listaEtiquetada is not None and self.etiquetando==False):
                    #si devuelve true, cambiaron de ubicacion las bolas -> no se puede continuar, caso contrario continuar
                    if(self.calculandoTiro == False):
                        if(self.checkTiroFinal.isChecked() and self.selecciono_negra(self.listaEtiquetada,self.bolaSeleccionada)==False):
                            print("Error, no selecciono la bola negra para el tiro final")
                            self.printUIError("Seleccione la bola negra para el tiro final")
                            self.deseleccionar_bola()
                            self.listaEtiquetada.clear()
                            self.listaEtiquetada = None
                            self.ultimaListaEtiquetada = None
                            self.repetirSimulacion = False
                            self.botonCancelar.setDisabled(True)
                            self.botonCalcularTiroConfirmar.setDisabled(True)
                            self.corregirFrame = False
                        elif(self.checkTiroFinal.isChecked() == False and self.selecciono_negra(self.listaEtiquetada,self.bolaSeleccionada)==True):
                            print("Error, selecciono la bola negra pero no indico la tronera")
                            self.printUIError("Seleccione la tronera")
                            self.deseleccionar_bola()
                            self.listaEtiquetada.clear()
                            self.listaEtiquetada = None
                            self.ultimaListaEtiquetada = None
                            self.repetirSimulacion = False
                            self.botonCancelar.setDisabled(True)
                            self.botonCalcularTiroConfirmar.setDisabled(True)
                            self.corregirFrame = False
                        # elif( self.cambiaron_bolas_previo_al_tiro( self.listaEtiquetada , self.circles ) ):
                        #     print("Error, las bolas cambiaron de posicion.")
                        #     self.printUIError("Error, las bolas cambiaron de posicion.")
                        #     self.deseleccionar_bola()
                        #     self.listaEtiquetada.clear()
                        #     self.listaEtiquetada = None
                        #     self.ultimaListaEtiquetada = None
                        #     self.repetirSimulacion = False
                        elif( self.selecciono_la_blanca(self.listaEtiquetada)):
                            print ("Error, se selecciono la bola blanca para embocar")
                            self.printUIError("Error, se selecciono la bola blanca para embocar")
                            self.deseleccionar_bola()
                            self.listaEtiquetada.clear()
                            self.listaEtiquetada = None
                            self.ultimaListaEtiquetada = None
                            self.repetirSimulacion = False
                            self.botonCancelar.setDisabled(True)
                            self.botonCalcularTiroConfirmar.setDisabled(True)
                            self.corregirFrame = False
                        elif( self.existe_la_negra(self.listaEtiquetada)==False):
                            print("El jugador anterior emboco la bola negra, fin del partido")
                            self.printUI("El jugador anterior emboco la bola negra, fin del partido")
                            self.deseleccionar_bola()
                            self.listaEtiquetada.clear()
                            self.listaEtiquetada = None
                            self.ultimaListaEtiquetada = None
                            self.repetirSimulacion = False
                            self.botonCancelar.setDisabled(True)
                            self.botonCalcularTiroConfirmar.setDisabled(True)
                            self.corregirFrame = False
                        elif( self.hay_bola_blanca(self.listaEtiquetada)==False):
                            print("No hay bola blanca en la mesa")
                            self.printUIError("No hay bola blanca en la mesa")
                            self.deseleccionar_bola()
                            self.listaEtiquetada.clear()
                            self.listaEtiquetada = None
                            self.ultimaListaEtiquetada = None
                            self.repetirSimulacion = False
                            self.botonCancelar.setDisabled(True)
                            self.botonCalcularTiroConfirmar.setDisabled(True)
                            self.corregirFrame = False
                        elif(self.solo_una_blanca(self.listaEtiquetada)==False):
                            print("Error, hay mas de una bola blanca en la mesa")
                            self.printUIError("Error, hay mas de una bola blanca en la mesa")
                            self.deseleccionar_bola()
                            self.listaEtiquetada.clear()
                            self.listaEtiquetada = None
                            self.ultimaListaEtiquetada = None
                            self.repetirSimulacion = False
                            self.botonCancelar.setDisabled(True)
                            self.botonCalcularTiroConfirmar.setDisabled(True)
                            self.corregirFrame = False
                        elif(self.solo_una_negra(self.listaEtiquetada)==False):
                            print("Error, hay mas de una bola 8 en la mesa")
                            self.printUI("Error, hay mas de una bola 8 en la mesa")
                            self.deseleccionar_bola()
                            self.listaEtiquetada.clear()
                            self.listaEtiquetada = None
                            self.ultimaListaEtiquetada = None
                            self.repetirSimulacion = False
                            self.botonCancelar.setDisabled(True)
                            self.botonCalcularTiroConfirmar.setDisabled(True)
                            self.corregirFrame = False
                        elif(self.maximo_rayadas_superado(self.listaEtiquetada)==True):
                            print("Error, hay mas de 7 bolas rayadas en la mesa")
                            self.printUIError("Error, hay mas de 7 bolas rayadas en la mesa")
                            self.deseleccionar_bola()
                            self.listaEtiquetada.clear()
                            self.listaEtiquetada = None
                            self.ultimaListaEtiquetada = None
                            self.repetirSimulacion = False
                            self.botonCancelar.setDisabled(True)
                            self.botonCalcularTiroConfirmar.setDisabled(True)
                            self.corregirFrame = False
                        elif(self.maximo_lisas_superado(self.listaEtiquetada)==True):
                            print("Error, hay mas de 7 bolas lisas en la mesa")
                            self.printUIError("Error, hay mas de 7 bolas lisas en la mesa")
                            self.deseleccionar_bola()
                            self.listaEtiquetada.clear()
                            self.listaEtiquetada = None
                            self.ultimaListaEtiquetada = None
                            self.repetirSimulacion = False
                            self.botonCancelar.setDisabled(True)
                            self.botonCalcularTiroConfirmar.setDisabled(True)
                            self.corregirFrame = False
                        elif(self.selecciono_negra(self.listaEtiquetada,self.bolaSeleccionada)==True and self.hayMesaAbierta == True):
                            print("Error, no se puede seleccionar la negra cuando hay mesa abierta")
                            self.printUIError("Error, no se puede seleccionar la negra cuando hay mesa abierta")
                            self.deseleccionar_bola()
                            self.listaEtiquetada.clear()
                            self.listaEtiquetada = None
                            self.ultimaListaEtiquetada = None
                            self.repetirSimulacion = False
                            self.botonCancelar.setDisabled(True)
                            self.botonCalcularTiroConfirmar.setDisabled(True)
                            self.corregirFrame = False
                        elif(self.seleccion_de_negra_incorrecto(self.listaEtiquetada, self.bolaSeleccionada)==True):
                            print("Error, se selecciono la negra pero no es la ultima bola")
                            self.printUIError("Error, se selecciono la negra pero no es la ultima bola")
                            self.deseleccionar_bola()
                            self.listaEtiquetada.clear()
                            self.listaEtiquetada = None
                            self.ultimaListaEtiquetada = None
                            self.repetirSimulacion = False
                            self.botonCancelar.setDisabled(True)
                            self.botonCalcularTiroConfirmar.setDisabled(True)
                            self.corregirFrame = False
                        self.progressBar.setValue(100)

                    if(self.listaEtiquetada is not None):
                        if self.bolaBlanca is not None:
                            (xb, yb, rb) = self.bolaBlanca
                            xb= xb + self.XIROI
                            yb= yb + self.YIROI
                            self.bolaBlanca = (xb,yb,rb)
                        
                        if (self.bolaBlanca is not None and self.bolaSeleccionada is not None):
                            tamROI = self.obtener_tam_ROI()
                            trayectoriasValidasBlanca = []
                            trayectoriasValidasSeleccionada = []
                            #self.fisicas = Fisicas(False, False, False, self.listaEtiquetada, self.bolaSeleccionada, bolaBlanca, tamROI, self.XIROI, self.YIROI,self.XDROI, self.YDROI, self.troneras, self.radioTronera, maxRadius, self.puntos_paredes,self.BolaEnMano, self.Hay2Tiros, self.hayMesaAbierta)
                            #self.fisicas.setear_pasos_tiempo(5)
                            
                            self.embocarNegra = False
                            (xs,ys,rs) = self.bolaSeleccionada
                            xs = xs - self.XIROI
                            ys = ys - self.YIROI
                            
                            
                            if(self.calculandoTiro == False):
                                singletonCompartida = SingletonCompartida(self.listaEtiquetada.copy(), (xs,ys,rs), tamROI,self.embocarNegra, self.BolaEnMano, self.Hay2Tiros, self.hayMesaAbierta,  self.troneraTiroFinal, distancia_railes, distancia_troneras_medias, distancia_troneras_esquinas,limite_velocidad, friccion_bolas, friccion_railes,ancho_mesa,tam_bolas_simulacion, alto_mesa, radio_troneras_IA)
                                SingletonRespuesta.delete_instance()
                                self.hiloCalculoTiro = miHilo(distancia_railes, distancia_troneras_medias, distancia_troneras_esquinas,limite_velocidad, friccion_bolas, friccion_railes, ancho_mesa,tam_bolas_simulacion, alto_mesa, radio_troneras_IA)
                                self.hiloCalculoTiro.start()
                                self.calculandoTiro = True

                            self.hiloCalculoTiro.join(timeout=0.01)

                            if  self.hiloCalculoTiro.is_alive():
                                #aca se puede poner un spin en la interfaz:6
                                #print("Calculando tiro...")
                                self.printUI("Calculando tiro...")
                                self.avanzarProgressBar(95)
                            else:
                                self.calculandoTiro = False 
                                
                                self.tiro_seleccionado = self.hiloCalculoTiro.tiroSeleccionado                           

                                self.respuesta_hiloTiro = self.hiloCalculoTiro.respuesta
                                self.puntos_trayectoria_bola_blanca =  self.respuesta_hiloTiro.trayectoriaBlanca  
                                self.puntos_trayectorias_bolas =  self.respuesta_hiloTiro.trayectorias   
                                self.velocidadRequerida = self.convertir_velocidad( self.respuesta_hiloTiro.velocidad)
                                print(f"velocidad de tiro requerida: {self.velocidadRequerida}")
                    
                                self.attrs =  self.respuesta_hiloTiro.attrs
                                self.best_player =  self.respuesta_hiloTiro.best_player
                                SingletonRespuesta.delete_instance()
                                print("fin calculo de trayectorias")
                                self.printUI("Calculo de trayectorias finalizado, Potencia requerida: " + f"{self.velocidadRequerida:.1f}")
                                self.velocidadRequerida = -0.1
                                self.botonCalcularTiroConfirmar.setDisabled(True)
                                self.bolaSeleccionada = None
                                resaltarBola = False
                                self.botonCalcularTiroConfirmar.setDisabled(True)
                                self.botonCancelar.setDisabled(True)
                                self.corregirFrame = False
                                
                                # for i in range(0, 5):
                                self.progressBar.setValue(100)

                                self.listaEtiquetada = None
                                with variable_compartida_lock:
                                    ListaApareadaConEtiquetas.clear()         
                            
                                # self.IA = IA_Handler()
                                # self.IA.invocarIA()
            
                                    #print(f"calculando {i+1} de 100...")
                                    #cuando hagamos algunos calculos tenemos que pasarle en vez de randoms algo mejor definido:
                                    #self.velXBlanca = random.randint(10,100)
                                    #self.velYBlanca = random.randint(10,100)
                                    #self.fisicas.setear_velocidad_inicial_blanca(self.velXBlanca,self.velYBlanca)
                                    
                                    #trayectoriasBlanca, trayectoriasSeleccionada, tiroValido, entroBlanca, entroSeleccionada, entroNegra, puntos_trayectoria_blanca, puntos_trayectoria_seleccionada, puntos_trayectorias = self.fisicas.simular()                                    
                                    #self.puntos_trayectoria_bola_blanca = puntos_trayectoria_blanca    
                                    #self.puntos_trayectoria_bola_seleccionada = puntos_trayectoria_seleccionada         
                                    #self.puntos_trayectorias_bolas = puntos_trayectorias                       
                                    #self.fisicas.reiniciar_simulacion()
                                    #if(entroSeleccionada and entroNegra==False and entroBlanca== False and tiroValido):
                                        #trayectoriasValidasBlanca.append(trayectoriasBlanca)
                                        #trayectoriasValidasSeleccionada.append(trayectoriasSeleccionada)
                # Parte del if(testear si funciona bien sin la condicion)           
                # and self.bolaSeleccionada is not None
                if(self.repetirSimulacion == True ):
                    if (self.tiro_seleccionado==3):
                        if (self.repitiendo_simulacion == False): 
                            self.repitiendo_simulacion = True     
                            tamROI = self.obtener_tam_ROI()
                            self.bolaBlanca = self.obtenerBolaBlanca(self.ultimaListaEtiquetada)
                            self.fisicas = None
                            self.fisicas = Fisicas(True, False, False, self.ultimaListaEtiquetada, self.bolaSeleccionada, self.bolaBlanca, tamROI, self.XIROI, self.YIROI,self.XDROI, self.YDROI, self.troneras, self.radioTronera, maxRadius, self.puntos_paredes,self.BolaEnMano, self.Hay2Tiros, self.hayMesaAbierta)
                            self.fisicas.setear_pasos_tiempo(5)
                            self.fisicas.setear_velocidad_inicial_blanca(self.velXBlanca,self.velYBlanca)
                            self.fisicas.simular()                                       
                            self.fisicas.reiniciar_simulacion()
                            self.repitiendo_simulacion = False

                    elif ((self.tiro_seleccionado==1 or self.tiro_seleccionado==2) and self.best_player is not None and self.attrs is not None):
                        if(self.repitiendo_simulacion == False):
                                # self.hiloCalculoTiro = threading.Thread(target=VerSimulacion, args = (self.attrs, self.best_player))
                                # self.hiloCalculoTiro.start()
                                self.hiloCalculoTiro.VerSimulacion(self.attrs, self.best_player)
                                self.repitiendo_simulacion = True

                        #self.hiloCalculoTiro.join(timeout=0.01)

                        if  self.hiloCalculoTiro.is_alive():
                            #aca se puede poner un spin en la interfaz:
                            print("Simulando tiro...")
                            self.printUI("Simulando tiro...")
                        else:
                            self.repitiendo_simulacion = False 
                    
                    self.repetirSimulacion = False

                if self.verROI == False:
                    for tronera, label in zip(self.troneras, self.troneras_labels_usuario):
                            x, y = tronera
                            cv2.putText(self.frame, label, (x , y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

                if self.verROI:
                    cv2.rectangle(self.frame, (self.XIROI, self.YIROI),
                                (self.XDROI, self.YDROI), (0, 255, 0), 2)
                    #grafica los huecos (troneras):
                    for tronera, label in zip(self.troneras, self.troneras_labels):
                        x, y = tronera
                        cv2.circle(self.frame, (x, y), self.radioTronera, (255, 255, 0), 2)
                        cv2.putText(self.frame, label, (x , y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

                    #grafica los puntos de paredes:
                    for punto, label in zip(self.puntos_paredes, self.puntos_paredes_labels):
                        x,y = punto
                        cv2.circle(self.frame, (x,y), 10 , (0,255,0),1)
                        cv2.putText(self.frame, label, (x+5,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
                        x1 = x - 10
                        y1 = y - 10
                        x2 = x + 10
                        y2 = y + 10
                        cv2.line(self.frame, (x1, y1), (x2, y2), (0,255,0), thickness=1)
                        cv2.line(self.frame, (x1, y2), (x2, y1), (0,255,0), thickness=1)

                if self.verVerticesROI:
                    cv2.circle(self.frame, (self.XIROI, self.YIROI),int(radioMin/2), (0, 255, 0), 2)
                    cv2.circle(self.frame, (self.XDROI, self.YDROI),int(radioMin/2), (0, 255, 0), 2)
                
                image = cv2.cvtColor(self.roi, cv2.COLOR_BGR2GRAY)
                image = self.aplicar_preprocesamientos(image)
            

                global Param1, Param2, hough
                # Cargar el fotograma actual en el objeto cv2.cuda_GpuMat
                if(computo == "GPU" and self.corregirFrame == False):
                    d_frame.upload(image)
                    self.circles = hough.detect(d_frame)
                elif (computo == "CPU"):
                    self.circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, 15, param1=85, param2=11, minRadius=4, maxRadius=10)
                if(computo == "GPU" and self.corregirFrame == True):
                    self.circles = self.circlesCopy
                global circles_prev
            
                self.hiloProyeccion.actualizar_circles([])
                if self.circles is not None:
                    if(computo == "GPU" and self.corregirFrame == False ):
                        self.circles = self.circles.download()
                    if(self.corregirFrame == True):
                        self.circles = self.circlesCopy
                    if self.circles is not None:
                        if(self.corregirFrame == False):
                            self.circles = np.round(self.circles[0, :]).astype(int)

                        self.circlesProyeccion = self.circles
                        self.hiloProyeccion.actualizar_circles(self.circles)

                        
                        radioProm = int((minRadius+maxRadius)/2)

                        i=0
                    
                        if(self.corregirFrame == False):
                            self.circles  = self.eliminar_circulos_repetidos(self.circles)
                        for (x, y, r) in self.circles:                        
                            # se dibujan los circulos en la interfaz:
                            xCircle = x + self.XIROI 
                            yCircle = y + self.YIROI 
                            cv2.circle(self.frame, (xCircle, yCircle),
                                    radioProm, (0, 255, 0), 2)
                            id = self.obtener_id_bola(x,y)
                            if id != -1:
                                cv2.putText(self.frame, str(id),(xCircle,yCircle),cv2.FONT_HERSHEY_SIMPLEX, 2,(255,255,0),2)
                                                                
                                # Dibujo de los trapecios posibles y no posibles:
                                # if(self.poligonos is not None):
                                #     for poligono in self.poligonos:                            
                                #         #Dibujamos el trapecio en la imagen
                                #         cv2.polylines(self.frame, [poligono], isClosed=True, color=(0, 255, 0), thickness=2)
                                # if(self.poligonosImposibles is not None):
                                #     for poligono in self.poligonosImposibles:
                                #         cv2.polylines(self.frame, [poligono], isClosed=True, color=(0, 0, 255), thickness=2)
        
                            i+=1

                        if resaltarBola == True and self.bolaSeleccionada is not None:
                                (xs,ys,rs) = self.bolaSeleccionada
                                cv2.circle(self.frame, (xs, ys), rs + 5, (255, 0, 255), thickness=2)
                                self.algunaEstaSeleccionada = True

                        if resaltarBolaCorreccion == True and self.bolaSeleccionadaCorreccion is not None:
                                (xsc,ysc,rsc) = self.bolaSeleccionadaCorreccion
                                xsc = xsc + self.XIROI
                                ysc = ysc + self.YIROI
                                cv2.rectangle(self.frame, (xsc-r, ysc+r), (xsc +r, ysc - r), (0, 255, 255), thickness=2)

                        if(self.algunaEstaSeleccionada == False):
                            self.bolaSeleccionada = None
                            self.puntos_trayectoria_bola_blanca = None
                            self.puntos_trayectorias_bolas = None
                            self.puntos_trayectoria_bola_seleccionada = None
                            resaltarBola = False
                            self.botonVerSimulacion.setEnabled = False

                                    
                self.graficar_trayectorias()
                # detectar si hay movimiento de alguna bola:
                if self.frame_count % 7 == 0:
                    #print(f"movimiento: {self.hayMovimiento}")
                    global movimientoDetectado
    
                    if circles_prev is not None and self.circles is not None:
                        movimientoDetectado = False
                        index = 0
                        for (x, y, r) in self.circles:
                            for (prev_x, prev_y, prev_r) in circles_prev:
                                distance = math.sqrt((x - prev_x) ** 2 + (y - prev_y) ** 2)
                                if distance < minRadius/2:  # Umbral para considerar movimiento
                                    movimientoDetectado = False
                                    break
                                else:
                                    movimientoDetectado = True  
                            if(movimientoDetectado == True):
                                break             
                    else:
                        movimientoDetectado = False
                    if(self.circles is not None):
                        circles_prev= self.circles.copy()
                        circles_prev = self.circles
                self.hay_movimiento(movimientoDetectado)


                # Calcular los FPS
                global previous_time, frames_previos
                current_time = time.time()
                if current_time - previous_time >= 1:
                    fps_str = "{:.2f}".format(self.frame_count - frames_previos)
                    self.fpsText.setText(fps_str)
                    frames_previos = self.frame_count
                    previous_time = current_time

                frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.label.setPixmap(QPixmap.fromImage(q_image))            

                self.frame_count += 1

                self.hiloProyeccion.noHilo()
        except Exception as e:
            print("Error de bucle principal:" + str(e))

    async def getCircles(self):
        return self.circlesProyeccion
    
       
    #determina si las bolas se movieron durante el calculo de tiro posible:
    def cambiaron_bolas_previo_al_tiro(self, listaEtiquetadas, actuales):
        if(listaEtiquetadas == None):
            return False
        lista2_set = set(actuales)        
        encontrado = False
        if( len(lista2_set) != len(listaEtiquetadas)):
            return True
        for (x1,y1,r1), _, _ in listaEtiquetadas:
            for (x2,y2,r2) in lista2_set:
                if  math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) <= r1: 
                    encontrado = True
                    break
            if(encontrado == False):
                #Cambiaron bolas previo al tiro, por eso no se encontro la bola
                return True
            encontrado = False
        #Devolvemos false porque no cambiaron las bolas previo al tiro y todas fueron encontradas                         
        return False
    
    #transforma una velocidad de 0 a 320 a un valor de 0 a 100
    def convertir_velocidad(self, velocidad):
        global limite_velocidad
        factor = limite_velocidad * 1.4156
        convertido = (velocidad/factor)*100        
        return round(convertido,1)

    def graficar_trayectorias(self):
        self.hiloProyeccion.actualizar_trayectorias(self.puntos_trayectoria_bola_blanca, self.puntos_trayectorias_bolas)
        if(self.puntos_trayectoria_bola_blanca is not None):
            for i in range(len(self.puntos_trayectoria_bola_blanca)):
                if(i == len(self.puntos_trayectoria_bola_blanca) - 1):
                    if isinstance(self.puntos_trayectoria_bola_blanca[i], tuple):  
                        punto = int(self.puntos_trayectoria_bola_blanca[i][0]), int(self.puntos_trayectoria_bola_blanca[i][1])
                    else:
                        punto = self.puntos_trayectoria_bola_blanca[i].int_tuple
                    x,y = punto
                    x = x + self.XIROI
                    y = y + self.YIROI
                    cv2.circle(self.frame, (x,y), int(minRadius/2) , (0,255,0),thickness=-1)
                    break
                if isinstance(self.puntos_trayectoria_bola_blanca[i], tuple):
                    puntoa = int(self.puntos_trayectoria_bola_blanca[i][0]), int(self.puntos_trayectoria_bola_blanca[i][1])
                else:    
                    puntoa = self.puntos_trayectoria_bola_blanca[i].int_tuple
                if isinstance(self.puntos_trayectoria_bola_blanca[i+1], tuple):
                    puntob = int(self.puntos_trayectoria_bola_blanca[i+1][0]), int(self.puntos_trayectoria_bola_blanca[i+1][1])
                else:
                    puntob = self.puntos_trayectoria_bola_blanca[i+1].int_tuple
                xa,ya = puntoa
                xb,yb = puntob
                xa = xa + self.XIROI
                ya = ya + self.YIROI
                xb = xb + self.XIROI
                yb = yb + self.YIROI
                if i == 0:
                    cv2.line(self.frame,(xa,ya) , (xb,yb), (255,0,0), 2)
                else:
                    cv2.line(self.frame,(xa,ya) , (xb,yb), (0,255,0), 2)
        if(self.puntos_trayectoria_bola_seleccionada is not None):
            for i in range(len(self.puntos_trayectoria_bola_seleccionada)):
                if(i == len(self.puntos_trayectoria_bola_seleccionada) - 1):
                    if isinstance(self.puntos_trayectoria_bola_blanca[i], tuple):  
                        punto = int(self.puntos_trayectoria_bola_blanca[i][0]), int(self.puntos_trayectoria_bola_blanca[i][1])
                    else:
                        punto = self.puntos_trayectoria_bola_seleccionada[i].int_tuple
                    x,y = punto
                    x = x + self.XIROI
                    y = y + self.YIROI
                    cv2.circle(self.frame, (x,y), int(minRadius/2) , (255,0,0),thickness=-1)
                    break
                if isinstance(self.puntos_trayectoria_bola_blanca[i], tuple):
                    puntoa = int(self.puntos_trayectoria_bola_blanca[i][0]), int(self.puntos_trayectoria_bola_blanca[i][1])
                else:
                    puntoa = self.puntos_trayectoria_bola_seleccionada[i].int_tuple
                if isinstance(self.puntos_trayectoria_bola_blanca[i+1], tuple): 
                    puntob = int(self.puntos_trayectoria_bola_blanca[i+1][0]), int(self.puntos_trayectoria_bola_blanca[i+1][1])
                else:
                    puntob = self.puntos_trayectoria_bola_seleccionada[i+1].int_tuple
                xa,ya = puntoa
                xb,yb = puntob
                xa = xa + self.XIROI
                ya = ya + self.YIROI
                xb = xb + self.XIROI
                yb = yb + self.YIROI
                cv2.line(self.frame, (xa,ya),(xb,yb), (255,0,0), 2)
        if(self.VerTodasTrayectorias):
            if(self.puntos_trayectorias_bolas is not None):
                for i in range(len(self.puntos_trayectorias_bolas)):
                    listaBola = self.puntos_trayectorias_bolas[i] 
                    if(len(listaBola)>0):
                        for x in range(len(listaBola)):
                            if(x == len(listaBola)-1):
                                if isinstance(listaBola[x], tuple):
                                    punto = int(listaBola[x][0]), int(listaBola[x][1])
                                else:
                                    punto = listaBola[x].int_tuple
                                x,y = punto
                                x = x + self.XIROI
                                y = y + self.YIROI
                                cv2.circle(self.frame, (x,y), int(minRadius/2) , (0,0,255),thickness=-1)
                                break
                            if isinstance(listaBola[x], tuple):
                                puntoa = int(listaBola[x][0]), int(listaBola[x][1])
                            else:
                                puntoa = listaBola[x].int_tuple
                            if isinstance(listaBola[x+1], tuple):
                                puntob = int(listaBola[x+1][0]), int(listaBola[x+1][1])
                            else:
                                puntob = listaBola[x+1].int_tuple
                            xa,ya = puntoa
                            xb,yb = puntob
                            xa = xa + self.XIROI
                            ya = ya + self.YIROI
                            xb = xb + self.XIROI
                            yb = yb + self.YIROI
                            cv2.line(self.frame, (xa,ya),(xb,yb), (0,0,255), 2)

    #determina si el usuario selecciono la bola blanca para embocar:
    def selecciono_la_blanca(self, listaEtiquetadas):
        if(listaEtiquetadas == None):
             return False
        if (self.bolaSeleccionada is not None):
            (xs, ys, rs) = self.bolaSeleccionada
            for(x1,y1,r1), _, etiqueta in listaEtiquetadas:
                x1=x1+self.XIROI
                y1=y1+self.YIROI
                if math.sqrt((x1-xs)**2 + (y1-ys)**2) <= rs:
                    if(etiqueta == "Blanca"):
                        return True
        return False
    
    def obtenerBolaBlanca(self, listaEtiquetadas):
        for(x1,y1,r1), _, etiqueta in listaEtiquetadas:
            bola = (x1,y1,r1) 
            x1=x1+self.XIROI
            y1=y1+self.YIROI
            if(etiqueta == "Blanca"):
                return bola
        return None

    def existe_la_negra(self, listaEtiquetada):
        if(listaEtiquetada == None):
             return False
        for(x,y,r), _ ,etiqueta in listaEtiquetada:
            if etiqueta == "Negra":
                return True
        return False
    
    def hay_bola_blanca(self, listaEtiquetada):
        if(listaEtiquetada == None):
            return False
        blancas = 0
        for(x,y,r), _, etiqueta in listaEtiquetada:
            if etiqueta == "Blanca":
                blancas = blancas + 1
        return blancas!=0

    def solo_una_blanca(self, listaEtiquetada):
        if(listaEtiquetada == None):
            return False
        blancas = 0
        for(x,y,r), _, etiqueta in listaEtiquetada:
            if etiqueta == "Blanca":
                blancas = blancas + 1
        return blancas==1
    
    def solo_una_negra(self, listaEtiquetada):
        if(listaEtiquetada == None):
            return False
        negras = 0
        for(x,y,r), _, etiqueta in listaEtiquetada:
            if etiqueta == "Negra":
                negras = negras + 1
        return negras==1

    def maximo_rayadas_superado(self, listaEtiquetada):
        if(listaEtiquetada == None):
            return False
        rayadas = 0
        for (x,y,r), _, etiqueta in listaEtiquetada:
            if etiqueta == "Rayada":
                rayadas = rayadas + 1
        return rayadas > 7

    
    def maximo_lisas_superado(self, listaEtiquetada):
        if(listaEtiquetada == None):
            return False
        lisas = 0
        for (x,y,r), _, etiqueta in listaEtiquetada:
            if etiqueta == "Lisa":
                lisas = lisas + 1
        return lisas > 7
    
    def selecciono_negra(self, listaEtiquetada, seleccionada):
        if seleccionada is not None:
            x,y,_ = seleccionada
            etiquetaSeleccionada = ""
            for (x1,y1,r1), _, etiqueta in listaEtiquetada:
                x1 = x1 + self.XIROI
                y1 = y1 + self.YIROI
                if (x1 == x and y1 == y):
                    etiquetaSeleccionada = etiqueta
                    break
            if etiquetaSeleccionada == "Negra":
                return True
            return False
        return False

        
    def seleccion_de_negra_incorrecto(self, listaEtiquetada, seleccionada):
       if seleccionada is not None:
            x,y,_ = seleccionada
            etiquetaSeleccionada = ""
            lisas = 0
            rayadas = 0 
            for (x1,y1,r1), _, etiqueta in listaEtiquetada:
                x1 = x1 + self.XIROI
                y1 = y1 + self.YIROI
                if etiqueta == "Lisa":
                    lisas = lisas +1
                elif etiqueta == "Rayada":
                    rayadas = rayadas +1 
                if (x1 == x and y1 == y):
                    etiquetaSeleccionada = etiqueta
            if etiquetaSeleccionada != "Negra":
                return False
            if rayadas != 0 and lisas != 0:
                    return True
       return False
           
           

    
    def distancia_puntos(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def obtener_tam_ROI(self):
        d1 = self.distancia_puntos(self.XIROI, self.YIROI, self.XDROI, self.YIROI)
        d2 = self.distancia_puntos(self.XDROI, self.YIROI, self.XDROI, self.YDROI)
        d3 = self.distancia_puntos(self.XDROI, self.YDROI, self.XIROI, self.YDROI)
        d4 = self.distancia_puntos(self.XIROI, self.YDROI, self.XIROI, self.YIROI)
        ancho = max(d1,d3)
        alto = max(d2,d4)
        return ancho, alto 

    def printUI(self, text):
        text = f"<p style='color: green; font-size: 20px'> {text} </p>"
        self.textBrowser.setText(text)
    
    def printUIError(self, text):
        text = f"<p style='color: red; font-size: 20px'> {text} </p>"
        self.textBrowser.setText(text)
    
    def reiniciarProgressBar(self):
        self.progressBar.setValue(0)
        self.contadorProgressBar = 0 
        self.valorProgressBar = 0

    def avanzarProgressBar(self, valorMaximo):
        if  self.valorProgressBar == valorMaximo:
            return
        
        self.contadorProgressBar += 1
        if (self.contadorProgressBar % 2 == 0):
            return
    
        self.valorProgressBar += 1
        self.progressBar.setValue(self.valorProgressBar)

resXProy = 1920
resYProy = 1080

#levanta archivo de configuracion antes de iniciar todo:
def levantar_configuracion():
    global computo
    path = script_dir + "\\configuracion.json"
    with open(path) as f:
        data = json.load(f)
    computo = data["computo"]
    print(f"computo: {computo}")


#deprecated:
class Bola:
    contador = 0  # Variable de clase para el ID autoincremental
    
    def __init__(self, x, y, r):
        Bola.contador += 1
        self.id = Bola.contador
        self.x = x
        self.y = y
        self.r = r
    
    def actualizar_posicion(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

if __name__ == "__main__":
    app = QApplication(sys.argv)

    levantar_configuracion()
    if (computo == "GPU"):
        iniciar_GPU()
    ventanaProyeccion = VentanaProyeccion()
    ventanaParametros = ControlWindow()
    ventanaContrasena = VentanaContrasena(ventanaParametros)
    ventanaPreprocesamiento = PreprocesamientoWindow()
    ventanaParametrosSimulacion = ParametrosSimulacionWindow()
    ventanaAyuda = AyudaWindow()
    hiloProyeccion = HiloProyeccion(bloqueo, ventanaProyeccion)
    ventana = VentanaVideo(ventanaProyeccion, ventanaParametros, hiloProyeccion, ventanaPreprocesamiento, ventanaParametrosSimulacion,ventanaContrasena, ventanaAyuda)

    ventana.show()
    ventana.controlWindow.show()

    sys.exit(app.exec_())
