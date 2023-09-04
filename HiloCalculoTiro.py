import threading
from Clases.IA_Handler import IA_Handler
from IA_Simulacion.SingletonRespuesta import SingletonRespuesta

tiroSeleccionado = 0
variable_compartida_lock_tiro = threading.Lock()

def IniciarCalculoTiro():
    print("inicia hilo IA")
    global tiroSeleccionado
    with variable_compartida_lock_tiro:
        #aca tenemos que llamar 2 veces a la IA y 1 vez a la simulacion fisica
        ia = IA_Handler()
        ia.invocarIA()
        ia = None
        respuesta = SingletonRespuesta()
        tiroSeleccionado = 1
        if respuesta.tiroValido != True or respuesta.primerContactoCorrecto!=True or respuesta.cantCorrectas==0 or respuesta.canIncorrectas>0:
            SingletonRespuesta.delete_instance()
            ia = IA_Handler()
            ia.invocarIA()
            ia = None
            respuesta = SingletonRespuesta()
            tiroSeleccionado = 2


def VerSimulacion(attrs, best_player):
    print("inicia hilo simulacion")
    with variable_compartida_lock_tiro:
        ia = IA_Handler()
        ia.verSimulacion(attrs,best_player)



               