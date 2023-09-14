import threading
from Clases.IA_Handler import IA_Handler
from IA_Simulacion.SingletonRespuesta import SingletonRespuesta

class miHilo(threading.Thread):
    def __init__(self):
        super().__init__()
        self.tiroSeleccionado = 0
        self.respuesta = None
        self.lock = threading.Lock()
    
    def run(self):
        # Realiza alguna operación que actualiza tiroSeleccionado
        with self.lock:
             #aca tenemos que llamar 2 veces a la IA y 1 vez a la simulacion fisica
            SingletonRespuesta.delete_instance()
            ia = IA_Handler()
            self.respuesta  = ia.invocarIA()
            ia = None            
            self.tiroSeleccionado = 1
            if self.respuesta .tiroValido != True or self.respuesta .primerContactoCorrecto!=True or self.respuesta .cantCorrectas==0 or self.respuesta .canIncorrectas>0:                
                SingletonRespuesta.delete_instance()
                ia = IA_Handler()
                self.respuesta  = ia.invocarIA()
                ia = None                
                self.tiroSeleccionado = 2
    def VerSimulacion(self,attrs, best_player):
        print("inicia hilo simulacion")
        with self.lock:
            ia = IA_Handler()
            ia.verSimulacion(attrs,best_player)
    



               