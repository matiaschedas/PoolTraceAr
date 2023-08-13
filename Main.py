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
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton, QCheckBox, QGridLayout, QWidget, QLineEdit, QVBoxLayout, QSplitter, QFileDialog, QDesktopWidget
from PyQt5.QtGui import QImage, QPixmap, QIcon, QWindow, QScreen, QGuiApplication
from PyQt5.QtCore import Qt, QTimer, QEvent
from HiloEtiquetador import ListaApareadaConEtiquetas, variable_compartida_lock
from HiloEtiquetador import Etiquetar
from Clases.ControlWindow import ControlWindow
from Clases.PreprocesamientoWindow import PreprocesamientoWindow
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

from Clases.Fisicas import Fisicas

screen_width, screen_height = pyautogui.size()

computo = None
anguloRotar = 0
ResolucionX = 1280
ResolucionY = 720
resoluciones = [(426, 240), (640, 360), (800, 450), (896, 504), (912, 513), (928, 522), (960, 540), (1024, 576), (1152, 648),
                (1200, 675), (1248, 702), (1280, 720), (1440, 810), (1520, 855), (1560, 877), (1584, 891), (1600, 900), (1680, 945), (1920, 1080)]
radios       = [(4, 5), (5, 6), (6, 7), (7, 8),
          (8, 9), (9, 10), (10, 11), (11, 12),(12,13),(13,14),(14,15),(15,16),(16,17),(17,18),(18,19),(19,20),(20,21),(21,22),(22,23)]
radioMin = 4
radioMax = 16
tamPanelBotones = 70
Param1 = 50
Param2 = 50
cerrarProyeccion = False
proyectando = False
script_dir = os.path.dirname(os.path.abspath(__file__))
display_monitor = 1

circles_prev = None
movimientoDetectado = False
bolaSeleccionada = None
resaltarBola = False

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
    hiloProyeccion.start()


def pararHilos():
    
    hiloProyeccion.detener_hilo()


def parar_de_actualizar(self):
    self.seguirActualizando = False


# Obtener el identificador de la ventana de PyQt5


def get_win_id(window):
    if sys.platform == 'win32':
        return window.winId()
    return None

# Configurar el estilo de la ventana para mostrar el botón de maximizar de Windows
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

        
        self.nroMonitor = display_monitor

        monitor = QDesktopWidget().screenGeometry(self.nroMonitor)
        self.move(monitor.left(), monitor.top())

        self.label.setGeometry(0, 0, 1920, 1080)
        self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.frame = np.zeros((resXProy, resYProy, 3), dtype=np.uint8)
        self.frame = cv2.resize(
            self.frame, (resYProy, resXProy), interpolation=cv2.INTER_LINEAR)
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

    def set_nroMonitor(self, numero):
        self.nroMonitor = numero
        monitor = QDesktopWidget().screenGeometry(self.nroMonitor)
        self.move(monitor.left() + 7, monitor.top())

    def dibujar_circulos(self, x, y, r, color, grosor):
            cv2.circle(self.frame, (x, y), r, color, grosor)

    def re_init_frame(self, h, w):
        self.frame = self.frame.copy()
        self.frame = cv2.resize(
            self.frame, (w, h), interpolation=cv2.INTER_LINEAR)

    def dibujar(self):
        self.frame = cv2.resize(
            self.frame, (resYProy, resXProy), interpolation=cv2.INTER_LINEAR)
        frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        imagen = QImage(frame_rgb.data, resYProy,
                        resXProy, QImage.Format_RGB888)
        imagen = QPixmap.fromImage(imagen)
        self.label.setPixmap(imagen)

    def limpiar_circulos(self):
        self.frame = np.zeros((resXProy, resYProy, 3), dtype=np.uint8)


