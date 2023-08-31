import threading
import time
import os
from Clases.IA_Handler import IA_Handler

variable_compartida_lock = threading.Lock()


def IniciarCalculoTiro():
    print("inicia hilo IA")
    with variable_compartida_lock:
        #aca tenemos que llamar 2 veces a la IA y 1 vez a la simulacion fisica luego ponderamos los 3 tiros:
        ia = IA_Handler()
        ia.invocarIA()
        