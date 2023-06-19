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
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton, QCheckBox, QGridLayout, QWidget, QLineEdit
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QEvent
from fchola import HiloEjemplo
from Clases.ControlWindow import ControlWindow
import win32con
import win32gui
import pyautogui

screen_width, screen_height = pyautogui.size()

ResolucionX = (int)(screen_width*0.8)
ResolucionY = (int)(screen_height*0.8)
resoluciones = [(426, 240), (640, 360), (800, 450), (896, 504), (912, 513), (928, 522), (960, 540), (1024, 576), (1136, 640),
                (1200, 675), (1248, 702), (1280, 720), (1440, 810), (1520, 855), (1560, 877), (1584, 891), (1600, 900), (1680, 945), (1920, 1080)]
radios = [(5, 9), (9, 12), (12, 15), (15, 19),
          (19, 22), (22, 25), (25, 28), (28, 31)]
radioMin = 4
radioMax = 16
tamPanelBotones = 140
Param1 = 50
Param2 = 50


circles_prev = None
movimientoDetectado = False

# bloqueo del hilo1 desde el main
bloqueo = threading.Lock()
hilo1 = HiloEjemplo(bloqueo)


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

hough = cv2.cuda.createHoughCirclesDetector(
    dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles)
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
    hilo1.detener_hilo()
    hiloProyeccion.detener_hilo()


def parar_de_actualizar(self):
    self.seguirActualizando = False


def obtener_webcams():
    webcams = []
    for index in range(10):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.isOpened():
            webcam_name = f"Webcam {index}"
            webcams.append(webcam_name)
            cap.release()
    return webcams

# Obtener el identificador de la ventana de PyQt5


def get_win_id(window):
    if sys.platform == 'win32':
        return window.winId()
    return None

# Configurar el estilo de la ventana para mostrar el botón de maximizar de Windows


def enable_maximize_button(window):
    if sys.platform == 'win32':
        hwnd = get_win_id(window)
        if hwnd:
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            win32gui.SetWindowLong(
                hwnd, win32con.GWL_STYLE, style | win32con.WS_MAXIMIZEBOX)


