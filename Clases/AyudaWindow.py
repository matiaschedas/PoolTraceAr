import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit

class AyudaWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800,600)
        self.setWindowTitle('Manual de Ayuda')
        textoManual = """Uso de la aplicación:\n\n
        1. Lo primero que debe hacer es seleccionar la bola que desea embocar:\n
        \t1.1. Puede seleccionarla con el clic izquierdo\n
        \t1.2. Puede seleccionarla manteniendo el clic izquierdo durante 2 segundos en el caso de que el sistema \n
        \ttenga dificultades al detectarla\n
        2. Una vez seleccionada la bola se habilitara el boton "Calcular tiro":\n
        \t2.1. Haciendo clic en "Calcular tiro" el sistema se pondra en modo "corrección" y el boton "Calcular tiro" cambiara a "Confirmar".\n
        \tEn este modo de correccion usted podra manipular las bolas que el sistema logro detectar en la mesa de la siguiente manera:\n
        \t\t2.1.1. Podra mover cualquiera de las bolas detectadas para acomodarlas en caso de que alguna/s de las \n
        \t\tdetecciones esten corridas\n
        \t\t2.1.2 Podra eliminar alguna/s bola/s detectada/s si lo requiere haciendo doble clic sobre la misma\n
        \t\t2.1.3 Podra agregar alguna/s bola/s si asi lo requiera en caso de que el sistema no la pudo detectar en ese momento\n 
        \t\thaciendo clic derecho donde la quiera ubicar\n
        3. Una vez realizadas las correcciones necesarias si las hubiera podra hacer clic en el boton "Confirmar", \n
        el sistema comenzara a calcular el tiro posibles.\n
        4. Cuando la barra de carga llegue al 100% podra visualizar la trayectoria sugerida sobre la mesa\n\n
        Opciones Extra: Al momento de comenzar su turno usted podra seleccionar en la interfaz las siguientes opciones:\n
        \t a. 2 tiros: si usted tiene 2 tiros para este turno\n
        \t b. Mesa abierta: si la mesa esta abierta en este turno\n
        \t c. Bola en mano: si usted tiene bola en mano en este turno"""
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText(textoManual)

        self.setCentralWidget(self.text_edit)

def main():
    app = QApplication(sys.argv)
    ventana_ayuda = AyudaWindow()
    ventana_ayuda.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()