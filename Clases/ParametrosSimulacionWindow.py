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
    anchoAltoMesaChanged = pyqtSignal(int)

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
        self.anchoAltoMesa = 1000

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
        self.anchoAltoMesa_label = QLabel("Ancho - Alto - Mesa")
        self.anchoCmMesa_label = QLabel("Ancho(cm)")
        self.altoCmMesa_label = QLabel("Alto(cm)")

        self.distRailes_slider = QSlider(Qt.Horizontal)
        self.distTronerasEsquinas_slider = QSlider(Qt.Horizontal)
        self.distTronerasMedias_slider = QSlider(Qt.Horizontal)
        self.limiteVelocidad_slider = QSlider(Qt.Horizontal)
        self.friccionBolas_slider = QSlider(Qt.Horizontal)
        self.friccionRailes_slider = QSlider(Qt.Horizontal)
        self.anchoAltoMesa_slider = QSlider(Qt.Horizontal)

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
        self.anchoAltoMesa_text = QLineEdit()
        self.anchoAltoMesa_text.setValidator(QIntValidator())

        self.altoCmMesa_text = QLineEdit()
        self.anchoCmMesa_text = QLineEdit()
        self.anchoCmMesa_text.setDisabled(True)
        self.altoCmMesa_text.setDisabled(True)

        self.distRailes_text.setFixedWidth(30)
        self.distTronerasEsquinas_text.setFixedWidth(30)
        self.distTronerasMedias_text.setFixedWidth(30)
        self.limiteVelocidad_text.setFixedWidth(30)
        self.friccionBolas_text.setFixedWidth(30)
        self.friccionRailes_text.setFixedWidth(30)
        self.anchoAltoMesa_text.setFixedWidth(30)
        self.anchoCmMesa_text.setFixedWidth(30)
        self.altoCmMesa_text.setFixedWidth(30)

        self.distRailes_text.setText(str(self.distRailes))  
        self.distTronerasEsquinas_text.setText(str(self.distTronerasEsquinas))    
        self.distTronerasMedias_text.setText(str(self.distTronerasMedias))       
        self.limiteVelocidad_text.setText(str(self.limiteVelocidad))
        self.friccionBolas_text.setText(str(self.friccionBolas))
        self.friccionRailes_text.setText(str(self.friccionRailes))
        self.anchoAltoMesa_text.setText(str(self.anchoAltoMesa))
        self.anchoCmMesa_text.setText("200")
        self.altoCmMesa_text.setText("100")

        self.distRailes_slider.setRange(1,154)
        self.distTronerasEsquinas_slider.setRange(1,152)
        self.distTronerasEsquinas_slider.setDisabled(True)
        self.distTronerasMedias_slider.setRange(1,130)
        self.distTronerasMedias_slider.setDisabled(True)
        self.limiteVelocidad_slider.setRange(10,400)
        self.friccionBolas_slider.setRange(1,10)
        self.friccionRailes_slider.setRange(1,10)
        self.anchoAltoMesa_slider.setRange(100,1000)

        self.distRailes_slider.setValue(self.distRailes)
        self.distTronerasEsquinas_slider.setValue(self.distTronerasEsquinas)
        self.distTronerasMedias_slider.setValue(self.distTronerasMedias)
        self.limiteVelocidad_slider.setValue(self.limiteVelocidad)
        self.friccionBolas_slider.setValue(int(self.friccionBolas * 10))
        self.friccionRailes_slider.setValue(int(self.friccionRailes * 10))
        self.anchoAltoMesa_slider.setValue(self.anchoAltoMesa)

        self.distRailes_slider.valueChanged.connect(self.onDistRailesSliderChange)
        self.distTronerasEsquinas_slider.valueChanged.connect(self.onDistTronerasEsquinasSliderChange)
        self.distTronerasMedias_slider.valueChanged.connect(self.onDistTronerasMediasSliderChange)
        self.limiteVelocidad_slider.valueChanged.connect(self.onLimiteVelocidadSliderChange)
        self.friccionBolas_slider.valueChanged.connect(self.onFriccionBolasSliderChange)
        self.friccionRailes_slider.valueChanged.connect(self.onFriccionRailesSliderChange)
        self.anchoAltoMesa_slider.valueChanged.connect(self.onAltoAnchoMesaSliderChange)

        self.distRailes_text.textChanged.connect(self.onDistRailesTextChange)
        self.distTronerasEsquinas_text.textChanged.connect(self.onDistTronerasEsquinasTextChange)
        self.distTronerasMedias_text.textChanged.connect(self.onDistTronerasMediasTextChange)
        self.limiteVelocidad_text.textChanged.connect(self.onLimiteVelocidadTextChange)
        self.friccionBolas_text.textChanged.connect(self.onFriccionBolasTextChange)
        self.friccionRailes_text.textChanged.connect(self.onFriccionRailesTextChange)
        self.anchoAltoMesa_text.textChanged.connect(self.onAltoAnchoMesaTextChange)

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
        
        layout.addWidget(self.anchoAltoMesa_label, 6, 0)
        layout.addWidget(self.anchoAltoMesa_slider, 6, 1)
        layout.addWidget(self.anchoAltoMesa_text, 6, 2)

        layout.addWidget(self.anchoCmMesa_label, 7, 0)
        layout.addWidget(self.anchoCmMesa_text, 7, 1)
        layout.addWidget(self.altoCmMesa_label, 8, 0)
        layout.addWidget(self.altoCmMesa_text, 8, 1)


        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        
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

    def onAltoAnchoMesaSliderChange(self, value):
        self.anchoAltoMesa = value
        self.anchoAltoMesaChanged.emit(self.anchoAltoMesa)
        self.anchoAltoMesa_text.setText(str(self.anchoAltoMesa))
        self.recalcularAnchoYAltoEnCm()

    def recalcularAnchoYAltoEnCm(self):
        #regla de 3 para calcular en cm
        anchoFixeado = self.anchoAltoMesa
        if(anchoFixeado%2!=0):
            anchoFixeado+=1
        ancho = (int)(anchoFixeado*200/1000)
        self.anchoCmMesa_text.setText(str(ancho))
        self.altoCmMesa_text.setText(str(ancho/2))

    def onDistRailesTextChange(self, text):    
        if text:
            self.distRailes = int(text)
            self.distRailesChanged.emit(self.distRailes)
            # Actualizar el slider correspondiente
            self.distRailes_slider.setValue(self.distRailes)

    def onAltoAnchoMesaTextChange(self, text):
        if text:
            self.anchoAltoMesa = int(text)
            self.anchoAltoMesaChanged.emit(self.anchoAltoMesa)            
            self.anchoAltoMesa_slider.setValue(self.anchoAltoMesa)
            self.recalcularAnchoYAltoEnCm()
        

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


def main():
    app = QApplication(sys.argv)
    window = ParametrosSimulacionWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()