class HiloProyeccion(threading.Thread):
    def __init__(self, bloqueo, ventanaProyeccion: VentanaProyeccion):
        super().__init__()
        self.detener = False
        self.bloqueo = bloqueo
        self.hora_inicio = datetime.now()
        self.ventanaProyeccion = ventanaProyeccion
        self.actualizar_interfaz = False
        self.circles = None
        self.height = None
        self.width = None
        

    def run(self):
        while not self.detener:
            time.sleep(0.0167)
            # limpiar ventana de proyeccion:
            self.ventanaProyeccion.limpiar_circulos()
            if self.circles is not None and self.height is not None and self.width is not None:
                self.ventanaProyeccion.re_init_frame(self.height, self.width)
                global minRadius, maxRadius
                radioProm = int((minRadius+maxRadius)/2)
                for (x, y, r) in self.circles:
                    # se dibujan los circulos en la interfaz: 
                    self.ventanaProyeccion.dibujar_circulos(
                        x + self.xiroi, y + self.yiroi, radioProm, (0, 255, 0), 2)
            self.ventanaProyeccion.dibujar()
            if self.detener:
                break

    def actualizar_circles(self, circles):
        self.circles = circles

    def actualizar_proporcion_interfaz(self, height, width):
        self.height = height
        self.width = width

    def actualizar_roi(self, xiroi, yiroi):
        self.xiroi = xiroi
        self.yiroi = yiroi

    def detener_hilo(self):
        with self.bloqueo:
            self.detener = True


