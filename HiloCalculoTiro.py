import threading
from Clases.IA_Handler import IA_Handler
from IA_Simulacion.SingletonRespuesta import SingletonRespuesta

class miHilo(threading.Thread):
    def __init__(self, rail_distance, side_pocket_dist, corner_pocket_dist, limite_velocidad, friccion_bola, friccion_railes, ancho_mesa, tam_bolas_simulacion, alto_mesa, radio_troneras_ia):
        super().__init__()
        self.tiroSeleccionado = 0
        self.respuesta = None
        self.lock = threading.Lock()
        self.rail_distance = rail_distance
        self.side_pocket_dist = side_pocket_dist
        self.corner_pocket_dist = corner_pocket_dist
        self.limite_velocidad = limite_velocidad
        self.friccion_bola = friccion_bola
        self.friccion_railes = friccion_railes
        self.ancho_mesa = ancho_mesa
        self.tam_bolas_simulacion = tam_bolas_simulacion
        self.alto_mesa = alto_mesa
        self.radio_troneras_ia = radio_troneras_ia
    
    def run(self):
        # Realiza alguna operación que actualiza tiroSeleccionado
        with self.lock:
             #aca tenemos que llamar 2 veces a la IA y 1 vez a la simulacion fisica
            SingletonRespuesta.delete_instance()
            ia = IA_Handler()
            self.respuesta  = ia.invocarIA(self.rail_distance, self.side_pocket_dist, self.corner_pocket_dist, self.limite_velocidad, self.friccion_bola, self.friccion_railes, self.ancho_mesa, self.tam_bolas_simulacion, self.alto_mesa, self.radio_troneras_ia)
            ia = None            
            self.tiroSeleccionado = 1
            if self.respuesta .tiroValido != True or self.respuesta .primerContactoCorrecto!=True or self.respuesta .cantCorrectas==0 or self.respuesta .canIncorrectas>0:                
                SingletonRespuesta.delete_instance()
                ia = IA_Handler()
                self.respuesta  = ia.invocarIA(self.rail_distance, self.side_pocket_dist, self.corner_pocket_dist, self.limite_velocidad, self.friccion_bola, self.friccion_railes, self.ancho_mesa,self.tam_bolas_simulacion, self.alto_mesa, self.radio_troneras_ia)
                ia = None                
                self.tiroSeleccionado = 2

    def VerSimulacion(self,attrs, best_player):
        print("inicia hilo simulacion")
        with self.lock:
            ia = IA_Handler()
            ia.verSimulacion(attrs,best_player)

    def VerMesa(self, objetoVerMesa):
        ia = IA_Handler()
        self.respuesta  = ia.verMesa(objetoVerMesa)
    



               