from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QSlider, QLineEdit, QLabel, QGridLayout, QPushButton, QCheckBox, QComboBox, QApplication
import cv2
import os
import sys
import ctypes


script_dir = os.path.dirname(os.path.abspath(__file__))

def obtener_webcams():
        webcams = []
        for index in range(10):
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if cap.isOpened():
                webcam_name = f"Webcam {index}"
                webcams.append(webcam_name)
                cap.release()
        return webcams



def obtener_numeros_monitores_conectados():
    num_monitores = ctypes.windll.user32.GetSystemMetrics(80)  # 80 es el código para SM_CMONITORS
    numeros_monitores = ["Monitor " + str(i + 1) for i in range(num_monitores)]
    return numeros_monitores


class ControlWindow(QMainWindow):
    dpChanged = pyqtSignal(int)
    minDistChanged = pyqtSignal(int)
    cannyThresholdChanged = pyqtSignal(int)
    votesThresholdChanged = pyqtSignal(int)
    minRadiusChanged = pyqtSignal(int)
    maxRadiusChanged = pyqtSignal(int)
    maxCirclesChanged = pyqtSignal(int)
    botonProyectar = None
    botonConfigurarROI = None
    botonPreprocesamientos = None
    comboCamaras = None

    def __init__(self, parent=None):
        super().__init__(parent)
        global script_dir 

        self.setWindowTitle("Ajuste de parámetros")
        self.setGeometry(100, 100, 400, 300)

        self.dp = 1
        self.minDist = 25
        self.cannyThreshold = 10
        self.votesThreshold = 10
        self.minRadius = 14
        self.maxRadius = 16
        self.maxCircles = 100

        
        icon_path = os.path.join(script_dir, "config.png")
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)

        self.initUI()

    def initUI(self):
        layout = QGridLayout()

        dp_label = QLabel("dp")
        self.dp_slider = QSlider(Qt.Horizontal)
        self.dp_slider.setRange(1, 10)
        self.dp_slider.setValue(self.dp)
        self.dp_slider.valueChanged.connect(self.onDpSliderChange)
        self.dp_text = QLineEdit()
        self.dp_text.setValidator(QIntValidator())
        self.dp_text.setText(str(self.dp))
        self.dp_text.textChanged.connect(self.onDpTextChange)
        self.dp_text.setFixedWidth(30)
        layout.addWidget(dp_label, 0, 0)
        layout.addWidget(self.dp_slider, 0, 1)
        layout.addWidget(self.dp_text, 0, 2)

        minDist_label = QLabel("minDist")
        self.minDist_slider = QSlider(Qt.Horizontal)
        self.minDist_slider.setRange(1, 50)
        self.minDist_slider.setValue(self.minDist)
        self.minDist_slider.valueChanged.connect(self.onMinDistSliderChange)
        self.minDist_text = QLineEdit()
        self.minDist_text.setValidator(QIntValidator())
        self.minDist_text.setText(str(self.minDist))
        self.minDist_text.textChanged.connect(self.onMinDistTextChange)
        self.minDist_text.setFixedWidth(30)
        layout.addWidget(minDist_label, 1, 0)
        layout.addWidget(self.minDist_slider, 1, 1)
        layout.addWidget(self.minDist_text, 1, 2)

        cannyThreshold_label = QLabel("cannyThreshold")
        self.cannyThreshold_slider = QSlider(Qt.Horizontal)
        self.cannyThreshold_slider.setRange(1, 100)
        self.cannyThreshold_slider.setValue(self.cannyThreshold)
        self.cannyThreshold_slider.valueChanged.connect(
            self.onCannyThresholdSliderChange)
        self.cannyThreshold_text = QLineEdit()
        self.cannyThreshold_text.setValidator(QIntValidator())
        self.cannyThreshold_text.setText(str(self.cannyThreshold))
        self.cannyThreshold_text.textChanged.connect(
            self.onCannyThresholdTextChange)
        self.cannyThreshold_text.setFixedWidth(30)
        layout.addWidget(cannyThreshold_label, 2, 0)
        layout.addWidget(self.cannyThreshold_slider, 2, 1)
        layout.addWidget(self.cannyThreshold_text, 2, 2)

        votesThreshold_label = QLabel("votesThreshold")
        self.votesThreshold_slider = QSlider(Qt.Horizontal)
        self.votesThreshold_slider.setRange(1, 100)
        self.votesThreshold_slider.setValue(self.votesThreshold)
        self.votesThreshold_slider.valueChanged.connect(
            self.onVotesThresholdSliderChange)
        self.votesThreshold_text = QLineEdit()
        self.votesThreshold_text.setValidator(QIntValidator())
        self.votesThreshold_text.setText(str(self.votesThreshold))
        self.votesThreshold_text.textChanged.connect(
            self.onVotesThresholdTextChange)
        self.votesThreshold_text.setFixedWidth(30)
        layout.addWidget(votesThreshold_label, 3, 0)
        layout.addWidget(self.votesThreshold_slider, 3, 1)
        layout.addWidget(self.votesThreshold_text, 3, 2)

        minRadius_label = QLabel("minRadius")
        self.minRadius_slider = QSlider(Qt.Horizontal)
        self.minRadius_slider.setRange(1, 50)
        self.minRadius_slider.setValue(self.minRadius)
        self.minRadius_slider.valueChanged.connect(
            self.onMinRadiusSliderChange)
        self.minRadius_text = QLineEdit()
        self.minRadius_text.setValidator(QIntValidator())
        self.minRadius_text.setText(str(self.minRadius))
        self.minRadius_text.textChanged.connect(self.onMinRadiusTextChange)
        self.minRadius_text.setFixedWidth(30)
        layout.addWidget(minRadius_label, 4, 0)
        layout.addWidget(self.minRadius_slider, 4, 1)
        layout.addWidget(self.minRadius_text, 4, 2)

        maxRadius_label = QLabel("maxRadius")
        self.maxRadius_slider = QSlider(Qt.Horizontal)
        self.maxRadius_slider.setRange(1, 50)
        self.maxRadius_slider.setValue(self.maxRadius)
        self.maxRadius_slider.valueChanged.connect(
            self.onMaxRadiusSliderChange)
        self.maxRadius_text = QLineEdit()
        self.maxRadius_text.setValidator(QIntValidator())
        self.maxRadius_text.setText(str(self.maxRadius))
        self.maxRadius_text.textChanged.connect(self.onMaxRadiusTextChange)
        self.maxRadius_text.setFixedWidth(30)
        layout.addWidget(maxRadius_label, 5, 0)
        layout.addWidget(self.maxRadius_slider, 5, 1)
        layout.addWidget(self.maxRadius_text, 5, 2)

        maxCircles_label = QLabel("maxCircles")
        self.maxCircles_slider = QSlider(Qt.Horizontal)
        self.maxCircles_slider.setRange(1, 200)
        self.maxCircles_slider.setValue(self.maxCircles)
        self.maxCircles_slider.valueChanged.connect(
            self.onMaxCirclesSliderChange)
        self.maxCircles_text = QLineEdit()
        self.maxCircles_text.setValidator(QIntValidator())
        self.maxCircles_text.setText(str(self.maxCircles))
        self.maxCircles_text.textChanged.connect(self.onMaxCirclesTextChange)
        self.maxCircles_text.setFixedWidth(30)
        layout.addWidget(maxCircles_label, 6, 0)
        layout.addWidget(self.maxCircles_slider, 6, 1)
        layout.addWidget(self.maxCircles_text, 6, 2)


        webcams = obtener_webcams()
        monitores = obtener_numeros_monitores_conectados()

        self.labelCamara = self.crear_label("Camara:", 1290, 5, 50, 30)
        self.comboCamaras = self.crear_combobox(webcams, 1290, 35, 100, 30, 0)
        self.comboMonitores = self.crear_combobox(monitores, 1290, 35, 100, 30, 0)
        self.labelNombrePreset = self.crear_label("Nombre archivo:", 1290,5,50,30)
        self.textNombrePreset = QLineEdit(self)
        
        self.botonProyectar = self.crear_boton("Proyectar", 1290, 125, 100, 30)
        self.botonConfigurarROI = self.crear_boton("Configurar ROI", 1290, 125, 100, 30)
        self.botonPreprocesamientos = self.crear_boton("Preprocesamientos", 1290, 125, 100, 30)
        self.botonGuardarPreset = self.crear_boton("Guardar Preset", 1290,125,100,30)
        self.botonCargarPreset = self.crear_boton("Cargar Preset", 1290,125,100, 30)
        self.botonSetearIDS = self.crear_boton("Setear IDS", 1290,125,100,30)


        layout.addWidget(self.labelCamara,7,0)
        layout.addWidget(self.labelNombrePreset,7,3)
        layout.addWidget(self.textNombrePreset,8,3)
        layout.addWidget(self.comboCamaras,8,0)
        layout.addWidget(self.botonSetearIDS,8,1)
        layout.addWidget(self.botonProyectar, 9, 0)
        layout.addWidget(self.comboMonitores, 10, 0)
        layout.addWidget(self.botonConfigurarROI, 9, 1)
        layout.addWidget(self.botonPreprocesamientos, 9, 2)
        layout.addWidget(self.botonGuardarPreset,9,3)
        layout.addWidget(self.botonCargarPreset,10,3)


        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
    
    def obtenerComboCamaras(self):
        return self.comboCamaras
    
    def obtenerComboMonitores(self):
        return self.comboMonitores
    
    def obtenerBotones(self):
        return self.botonProyectar, self.botonConfigurarROI, self.botonPreprocesamientos, self.botonGuardarPreset,  self.botonCargarPreset, self.botonSetearIDS

    def crear_boton(self, texto, x, y, ancho, alto):
        boton = QPushButton(texto, self)
        boton.setGeometry(x, y, ancho, alto)
        return boton
    
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

    def onDpSliderChange(self, value):
        self.dp = value
        self.dpChanged.emit(self.dp)
        # Actualizar el cuadro de texto correspondiente
        self.dp_text.setText(str(self.dp))

    def onDpTextChange(self, text):
        if text:
            self.dp = int(text)
            self.dpChanged.emit(self.dp)
            # Actualizar el slider correspondiente
            self.dp_slider.setValue(self.dp)

    def onMinDistSliderChange(self, value):
        self.minDist = value
        self.minDistChanged.emit(self.minDist)
        # Actualizar el cuadro de texto correspondiente
        self.minDist_text.setText(str(self.minDist))

    def onMinDistTextChange(self, text):
        if text:
            self.minDist = int(text)
            self.minDistChanged.emit(self.minDist)
            # Actualizar el slider correspondiente
            self.minDist_slider.setValue(self.minDist)

    def onCannyThresholdSliderChange(self, value):
        self.cannyThreshold = value
        self.cannyThresholdChanged.emit(self.cannyThreshold)
        # Actualizar el cuadro de texto correspondiente
        self.cannyThreshold_text.setText(str(self.cannyThreshold))

    def onCannyThresholdTextChange(self, text):
        if text:
            self.cannyThreshold = int(text)
            self.cannyThresholdChanged.emit(self.cannyThreshold)
            # Actualizar el slider correspondiente
            self.cannyThreshold_slider.setValue(self.cannyThreshold)

    def onVotesThresholdSliderChange(self, value):
        self.votesThreshold = value
        self.votesThresholdChanged.emit(self.votesThreshold)
        # Actualizar el cuadro de texto correspondiente
        self.votesThreshold_text.setText(str(self.votesThreshold))

    def onVotesThresholdTextChange(self, text):
        if text:
            self.votesThreshold = int(text)
            self.votesThresholdChanged.emit(self.votesThreshold)
            # Actualizar el slider correspondiente
            self.votesThreshold_slider.setValue(self.votesThreshold)

    def onMinRadiusSliderChange(self, value):
        self.minRadius = value
        self.minRadiusChanged.emit(self.minRadius)
        # Actualizar el cuadro de texto correspondiente
        self.minRadius_text.setText(str(self.minRadius))

    def onMinRadiusTextChange(self, text):
        if text:
            self.minRadius = int(text)
            self.minRadiusChanged.emit(self.minRadius)
            # Actualizar el slider correspondiente
            self.minRadius_slider.setValue(self.minRadius)
            # Validar que minRadius sea menor que maxRadius
            if self.minRadius >= self.maxRadius:
                self.minRadius = self.maxRadius - 1
                self.minRadius_text.setText(str(self.minRadius))
                self.minRadius_slider.setValue(self.minRadius)

    def onMaxRadiusSliderChange(self, value):
        self.maxRadius = value
        self.maxRadiusChanged.emit(self.maxRadius)
        # Actualizar el cuadro de texto correspondiente
        self.maxRadius_text.setText(str(self.maxRadius))

    def onMaxRadiusTextChange(self, text):
        if text:
            self.maxRadius = int(text)
            self.maxRadiusChanged.emit(self.maxRadius)
            # Actualizar el slider correspondiente
            self.maxRadius_slider.setValue(self.maxRadius)
            # Validar que maxRadius sea mayor que minRadius
            if self.maxRadius <= self.minRadius:
                self.maxRadius = self.minRadius + 1
                self.maxRadius_text.setText(str(self.maxRadius))
                self.maxRadius_slider.setValue(self.maxRadius)

    def onMaxCirclesSliderChange(self, value):
        self.maxCircles = value
        self.maxCirclesChanged.emit(self.maxCircles)
        # Actualizar el cuadro de texto correspondiente
        self.maxCircles_text.setText(str(self.maxCircles))

    def onMaxCirclesTextChange(self, text):
        if text:
            self.maxCircles = int(text)
            self.maxCirclesChanged.emit(self.maxCircles)
            # Actualizar el slider correspondiente
            self.maxCircles_slider.setValue(self.maxCircles)

    def actualizarParametros(self, dp, minDist, cannyThreshold, votesThreshold, minRadius, maxRadius, maxCircles):
        self.dp = dp
        self.minDist = minDist
        self.cannyThreshold = cannyThreshold
        self.votesThreshold = votesThreshold
        self.minRadius = minRadius
        self.maxRadius = maxRadius
        self.maxCircles = maxCircles
        self.actualizarSliderTextBox()

    def actualizarSliderTextBox(self):
        self.minRadius_text.setText(str(self.minRadius))
        self.minRadius_slider.setValue(self.minRadius)

        self.maxRadius_text.setText(str(self.maxRadius))
        self.maxRadius_slider.setValue(self.maxRadius)

        self.cannyThreshold_text.setText(str(self.cannyThreshold))
        self.cannyThreshold_slider.setValue(self.cannyThreshold)

        self.votesThreshold_text.setText(str(self.votesThreshold))
        self.votesThreshold_slider.setValue(self.votesThreshold)

        self.dp_text.setText(str(self.dp))
        self.dp_slider.setValue(self.dp)

        self.maxCircles_text.setText(str(self.maxCircles))
        self.maxCircles_slider.setValue(self.maxCircles)

        self.minDist_text.setText(str(self.minDist))
        self.minDist_slider.setValue(self.minDist)
    
    
# def main():
#     app = QApplication(sys.argv)
#     window = ControlWindow()
#     window.show()
#     sys.exit(app.exec_())

# if __name__ == "__main__":
#     main()