class VentanaVideo(QMainWindow):
    def __init__(self, ventanaProyeccion: VentanaProyeccion, ventanaParametros: ControlWindow, hiloProyeccion: HiloProyeccion, ventanaPreprocesamiento: PreprocesamientoWindow):
        super().__init__()
        global script_dir 

        self.roi = None
        self.hiloEtiquetador = None
        self.etiquetar = False
        self.etiquetando = False

        self.hiloProyeccion = hiloProyeccion
        self.setMaximumSize(screen_width, screen_height)
        self.resize(ResolucionX, ResolucionY)
        self.setWindowTitle("PoolTraceAR")
        self.ventanaPrepro = ventanaPreprocesamiento
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
        self.hiloProyeccion.actualizar_roi(xiroi=self.XIROI, yiroi=self.YIROI)
        self.moverVertices = False
        self.verticeSeleccionado = None
        self.inicio = True
        self.creandoROI = False
        self.cargarCoordenadas = True
      
        # endregion

        # region coordenadas de huecos(troneras):
        self.troneras =[(0, 0),(0, 0),(0, 0),(0, 0),(0, 0),(0, 0)]
        self.troneras_labels = ["T1", "T2", "T3", "T4", "T5", "T6"]
        self.radioTronera = int(radioMax)+3
        self.selected_tronera = None
        # endregion

        # region Parametros de reglas de juego
        self.BolaEnMano = False
        self.Hay2Tiros = False
        self.hayMesaAbierta = False
        self.hayMovimiento = False
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

        #region creacion de interfaz
        self.botonProyectar, self.botonROI, self.botonPreprocesamientos, self.botonGuardarPreset, self.botonCargarPreset, self.botonSetearIDS = ventanaParametros.obtenerBotones()
        self.comboCamaras = ventanaParametros.obtenerComboCamaras()
        self.comboMonitores = ventanaParametros.obtenerComboMonitores()
        #self.labelCamara = self.crear_label("Camara:", 1290, 5, 50, 30)
        #self.comboCamaras = self.crear_combobox(webcams, 1290, 35, 100, 30, 0)

        self.botonConfiguracion = self.crear_boton("Configuracion", 1290, 125, 100, 30)
        self.fpsText = QLineEdit(self)
        self.fpsText.setReadOnly(True)
        self.labelFps = self.crear_label("FPS: ", 5, 820, 100, 25)
        self.labelFps.setAlignment(Qt.AlignCenter)

        self.botonConfiguracion.clicked.connect(self.configurar)
        self.botonProyectar.clicked.connect(self.proyectar)
        self.comboCamaras.currentIndexChanged.connect(self.cambio_camara)
        self.comboMonitores.currentIndexChanged.connect(self.cambio_monitor)
        self.botonROI.clicked.connect(self.crear_ROI)
        self.botonPreprocesamientos.clicked.connect(self.abrir_preprocesamiento)

        self.labelBolaEnMano = self.crear_label("Bola en mano: ", 5, 820, 100, 25)
        self.label2Tiros = self.crear_label("2 Tiros: ", 5,820,100,25)
        self.labelMesaAbierta = self.crear_label("Mesa abierta: ", 5, 820, 100, 25)
        self.checkBolaEnMano = self.crear_checkbox(80, 820, 50, 30)
        self.checkBolaEnMano.stateChanged.connect(self.bola_en_mano)
        self.check2Tiros = self.crear_checkbox(80,820,50,30)
        self.check2Tiros.stateChanged.connect(self.dos_tiros)
        self.checkMesaAbierta = self.crear_checkbox(80,820,50,30)
        self.checkMesaAbierta.stateChanged.connect(self.mesa_abierta)
        self.botonSetearIDS.clicked.connect(self.SetearIDS)

        self.botonGuardarPreset.clicked.connect(self.guardar_preset)
        self.botonCargarPreset.clicked.connect(self.cargar_preset)
        # endregion

        # Crear el widget principal y asignarle un layout vertical
        widgetPrincipal = QWidget()
        layoutPrincipal = QVBoxLayout()
        widgetPrincipal.setLayout(layoutPrincipal)
        layoutPrincipal.setContentsMargins(0, 0, 0, 0)

        # Crear el widget1 y asignarle el layout1 como QGridLayout
        self.widget1 = QWidget()
        self.layout1 = QGridLayout(self.widget1)
        self.layout1.setContentsMargins(0, 0, 0, 0)
        self.layout1.setSpacing(0)  # Opcional: eliminar el espacio entre los widgets

        # Crear el widget2 y asignarle el layout2
        self.widget2 = QWidget()
        self.layout2 = QGridLayout(self.widget2)
        self.layout2.setContentsMargins(0, 0, 0, 0)
        self.widget2.setFixedHeight(tamPanelBotones)

        self.fpsText.setMaximumWidth(50)
        self.botonConfiguracion.setMaximumWidth(100)  # Ancho fijo
        self.layout2.setSpacing(0)

        # Agregar los widgets al layout principal
        layoutPrincipal.addWidget(self.widget1)
        layoutPrincipal.addWidget(self.widget2)

        # Agregar los widgets al layout1 y layout2 con sus respectivas posiciones
        self.layout1.addWidget(self.label, 0, 0, 1, 1, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.layout2.addWidget(self.botonConfiguracion, 1, 0)
        self.layout2.addWidget(self.labelBolaEnMano, 2, 0)
        self.layout2.addWidget(self.label2Tiros,2,1)
        self.layout2.addWidget(self.labelMesaAbierta, 2 ,2)
        self.layout2.addWidget(self.checkBolaEnMano, 3, 0)
        self.layout2.addWidget(self.check2Tiros,3,1)
        self.layout2.addWidget(self.checkMesaAbierta, 3, 2)

        # Agregar el contador de FPS con alineación a la esquina inferior derecha
        self.layout2.addWidget(self.labelFps, 3, 10)
        self.layout2.addWidget(self.fpsText, 3, 11, Qt.AlignBottom | Qt.AlignRight)

        self.setCentralWidget(widgetPrincipal)
        
        #componenetes de la ventana de preprocesamiento
        self.ventanaPrepro.view_frame_button.clicked.connect(self.ver_frame)
        self.ventanaPrepro.alphaChanged.connect(self.onAlphaChanged)
        self.ventanaPrepro.betaChanged.connect(self.onBetaChanged)
        self.ventanaPrepro.blurChanged.connect(self.onBlurChanged)
        

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
        inicioHilos()
        self.initCameras()

    def initCameras(self):
        self.cambio_camara(self.current_camera_index)  # Llamar al método para mostrar la primera cámara

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_video)
        self.timer.start(16)  # 30 ms (30 FPS)

    def SetearIDS(self):
        global setearIDS
        setearIDS=True
        print(f"Setear IDS {setearIDS}")

    def es_nombre_archivo_valido(self, texto):
        patron = r"^(?!^(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$)[^\x00-\x1f\\?*:\";|/<>]+$"
        coincide = re.match(patron, texto, re.IGNORECASE)
        return coincide is not None
    
    def guardar_preset(self):
        global dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles
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
            }
            with open(path, "w") as archivo:
                json.dump(datos, archivo)

    def cargar_preset(self):
        global dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles
        campos = ['dp','minDist','cannyThreshold','votesThreshold','minRadius','maxRadius','maxCircles']
        valido = False
        file_dialog = QFileDialog()

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        file_path, _ = file_dialog.getOpenFileName(None, "Seleccionar archivo", "", "Todos los archivos (*.*)", options=options)
            
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
            self.controlWindow.actualizarParametros(
            dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles)
           
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

    def ver_frame(self):
        global mostrarFrameRaw
        if mostrarFrameRaw  == True:
            mostrarFrameRaw = False
            if cv2.getWindowProperty("Frame", cv2.WND_PROP_VISIBLE) > 0:
                cv2.destroyWindow("Frame")
        else:
            mostrarFrameRaw = True

    def actualizarHough(self):
        global hough, dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles, computo
        self.controlWindow.actualizarParametros(
            dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles)
        print(f"dp: {dp}, minDist: {minDist}, cannyThreshold: {cannyThreshold}, votesThreshold: {votesThreshold}, minRadius: {minRadius}, maxRadius: {maxRadius}, maxCircles: {maxCircles}")
        try:
            if (computo == "GPU"):
                hough = cv2.cuda.createHoughCirclesDetector(
                    dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles)
        except cv2.error as e:
            pass

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

    def onAnguloChanged(self, anguloNew):
        global anguloRotar
        anguloRotar = anguloNew

    def onRadioTroneraChanged(self, radioTroneraNew):
        global anguloRotar
        self.radioTronera = radioTroneraNew    

    def init_ui(self):
        # Configurar la ventana para mostrar el botón de maximizar de Windows
        enable_maximize_button(self)

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

    def encontrar_radio(self, resolucion_encontrada):
        global resoluciones, radios
        indiceResolucion = resoluciones.index(resolucion_encontrada)
        
        indice_radio = indiceResolucion
        radio = radios[indice_radio]
        return radio

    def on_resize_timeout(self):
        # Código a ejecutar cuando finaliza el evento de redimensionamiento
        print("Final del evento de redimensionamiento")
        global ResolucionX, ResolucionY, resoluciones, radioMax, radioMin, computo
        resolucion_encontrada = self.encontrar_resolucion(
            resoluciones, ResolucionX, ResolucionY)
        ResolucionX = resolucion_encontrada[0]
        ResolucionY = resolucion_encontrada[1]
        if self.frame is not None:
            self.frame = cv2.resize(
                self.frame, (ResolucionX, ResolucionY), interpolation=cv2.INTER_LINEAR)
            ventanaProyeccion.frame = cv2.resize(
                ventanaProyeccion.frame, (resYProy, resXProy), interpolation=cv2.INTER_LINEAR)
        self.XIROI, self.YIROI = 10, 10
        self.XDROI, self.YDROI = ResolucionY - \
            int(ResolucionY/2), ResolucionY-int(ResolucionY/2)
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
        self.hiloProyeccion.actualizar_roi(xiroi=self.XIROI, yiroi=self.YIROI)

        self.hiloProyeccion.actualizar_proporcion_interfaz(
            ResolucionY, ResolucionX)

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
        except Exception as ex:
            self.frame = None
            self.cap = None
            print("Error", ex)

    def cambio_monitor(self, index):
        global display_monitor
        opcion = self.comboMonitores.itemText(index)
        print(f"monitor: {opcion}")
        numero = int(re.search(r'\d+', opcion).group())
        display_monitor = numero
        self.ventanaProyeccion.set_nroMonitor(display_monitor)

    def distancia_media_entre_puntos(self, x1, x2):
        distancia = (x2 - x1)
        return math.floor(distancia/2)

    def proyectar(self):
        global proyectando, cerrarProyeccion
        self.cambio_monitor(display_monitor-1)
        if(proyectando==False):
            proyectando = True
            self.ventanaProyeccion.show()
            cerrarProyeccion=False
        else:
            proyectando=False
            cerrarProyeccion = True
            ventanaProyeccion.close()
        

    def configurar(self):
        self.controlWindow.show()

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
        event.accept()

    def bola_en_mano(self):
        estado_actual = self.checkBolaEnMano.isChecked()
        if estado_actual == True:
            self.BolaEnMano = True
            print("Hay bola en mano")
        else:
            self.BolaEnMano = False
            print("No hay bola en mano")

    def dos_tiros(self):
        estado_actual = self.check2Tiros.isChecked()
        if estado_actual == True:
            self.Hay2Tiros = True
            print("Hay 2 tiros")
        else:
            self.Hay2Tiros = False
            print("No hay 2 tiros")

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

    def mousePressEvent(self, event):
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

        if self.moverVertices == False and self.etiquetando==False:
            global bolaSeleccionada
            if self.circles is not None:
                for (x, y, r) in self.circles:
                    x = (x+self.XIROI)
                    y = (y+self.YIROI)
                    distancia = np.sqrt( (event.x()-x)**2 + (event.y()- y)**2)
                    if distancia <=10:
                        print(f"bola {x},{y}")
                        clickEnBola = True
                        bolaSeleccionada=(x,y,r)
                        self.resaltar_bola_seleccionada()
                        self.etiquetar=True
                        self.tronerasPosibles = self.calcular_posibles_troneras()
        if (self.etiquetando==True):
            print("Espere por favor, se esta calculando el tiro")

        if clickEnBola == False and self.moverVertices == False and self.etiquetando==False:
            self.deseleccionar_bola()

    def resaltar_bola_seleccionada(self):
        global resaltarBola
        if bolaSeleccionada is not None:
            resaltarBola = True
            
    def deseleccionar_bola(self):
        global resaltarBola, bolaSeleccionada
        resaltarBola = False
        bolaSeleccionada = None

    def obtener_troneras(self):
            return self.troneras
    
    def distance_between_points(self, punto1, punto2):
        x1, y1 = punto1
        x2, y2 = punto2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

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

    def calcular_posibles_troneras(self):
        global bolaSeleccionada
        self.poligonos = []
        self.poligonosImposibles = []
        if bolaSeleccionada is None:
            return
        troneras = self.obtener_troneras()
        tronerasPosibles = []
        for tronera in troneras:
            (xb,yb,rb)=bolaSeleccionada
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


    def revisar_circulos(self,trapecio_vertices, circulos):
        trapecio_valido = True
        for circulo in circulos:
            x, y, radio = circulo
            x=x+self.XIROI
            y=y+self.YIROI
            distancia = math.sqrt((bolaSeleccionada[0]-x)**2 + (bolaSeleccionada[1]-y)**2)
            #se saltea a si misma (la seleccionada)
            if distancia < radio + 1:
                continue  
            centro_circulo = (x, y)
            print("Circulo :"+ str(centro_circulo) +" "+ str(self.esta_dentro_del_trapecio(trapecio_vertices,centro_circulo,radio)))
            print("Vertices de trapecio " + str(trapecio_vertices) )
            print("Radio: "+str(radio))
            
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

    def distancia_punto_a_linea(self,x, y, x1, y1, x2, y2):
        # Calcula la distancia entre el punto (x, y) y la línea definida por los puntos (x1, y1) y (x2, y2)
        return abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
    
    def mouseMoveEvent(self, event):
        if self.moverVertices and self.verticeSeleccionado is not None:
            print(f"moviendo vertice: {self.verticeSeleccionado}")
            # Actualizar la posición del vértice seleccionado según la posición del mouse
            if self.verticeSeleccionado == 0 and event.x() < self.XDROI-10 and event.y() < self.YDROI-10 and event.y() > 1 and event.x() > 1 and event.x() < ResolucionX and event.y() < ResolucionY:
                self.XIROI = event.x()
                self.YIROI = event.y()
            elif self.verticeSeleccionado == 1 and event.x() > self.XIROI+10 and event.y() > self.YIROI+10 and event.x() > 1 and event.y() > 1 and event.x() < ResolucionX and event.y() < ResolucionY:
                self.XDROI = event.x()
                self.YDROI = event.y()
            self.hiloProyeccion.actualizar_roi(xiroi=self.XIROI, yiroi=self.YIROI)
            self.actualizar_roi()
        if self.selected_tronera is not None:
            x, y = event.x(), event.y()
            self.troneras[self.selected_tronera] = (x, y)
            self.update()

    def mouseReleaseEvent(self, event):
        self.selected_tronera = None

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
    
    def abrir_preprocesamiento(self):
        self.ventanaPrepro.show()

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

    def agregar_o_actualizar_bola(self,x,y,r):
        global bolas
        actualizada = False
        encontrada = False
        for bola in bolas:
            distancia = math.sqrt((bola.x- x)**2 + (bola.y-y)**2)
            if distancia <= 30:
                bola.actualizar_posicion(x,y,r)
                actualizada = True
                break
        if actualizada==False:
            bolas.append(Bola(x,y,r))
        for bola in bolas:
            for (xd,yd,rd) in self.circles:
                distancia = math.sqrt((bola.x - xd)**2 + (bola.y - yd)**2)
                if distancia <= 30:
                    encontrada = True
                    break
            if encontrada == False:
                 bolas.remove(bola)
            encontrada = False

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
    def actualizar_video(self):
        global bolaSeleccionada, resaltarBola, minRadius, maxRadius
        if not self.seguirActualizando:
            return
        if self.cap is not None and not is_frame_black(self.frame):
            ret, self.frame = self.cap.read()
        else:
            ret = False
            width, height = ResolucionX, ResolucionY
            frame = frame = np.zeros((height, width, 3), dtype=np.uint8)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(q_image)) 
        if ret and not is_frame_black(self.frame):
            if self.inicio:
                self.XIROI, self.YIROI = 100, 100
                self.XDROI, self.YDROI = 150, 150
                self.inicio = False
                self.hiloProyeccion.actualizar_roi(
                    xiroi=self.XIROI, yiroi=self.YIROI)
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
                    print("etiquetando...")
                else:
                    print("fin de etiquetado")
                    self.etiquetar = False
                    self.etiquetando = False
                    with variable_compartida_lock:
                        listaEtiquetada = ListaApareadaConEtiquetas
                        bolaBlanca = self.obtenerBolaBlanca(listaEtiquetada)
                    
                    if( listaEtiquetada is not None ):
                        #si devuelve true, cambiaron de ubicacion las bolas -> no se puede continuar, caso contrario continuar
                        if( self.cambiaron_bolas_previo_al_tiro( listaEtiquetada , self.circles ) ):
                            print("Error, las bolas cambiaron de posicion.")
                            self.deseleccionar_bola()
                            listaEtiquetada.clear()
                            listaEtiquetada = None
                        if( self.selecciono_la_blanca(listaEtiquetada)):
                            print ("Error, se selecciono la bola blanca para embocar")
                            self.deseleccionar_bola()
                            listaEtiquetada.clear()
                            listaEtiquetada = None
                        if( self.existe_la_negra(listaEtiquetada)==False):
                            print("El jugador anterior emboco la bola negra, fin del partido")
                            self.deseleccionar_bola()
                            listaEtiquetada.clear()
                            listaEtiquetada = None
                        
                        if(listaEtiquetada is not None):
                            if bolaBlanca is not None:
                                (xb, yb, rb) = bolaBlanca
                                xb= xb + self.XIROI
                                yb= yb + self.YIROI
                                bolaBlanca = (xb,yb,rb)
                            
                            if (bolaBlanca is not None and bolaSeleccionada is not None):
                                tamROI = self.obtener_tam_ROI()
                                trayectoriasValidasBlanca = []
                                trayectoriasValidasSeleccionada = []
                                fisicas = Fisicas(True, True, False, listaEtiquetada, bolaSeleccionada, bolaBlanca, tamROI, self.XIROI, self.YIROI, self.troneras, self.radioTronera, maxRadius)
                                fisicas.setear_pasos_tiempo(5)
                                for i in range(2):
                                    #print(f"calculando {i+1} de 100...")
                                    #cuando hagamos algunos calculos tenemos que pasarle en vez de randoms algo mejor definido:
                                    #fisicas.setear_velocidad_inicial_blanca(random.randint(10,100),random.randint(10,100))
                                    fisicas.setear_velocidad_inicial_blanca(15,23)
                                    trayectoriasBlanca, trayectoriasSeleccionada, tiroValido, entroBlanca, entroSeleccionada, entroNegra = fisicas.simular()
                                    fisicas.reiniciar_simulacion()
                                    if(entroSeleccionada and entroNegra==False and entroBlanca== False and tiroValido):
                                        trayectoriasValidasBlanca.append(trayectoriasBlanca)
                                        trayectoriasValidasSeleccionada.append(trayectoriasSeleccionada)
                                print("fin calculo de trayectorias")
                                listaEtiquetada = None
                           

                    
                            

            if self.verROI:
                cv2.rectangle(self.frame, (self.XIROI, self.YIROI),
                              (self.XDROI, self.YDROI), (0, 255, 0), 2)
                # grafica los huecos (troneras):
                for tronera, label in zip(self.troneras, self.troneras_labels):
                    x, y = tronera
                    cv2.circle(self.frame, (x, y), self.radioTronera, (255, 255, 0), 2)
                    cv2.putText(self.frame, label, (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                

            if self.verVerticesROI:
                cv2.circle(self.frame, (self.XIROI, self.YIROI),int(radioMin/2), (0, 255, 0), 2)
                cv2.circle(self.frame, (self.XDROI, self.YDROI),int(radioMin/2), (0, 255, 0), 2)
            
            image = cv2.cvtColor(self.roi, cv2.COLOR_BGR2GRAY)
            image = self.aplicar_preprocesamientos(image)
           

            global Param1, Param2, hough
            # Cargar el fotograma actual en el objeto cv2.cuda_GpuMat
            if(computo == "GPU"):
                d_frame.upload(image)
                self.circles = hough.detect(d_frame)                
            elif (computo == "CPU"):
                self.circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, 15, param1=85, param2=11, minRadius=4, maxRadius=10)
            global circles_prev
           
            if self.circles is not None:
                if(computo == "GPU"):
                    self.circles = self.circles.download()
                if self.circles is not None:
                    self.circles = np.round(self.circles[0, :]).astype(int)
                    self.circlesProyeccion = self.circles
                    self.hiloProyeccion.actualizar_circles(self.circles.copy())

                    
                    radioProm = int((minRadius+maxRadius)/2)
                    algunaEstaSeleccionada = False

                    i=0
                   

                    self.circles  = self.eliminar_circulos_repetidos(self.circles)
                    for (x, y, r) in self.circles:
                        if(setearIDS):
                            self.agregar_o_actualizar_bola(x,y,r)
                        # se dibujan los circulos en la interfaz:
                        xCircle = x + self.XIROI 
                        yCircle = y + self.YIROI 
                        cv2.circle(self.frame, (xCircle, yCircle),
                                   radioProm, (0, 255, 0), 2)
                        id = self.obtener_id_bola(x,y)
                        if id != -1:
                            cv2.putText(self.frame, str(id),(xCircle,yCircle),cv2.FONT_HERSHEY_SIMPLEX, 2,(255,255,0),2)
                        if resaltarBola == True and bolaSeleccionada is not None:
                            (xs,ys,rs) = bolaSeleccionada
                            (xTronera, yTronera) = self.troneras[0]
                            dist = np.sqrt((xCircle-xs)**2 + (yCircle-ys)**2)
                            if dist <=10:
                                cv2.circle(self.frame, (xCircle, yCircle),
                                    radioProm+6, (0, 0, 255), 3)
                                algunaEstaSeleccionada = True
                            
                            # Dibujo de los trapecios posibles y no posibles:
                            if(self.poligonos is not None):
                                for poligono in self.poligonos:                            
                                    #Dibujamos el trapecio en la imagen
                                    cv2.polylines(self.frame, [poligono], isClosed=True, color=(0, 255, 0), thickness=2)
                            if(self.poligonosImposibles is not None):
                                for poligono in self.poligonosImposibles:
                                    cv2.polylines(self.frame, [poligono], isClosed=True, color=(0, 0, 255), thickness=2)

                            # #Dibujo de las troneras posibles: (esto esta bueno pero lagea)
                            # if self.tronerasPosibles is not None:
                            #     elapsed_time = time.time() - start_time
                            #     global alpha
                            #     frequency = 2.0 
                            #     amplitude = 0.5 
                            #     alpha = 0.5 + amplitude + np.sin(2 * np.pi * frequency * elapsed_time)

                            #     temp_frame = self.frame.copy()
                            #     for tronera in self.tronerasPosibles:
                            #         (xtp, ytp) = tronera
                            #         cv2.circle(temp_frame, (xtp,ytp), maxRadius, (0, 255, 0), -1)
                            #     cv2.addWeighted(temp_frame, alpha, self.frame, 1 - alpha, 0, self.frame)                   
                                
                        i+=1
                    if(algunaEstaSeleccionada == False):
                        bolaSeleccionada = None
                        resaltarBola = False

                                
                     
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

    async def getCircles(self):
        return self.circlesProyeccion
    
    def cambiaron_bolas_previo_al_tiro(self, listaEtiquetadas, actuales):
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

    def selecciono_la_blanca(self, listaEtiquetadas):
        if (bolaSeleccionada is not None):
            (xs, ys, rs) = bolaSeleccionada
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
        for(x,y,r), _ ,etiqueta in listaEtiquetada:
            if etiqueta == "Negra":
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

        

resXProy = 1080
resYProy = 1920

def levantar_configuracion():
    global computo
    path = script_dir + "\\configuracion.json"
    with open(path) as f:
        data = json.load(f)
    computo = data["computo"]
    print(f"computo: {computo}")

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
    ventanaPreprocesamiento = PreprocesamientoWindow()
    hiloProyeccion = HiloProyeccion(bloqueo, ventanaProyeccion)
    ventana = VentanaVideo(ventanaProyeccion, ventanaParametros, hiloProyeccion, ventanaPreprocesamiento)

    ventana.show()
    ventana.controlWindow.show()

    sys.exit(app.exec_())
