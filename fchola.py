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
        print("inicio hilo fchola")
        self.hora_inicio = datetime.datetime.now()
        segundos_transcurridos = 0
        while segundos_transcurridos < 30 and not self.detener:
            print(segundos_transcurridos)
            segundos_transcurridos = (datetime.datetime.now() - self.hora_inicio).total_seconds()
            time.sleep(0.1)
            with self.bloqueo:
                if self.detener:
                    break
            

    def detener_hilo(self):
        with self.bloqueo:
            self.detener = True
