import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator, QIcon, QDoubleValidator
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QSlider, QLineEdit, QLabel, QGridLayout, QPushButton, QCheckBox, QComboBox, QApplication
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

class ParametrosSimulacionWindow(QMainWindow):
    distRailesChanged = pyqtSignal(int)
    distTronerasMediasChanged = pyqtSignal(int)
    distTronerasEsquinasChanged = pyqtSignal(int)
    friccionBolasChanged = pyqtSignal(float)
    friccionRailesChanged = pyqtSignal(float)
    limiteVelocidadChanged = pyqtSignal(int)
    anchoMesaChanged = pyqtSignal(int)
    tambBolasChanged = pyqtSignal(int)
    altoMesaChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Parametros Simulacion Fisica")
        self.setGeometry(100, 100, 500, 300)

        self.distRailes = 1
        self.distTronerasEsquinas = -2
        self.distTronerasMedias = -21
        self.limiteVelocidad = 320
        self.friccionBolas = 0.9
        self.friccionRailes = 0.5
        self.anchoMesa = 1000
        self.tamBolas = 12
        self.altoMesa = 500

        icon_path = os.path.join(script_dir.replace("Clases", "images"), "config.png")
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)

        self.initUI()
       
    def initUI(self):
        layout = QGridLayout()

        self.distRailes_label = QLabel("Distancia railes")
        self.distTronerasEsquinas_label = QLabel("Distancia Troneras Esquinas")
        self.distTronerasMedias_label = QLabel("Distancia Troneras Medias")
        self.limiteVelocidad_label = QLabel("Limite de velocidad")
        self.friccionBolas_label = QLabel("Friccion de bolas")
        self.friccionRailes_label = QLabel("Friccion de railes")
        self.tamBolas_label = QLabel("Tamaño bolas")
        self.anchoMesa_label = QLabel("Ancho - Mesa")
        self.altoMesa_label = QLabel("Alto - Mesa")
        self.anchoCmMesa_label = QLabel("Ancho(cm)")
        self.altoCmMesa_label = QLabel("Alto(cm)")
        self.relacionBolaAlto_label = QLabel("Alto(cant bolas)")
        self.relacionBolaAncho_label = QLabel("Ancho(cant bolas)")

        self.distRailes_slider = QSlider(Qt.Horizontal)
        self.distTronerasEsquinas_slider = QSlider(Qt.Horizontal)
        self.distTronerasMedias_slider = QSlider(Qt.Horizontal)
        self.limiteVelocidad_slider = QSlider(Qt.Horizontal)
        self.friccionBolas_slider = QSlider(Qt.Horizontal)
        self.friccionRailes_slider = QSlider(Qt.Horizontal)
        self.tamBolas_slider = QSlider(Qt.Horizontal)
        self.anchoMesa_slider = QSlider(Qt.Horizontal)
        self.altoMesa_slider = QSlider(Qt.Horizontal)

        self.distRailes_text = QLineEdit()
        self.distRailes_text.setValidator(QIntValidator())
        self.distTronerasEsquinas_text = QLineEdit()
        self.distTronerasEsquinas_text.setValidator(QIntValidator())
        self.distTronerasMedias_text = QLineEdit()
        self.distTronerasMedias_text.setValidator(QIntValidator())
        self.limiteVelocidad_text = QLineEdit()
        self.limiteVelocidad_text.setValidator(QIntValidator())
        self.friccionBolas_text = QLineEdit()
        self.friccionBolas_text.setValidator(QDoubleValidator())
        self.friccionRailes_text = QLineEdit()
        self.friccionRailes_text.setValidator(QDoubleValidator())
        self.tamBolas_text = QLineEdit()
        self.tamBolas_text.setValidator(QIntValidator())
        self.anchoMesa_text = QLineEdit()
        self.anchoMesa_text.setValidator(QIntValidator())
        self.altoMesa_text = QLineEdit()
        self.altoMesa_text.setValidator(QIntValidator())

        self.altoCmMesa_text = QLineEdit()
        self.anchoCmMesa_text = QLineEdit()
        self.relacionBolaAlto_text = QLineEdit()
        self.relacionBolaAncho_text = QLineEdit()
        self.anchoCmMesa_text.setDisabled(True)
        self.altoCmMesa_text.setDisabled(True)
        self.relacionBolaAlto_text.setDisabled(True)
        self.relacionBolaAncho_text.setDisabled(True)

        self.distRailes_text.setFixedWidth(30)
        self.distTronerasEsquinas_text.setFixedWidth(30)
        self.distTronerasMedias_text.setFixedWidth(30)
        self.limiteVelocidad_text.setFixedWidth(30)
        self.friccionBolas_text.setFixedWidth(30)
        self.friccionRailes_text.setFixedWidth(30)
        self.anchoMesa_text.setFixedWidth(30)
        self.anchoCmMesa_text.setFixedWidth(30)
        self.altoCmMesa_text.setFixedWidth(30)
        self.tamBolas_text.setFixedWidth(30)
        self.relacionBolaAlto_text.setFixedWidth(30)
        self.relacionBolaAncho_text.setFixedWidth(30)
        self.altoMesa_text.setFixedWidth(30)

        self.distRailes_text.setText(str(self.distRailes))  
        self.distTronerasEsquinas_text.setText(str(self.distTronerasEsquinas))    
        self.distTronerasMedias_text.setText(str(self.distTronerasMedias))       
        self.limiteVelocidad_text.setText(str(self.limiteVelocidad))
        self.friccionBolas_text.setText(str(self.friccionBolas))
        self.friccionRailes_text.setText(str(self.friccionRailes))
        self.tamBolas_text.setText(str(self.tamBolas))
        self.anchoMesa_text.setText(str(self.anchoMesa))
        self.anchoCmMesa_text.setText("200")
        self.altoCmMesa_text.setText("100")
        relacionBolaAlto = (self.anchoMesa/2)/(self.tamBolas*2)
        relacionBolaAncho = (self.anchoMesa)/(self.tamBolas*2)
        self.relacionBolaAlto_text.setText("{:.1f}".format(relacionBolaAlto))
        self.relacionBolaAncho_text.setText("{:.1f}".format(relacionBolaAncho))
        self.altoMesa_text.setText(str(self.altoMesa))

        self.distRailes_slider.setRange(1,154)
        self.distTronerasEsquinas_slider.setRange(-2,152)
        self.distTronerasEsquinas_slider.setDisabled(False)
        self.distTronerasMedias_slider.setRange(-21,130)
        self.distTronerasMedias_slider.setDisabled(False)
        self.limiteVelocidad_slider.setRange(10,400)
        self.friccionBolas_slider.setRange(1,10)
        self.friccionRailes_slider.setRange(1,10)
        self.anchoMesa_slider.setRange(250,1500)
        self.tamBolas_slider.setRange(5,35)
        self.altoMesa_slider.setRange(250,1500)

        self.distRailes_slider.setValue(self.distRailes)
        self.distTronerasEsquinas_slider.setValue(self.distTronerasEsquinas)
        self.distTronerasMedias_slider.setValue(self.distTronerasMedias)
        self.limiteVelocidad_slider.setValue(self.limiteVelocidad)
        self.friccionBolas_slider.setValue(int(self.friccionBolas * 10))
        self.friccionRailes_slider.setValue(int(self.friccionRailes * 10))
        self.anchoMesa_slider.setValue(self.anchoMesa)
        self.tamBolas_slider.setValue(self.tamBolas)
        self.altoMesa_slider.setValue(self.altoMesa)

        self.distRailes_slider.valueChanged.connect(self.onDistRailesSliderChange)
        self.distTronerasEsquinas_slider.valueChanged.connect(self.onDistTronerasEsquinasSliderChange)
        self.distTronerasMedias_slider.valueChanged.connect(self.onDistTronerasMediasSliderChange)
        self.limiteVelocidad_slider.valueChanged.connect(self.onLimiteVelocidadSliderChange)
        self.friccionBolas_slider.valueChanged.connect(self.onFriccionBolasSliderChange)
        self.friccionRailes_slider.valueChanged.connect(self.onFriccionRailesSliderChange)
        self.anchoMesa_slider.valueChanged.connect(self.onAnchoMesaSliderChange)
        self.tamBolas_slider.valueChanged.connect(self.onTamBolasSliderChange)
        self.altoMesa_slider.valueChanged.connect(self.onAltoMesaSliderChange)

        self.distRailes_text.textChanged.connect(self.onDistRailesTextChange)
        self.distTronerasEsquinas_text.textChanged.connect(self.onDistTronerasEsquinasTextChange)
        self.distTronerasMedias_text.textChanged.connect(self.onDistTronerasMediasTextChange)
        self.limiteVelocidad_text.textChanged.connect(self.onLimiteVelocidadTextChange)
        self.friccionBolas_text.textChanged.connect(self.onFriccionBolasTextChange)
        self.friccionRailes_text.textChanged.connect(self.onFriccionRailesTextChange)
        self.anchoMesa_text.textChanged.connect(self.onAnchoMesaTextChange)
        self.tamBolas_text.textChanged.connect(self.onTamBolasTextChange)
        self.altoMesa_text.textChanged.connect(self.onAltoMesaTextChange)
        
        self.ver_mesa_button = QPushButton("Ver mesa", self)

        layout.addWidget(self.distRailes_label, 0, 0)
        layout.addWidget(self.distRailes_slider, 0, 1)
        layout.addWidget(self.distRailes_text, 0, 2)

        layout.addWidget(self.distTronerasEsquinas_label, 1, 0)
        layout.addWidget(self.distTronerasEsquinas_slider, 1, 1)
        layout.addWidget(self.distTronerasEsquinas_text, 1, 2)

        layout.addWidget(self.distTronerasMedias_label, 2, 0)
        layout.addWidget(self.distTronerasMedias_slider, 2, 1)
        layout.addWidget(self.distTronerasMedias_text, 2, 2)

        layout.addWidget(self.limiteVelocidad_label, 3, 0)
        layout.addWidget(self.limiteVelocidad_slider, 3, 1)
        layout.addWidget(self.limiteVelocidad_text, 3, 2)

        layout.addWidget(self.friccionBolas_label, 4, 0)
        layout.addWidget(self.friccionBolas_slider, 4, 1)
        layout.addWidget(self.friccionBolas_text, 4, 2)

        layout.addWidget(self.friccionRailes_label, 5, 0)
        layout.addWidget(self.friccionRailes_slider, 5, 1)
        layout.addWidget(self.friccionRailes_text, 5, 2)

        layout.addWidget(self.tamBolas_label, 6,0)
        layout.addWidget(self.tamBolas_slider,6,1)
        layout.addWidget(self.tamBolas_text, 6,2)
        
        layout.addWidget(self.anchoMesa_label, 7, 0)
        layout.addWidget(self.anchoMesa_slider, 7, 1)
        layout.addWidget(self.anchoMesa_text, 7, 2)

        layout.addWidget(self.altoMesa_label, 8, 0)
        layout.addWidget(self.altoMesa_slider, 8, 1)
        layout.addWidget(self.altoMesa_text, 8, 2)

        layout.addWidget(self.anchoCmMesa_label, 9, 0)
        layout.addWidget(self.anchoCmMesa_text, 9, 1)
        layout.addWidget(self.altoCmMesa_label, 10, 0)
        layout.addWidget(self.altoCmMesa_text, 10, 1)

        layout.addWidget(self.relacionBolaAlto_label, 11,0)
        layout.addWidget(self.relacionBolaAlto_text, 11,1)
        layout.addWidget(self.relacionBolaAncho_label, 12 ,0)
        layout.addWidget(self.relacionBolaAncho_text, 12 ,1)

        layout.addWidget(self.ver_mesa_button, 13,2)


        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def obtenerBotonVerMesa(self):
        return self.ver_mesa_button

    def actualizarAnchoAltoMesa(self):
        ancho = self.anchoMesa
        alto = self.altoMesa
        if ancho%2 != 0:
            ancho += 1
        if alto%2 != 0:
            alto += 1
        ancho = (int)(ancho*200/1000)
        alto = (int)(alto*200/1000) 
        self.anchoCmMesa_text.setText(str(ancho))
        self.altoCmMesa_text.setText(str(alto))

    def onAltoMesaSliderChange(self, value):
        self.altoMesa = value
        self.altoMesaChanged.emit(self.altoMesa)
        self.altoMesa_slider.setValue(self.altoMesa)
        self.altoMesa_text.setText(str(self.altoMesa))
        self.actualizarRelaciones()
        self.actualizarAnchoAltoMesa()
        
    def onDistRailesSliderChange(self, value):
        self.distRailes = value
        self.distTronerasEsquinas = value - 3
        self.distTronerasMedias = value - 22
        self.distTronerasMediasChanged.emit(self.distTronerasMedias)
        self.distTronerasEsquinasChanged.emit(self.distTronerasEsquinas)
        self.distRailesChanged.emit(self.distRailes)
        self.distTronerasMedias_slider.setValue(self.distTronerasMedias)
        self.distTronerasEsquinas_slider.setValue(self.distTronerasEsquinas)
        # Actualizar el cuadro de texto correspondiente
        self.distRailes_text.setText(str(self.distRailes))
        self.distTronerasEsquinas_text.setText(str(self.distTronerasEsquinas))
        self.distTronerasMedias_text.setText(str(self.distTronerasMedias))

    def onDistTronerasEsquinasSliderChange(self, value):
        self.distTronerasEsquinas = value
        self.distTronerasEsquinasChanged.emit(self.distTronerasEsquinas)
        # Actualizar el cuadro de texto correspondiente
        self.distTronerasEsquinas_text.setText(str(self.distTronerasEsquinas))

    def onDistTronerasMediasSliderChange(self, value):
        self.distTronerasMedias = value
        self.distTronerasMediasChanged.emit(self.distTronerasMedias)
        # Actualizar el cuadro de texto correspondiente
        self.distTronerasMedias_text.setText(str(self.distTronerasMedias))

    def actualizarRelaciones(self):
        relacionBolaAlto = (self.altoMesa)/(self.tamBolas*2)
        relacionBolaAncho = (self.anchoMesa)/(self.tamBolas*2)
        self.relacionBolaAlto_text.setText("{:.1f}".format(relacionBolaAlto))
        self.relacionBolaAncho_text.setText("{:.1f}".format(relacionBolaAncho))

    def onTamBolasSliderChange(self, value):
        self.tamBolas = value
        self.tambBolasChanged.emit(self.tamBolas)
        self.tamBolas_text.setText(str(self.tamBolas))
        self.actualizarRelaciones()

    def onLimiteVelocidadSliderChange(self, value):
        self.limiteVelocidad = value
        self.limiteVelocidadChanged.emit(self.limiteVelocidad)
        # Actualizar el cuadro de texto correspondiente
        self.limiteVelocidad_text.setText(str(self.limiteVelocidad))

    def onFriccionBolasSliderChange(self, value):
        self.friccionBolas = value / 10.0  # Dividir por 10.0 para obtener el valor decimal
        self.friccionBolas_text.setText(str(self.friccionBolas))
        self.friccionBolasChanged.emit(self.friccionBolas)

    def onFriccionRailesSliderChange(self, value):
        self.friccionRailes = value / 10.0  # Dividir por 10.0 para obtener el valor decimal
        self.friccionRailes_text.setText(str(self.friccionRailes))
        self.friccionRailesChanged.emit(self.friccionRailes)

    def onAnchoMesaSliderChange(self, value):
        self.anchoMesa = value
        self.anchoMesaChanged.emit(self.anchoMesa)
        self.anchoMesa_text.setText(str(self.anchoMesa))
        self.actualizarRelaciones()
        self.actualizarAnchoAltoMesa()


    def onAltoMesaTextChange(self, text):
        if text:
            self.altoMesa = int(text)
            self.altoMesaChanged.emit(self.altoMesa)
            self.altoMesa_slider.setValue(self.altoMesa)

    def onDistRailesTextChange(self, text):    
        if text:
            self.distRailes = int(text)
            self.distRailesChanged.emit(self.distRailes)
            # Actualizar el slider correspondiente
            self.distRailes_slider.setValue(self.distRailes)

    def onAnchoMesaTextChange(self, text):
        if text:
            self.anchoMesa = int(text)
            self.anchoMesaChanged.emit(self.anchoMesa)            
            self.anchoMesa_slider.setValue(self.anchoMesa)
            self.actualizarRelaciones()
            
    def onTamBolasTextChange(self, text):
        if text:
            self.tamBolas = int(text)
            self.tambBolasChanged.emit(self.tamBolas)
            self.tamBolas_slider.setValue(self.tamBolas)
            self.actualizarRelaciones()

    def onDistTronerasEsquinasTextChange(self, text):
        self.distTronerasEsquinas_text.setText(str(self.distTronerasEsquinas))
    
    def onDistTronerasMediasTextChange(self, text):
        self.distTronerasMedias_text.setText(str(self.distTronerasMedias))

    def onLimiteVelocidadTextChange(self, text):
        if text:
            self.limiteVelocidad = int(text)
            self.limiteVelocidadChanged.emit(self.limiteVelocidad)
            # Actualizar el slider correspondiente
            self.limiteVelocidad_slider.setValue(self.limiteVelocidad)

    def onFriccionBolasTextChange(self, text):
        try:
            self.friccionBolas = float(text)  # Dividir por 10 para obtener el valor decimal
            self.friccionBolas_slider.setValue(int(self.friccionBolas * 10))
        except ValueError:
            pass
        
    def onFriccionRailesTextChange(self, text):
        try:
            self.friccionRailes = float(text)  # Dividir por 10 para obtener el valor decimal
            self.friccionRailes_slider.setValue(int(self.friccionRailes * 10))
        except ValueError:
            pass
    def actualizarParametros(self, distRailes, distTronerasEsquinas, distTronerasMedias, limiteVelocidad, friccionBolas, friccionRailes, tamBolas, anchoMesa, altoMesa):
        self.distRailes = distRailes
        self.distTronerasEsquinas = distTronerasEsquinas
        self.distTronerasMedias = distTronerasMedias
        self.limiteVelocidad = limiteVelocidad
        self.friccionBolas = friccionBolas
        self.friccionRailes = friccionRailes
        self.tamBolas = tamBolas
        self.anchoMesa = anchoMesa
        self.altoMesa = altoMesa
        self.actualizarSliderTextBox()

    def actualizarSliderTextBox(self):
        self.distRailes_text.setText(str(self.distRailes))
        self.distRailes_slider.setValue(self.distRailes)

        self.distTronerasEsquinas_text.setText(str(self.distTronerasEsquinas))
        self.distTronerasEsquinas_slider.setValue(self.distTronerasEsquinas)

        self.distTronerasMedias_text.setText(str(self.distTronerasEsquinas))
        self.distTronerasMedias_slider.setValue(self.distTronerasMedias)

        self.limiteVelocidad_text.setText(str(self.limiteVelocidad))
        self.limiteVelocidad_slider.setValue(self.limiteVelocidad)

        self.friccionBolas_text.setText(str(self.friccionBolas))
        self.friccionBolas_slider.setValue(int(self.friccionBolas*10))

        self.friccionRailes_text.setText(str(self.friccionRailes))
        self.friccionRailes_slider.setValue(int(self.friccionRailes*10))

        self.tamBolas_text.setText(str(self.tamBolas))
        self.tamBolas_slider.setValue(self.tamBolas)

        self.anchoMesa_text.setText(str(self.anchoMesa))
        self.anchoMesa_slider.setValue(self.anchoMesa)

        self.altoMesa_text.setText(str(self.altoMesa))
        self.altoMesa_slider.setValue(self.altoMesa)

def main():
    app = QApplication(sys.argv)
    window = ParametrosSimulacionWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()