class VentanaProyeccion(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyeccion")
        self.label = QLabel(self)
        global resXProy, resYProy
        self.label.setGeometry(0, 0, 1920, 1080)
        self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.frame = np.zeros((resXProy, resYProy, 3), dtype=np.uint8)
        self.frame = cv2.resize(
            self.frame, (resYProy, resXProy), interpolation=cv2.INTER_LINEAR)
        self.resize(1920, 1080)

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
        self.hora_inicio = datetime.datetime.now()
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
                for (x, y, r) in self.circles:
                    # se dibujan los circulos en la interfaz:
                    self.ventanaProyeccion.dibujar_circulos(
                        x + self.xiroi, y + self.yiroi, r+3, (0, 255, 0), 2)
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
    def __init__(self, ventanaProyeccion: VentanaProyeccion, ventanaParametros: ControlWindow, hiloProyeccion: HiloProyeccion):
        super().__init__()
        self.hiloProyeccion = hiloProyeccion
        self.setMaximumSize(screen_width, screen_height)
        self.resize(ResolucionX, ResolucionY)
        self.setWindowTitle("PoolTraceAR")
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

        self.init_ui()
        self.circlesProyeccion = None

        webcams = obtener_webcams()
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
        self.tronera1 = [0, 0]
        self.tronera2 = [0, 0]
        self.tronera3 = [0, 0]
        self.tronera4 = [0, 0]
        self.tronera5 = [0, 0]
        self.tronera6 = [0, 0]
        # endregion

        # region Parametros de reglas de juego
        self.BolaEnMano = False
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

        # region creacion de interfaz
        self.labelCamara = self.crear_label("Camara:", 1290, 5, 50, 30)
        self.comboCamaras = self.crear_combobox(webcams, 1290, 35, 100, 30, 0)
        self.botonROI = self.crear_boton("Configurar ROI", 1290, 80, 100, 30)
        self.botonProyectar = self.crear_boton("Proyectar", 1290, 125, 100, 30)
        self.fpsText = QLineEdit(self)
        self.fpsText.setReadOnly(True)
        self.labelFps = self.crear_label("FPS: ", 5, 820, 100, 25)
        self.labelFps.setAlignment(Qt.AlignCenter)

        self.botonProyectar.clicked.connect(self.proyectar)
        self.comboCamaras.currentIndexChanged.connect(self.cambio_camara)
        self.botonROI.clicked.connect(self.crear_ROI)

        self.labelBolaEnMano = self.crear_label(
            "Bola en mano: ", 5, 820, 100, 25)
        self.checkBolaEnMano = self.crear_checkbox(80, 820, 50, 30)
        self.checkBolaEnMano.stateChanged.connect(self.bola_en_mano)

        # Layout:
        self.widget = QWidget()
        self.layout = QGridLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # configuracion de columnas:
        self.layout.setColumnStretch(0, 0)
        self.layout.setColumnStretch(1, 0)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 0)
        self.layout.setColumnStretch(4, 1)
        self.layout.setColumnStretch(10, 0)
        self.fpsText.setMaximumWidth(50)

        # nro fila, nro de col, cant filas, cant columnas
        self.layout.addWidget(self.label, 0, 0, 1, 3)
        self.layout.addWidget(self.labelCamara, 1, 0)
        self.layout.addWidget(self.comboCamaras, 2, 0)
        self.layout.addWidget(self.botonROI, 3, 0)
        self.layout.addWidget(self.botonProyectar, 3, 1)
        self.layout.addWidget(self.labelBolaEnMano, 4, 0)
        self.layout.addWidget(self.checkBolaEnMano, 5, 0)
        self.layout.addWidget(self.labelFps, 6, 4, 1, 10)
        self.layout.addWidget(self.fpsText, 6, 10, 1, 10)
        self.setCentralWidget(self.widget)
        # endregion
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.on_resize_timeout)
        inicioHilos()

        self.actualizar_video()

    def actualizarHough(self):
        global hough, dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles
        self.controlWindow.actualizarParametros(
            dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles)
        print(f"dp: {dp}, minDist: {minDist}, cannyThreshold: {cannyThreshold}, votesThreshold: {votesThreshold}, minRadius: {minRadius}, maxRadius: {maxRadius}, maxCircles: {maxCircles}")
        try:
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
        self.cap.release()
        global ResolucionX, ResolucionY
        ResolucionX = event.size().width()
        ResolucionY = event.size().height()

    def encontrar_resolucion(self, resoluciones, ResolucionX, ResolucionY):
        print(f"resX: {ResolucionX} resY: {ResolucionY}")
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
        n = 3  # proporcion entre la cantidad de resoluciones y radios
        indice_radio = indiceResolucion // n
        if indice_radio > len(radios):
            indice_radio = len(radios)
        radio = radios[indice_radio]
        return radio

    def on_resize_timeout(self):
        # Código a ejecutar cuando finaliza el evento de redimensionamiento
        print("Final del evento de redimensionamiento")
        global ResolucionX, ResolucionY, resoluciones, radioMax, radioMin
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

        self.actualizarHough()
        self.cambio_camara(self.comboCamaras.currentIndex())
        self.hiloProyeccion.actualizar_roi(xiroi=self.XIROI, yiroi=self.YIROI)

        self.hiloProyeccion.actualizar_proporcion_interfaz(
            ResolucionY, ResolucionX)

    def cambio_camara(self, index):
        opcion = self.comboCamaras.itemText(index)
        print(f"opcion seleccionada: {opcion}")
        numero = int(re.search(r'\d+', opcion).group())
        try:
            self.cap.release()
            self.cap = cv2.VideoCapture(numero, cv2.CAP_DSHOW)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ResolucionX)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ResolucionY)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.actualizar_video()
        except Exception as ex:
            print("Error")
            self.cap.release()

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
        self.ventanaProyeccion.close()
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
                distancia = np.sqrt(
                    (event.x() - vertice[0])**2 + (event.y() - vertice[1])**2)
                if distancia <= 10:  # Si la distancia es menor o igual a 10 píxeles, se considera seleccionado
                    self.verticeSeleccionado = i
                    self.moverVertices = True
                    break

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
            self.hiloProyeccion.actualizar_roi(
                xiroi=self.XIROI, yiroi=self.YIROI)

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

    def actualizar_video(self):
        if not self.seguirActualizando:
            return

        ret, self.frame = self.cap.read()
        if self.frame is not None:
            if self.inicio:
                self.XIROI, self.YIROI = 100, 100
                self.XDROI, self.YDROI = 150, 150
                self.inicio = False
                self.hiloProyeccion.actualizar_roi(
                    xiroi=self.XIROI, yiroi=self.YIROI)

            roi = self.frame[self.YIROI+5:self.YDROI -
                             5, self.XIROI+5:self.XDROI-5]
            if self.verROI:
                cv2.rectangle(self.frame, (self.XIROI, self.YIROI),
                              (self.XDROI, self.YDROI), (0, 255, 0), 2)
                # grafica los huecos (troneras):
                mitadMesa = self.distancia_media_entre_puntos(
                    self.XIROI, self.XDROI)
                radioTronera = int(radioMax)+3
                desplazamiento = int(math.sqrt(((radioTronera)**2)/2))
                troneras = [(self.XIROI-desplazamiento, self.YIROI-desplazamiento), (self.XDROI+desplazamiento, self.YDROI+desplazamiento), (self.XIROI-desplazamiento, self.YDROI+desplazamiento),
                            (self.XDROI+desplazamiento, self.YIROI-desplazamiento), (self.XIROI+mitadMesa, self.YIROI-desplazamiento), (self.XIROI+mitadMesa, self.YDROI+desplazamiento)]
                self.tronera2 = (self.XDROI+desplazamiento,
                                 self.YDROI+desplazamiento)
                self.tronera3 = (self.XIROI-desplazamiento,
                                 self.YDROI+desplazamiento)
                self.tronera4 = (self.XDROI+desplazamiento,
                                 self.YIROI-desplazamiento)
                self.tronera5 = (self.XIROI+mitadMesa,
                                 self.YIROI-desplazamiento)
                self.tronera6 = (self.XIROI+mitadMesa,
                                 self.YDROI+desplazamiento)
                for tronera in troneras:
                    cv2.circle(self.frame, tronera,
                               radioTronera, (255, 255, 0), 2)

            if self.verVerticesROI:
                cv2.circle(self.frame, (self.XIROI, self.YIROI),
                           8, (0, 255, 0), 2)
                cv2.circle(self.frame, (self.XDROI, self.YDROI),
                           8, (0, 255, 0), 2)

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            global Param1, Param2
            # Cargar el fotograma actual en el objeto cv2.cuda_GpuMat
            d_frame.upload(blur)
            global hough
            self.circles = hough.detect(d_frame)
            global circles_prev
            if self.circles is not None:
                self.circles = self.circles.download()
                if self.circles is not None:
                    self.circles = np.round(self.circles[0, :]).astype(int)
                    self.circlesProyeccion = self.circles
                    self.hiloProyeccion.actualizar_circles(self.circles.copy())
                    for (x, y, r) in self.circles:
                        # se dibujan los circulos en la interfaz:
                        xCircle = x + self.XIROI + 3
                        yCircle = y + self.YIROI + 3
                        cv2.circle(self.frame, (xCircle, yCircle),
                                   r+5, (0, 255, 0), 1)
                        # self.ventanaProyeccion.dibujar_circulos(
                        #     xCircle, yCircle, r, (0, 255, 0), 1)

            # self.ventanaProyeccion.dibujar()
            # detectar si hay movimiento de alguna bola:
            if self.frame_count % 4 == 0:
                # print(f"movimiento: {self.hayMovimiento}")
                global movimientoDetectado
                if circles_prev is not None and self.circles is not None:
                    movimientoDetectado = False
                    index = 0
                    for (x, y, r) in self.circles:
                        for (prev_x, prev_y, prev_r) in circles_prev:
                            distance = math.sqrt(
                                (x - prev_x) ** 2 + (y - prev_y) ** 2)
                            if distance < 6:  # Umbral para considerar movimiento
                                movimientoDetectado = False
                                break
                            else:
                                movimientoDetectado = True
                else:
                    movimientoDetectado = False
                circles_prev = self.circles

            self.hay_movimiento(movimientoDetectado)

            tiempo_actual = time.time()
            tiempo_transcurrido = tiempo_actual - self.tiempo_inicio

            # Calcular los FPS
            global previous_time, frames_previos
            current_time = time.time()
            if current_time - previous_time >= 1:
                fps_str = "{:.2f}".format(self.frame_count - frames_previos)
                self.fpsText.setText(fps_str)
                frames_previos = self.frame_count
                previous_time = current_time

            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            imagen = QImage(
                frame_rgb.data, frame_rgb.shape[1], frame_rgb.shape[0], QImage.Format_RGB888)
            imagen = QPixmap.fromImage(imagen)
            self.label.setPixmap(imagen)

            self.frame_count += 1
            # Establecer el tiempo de espera en base a los fps del video
            tiempo_espera = 1
            QTimer.singleShot(tiempo_espera, self.actualizar_video)

    async def getCircles(self):
        return self.circlesProyeccion


resXProy = 1080
resYProy = 1920

if __name__ == "__main__":
    app = QApplication(sys.argv)

    ventanaProyeccion = VentanaProyeccion()
    ventanaParametros = ControlWindow()
    hiloProyeccion = HiloProyeccion(bloqueo, ventanaProyeccion)
    ventana = VentanaVideo(
        ventanaProyeccion, ventanaParametros, hiloProyeccion)

    ventana.show()
    ventana.controlWindow.show()

    sys.exit(app.exec_())
