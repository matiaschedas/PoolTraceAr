import datetime
import threading
import time

class HiloEjemplo(threading.Thread):
    def __init__(self, bloqueo):
        super().__init__()
        self.detener = False
        self.bloqueo = bloqueo
        self.hora_inicio = datetime.datetime.now()

    def run(self):
        segundos_transcurridos = 0
        while segundos_transcurridos < 30 or not self.detener:
            with self.bloqueo:
                if self.detener:
                    break
            print(segundos_transcurridos)
            segundos_transcurridos = (datetime.datetime.now() - self.hora_inicio).total_seconds()
            time.sleep(0.1)

    def detener_hilo(self):
        with self.bloqueo:
            self.detener = True
