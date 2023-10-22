import threading
import math

class SingletonCompartida:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SingletonCompartida, cls).__new__(cls)
                    cls._instance.init_singletonCompartida(*args, **kwargs)
        return cls._instance
    
    def init_singletonCompartida(self, listaApareada=None, bolaSeleccionada=None, tamROI=None, embocarNegra=None, bolaEnMano=None, dosTiros=None, mesaAbierta=None, nroTronera=None, distancia_railes=None,  distancia_troneras_medias=None,distancia_troneras_esquinas=None,limite_velocidad=None, friccion_bolas=None, friccion_railes=None, ancho_mesa=None, tam_bolas_simulacion=None, alto_mesa = None, radio_troneras_ia=None):
        self.listaApareada = listaApareada
        self.bolaSeleccionada = bolaSeleccionada
        self.tamROI = tamROI
        if(self.tamROI is not None):
            self.ancho, self.alto = self.tamROI
        self.embocarNegra = embocarNegra
        if(listaApareada is not None and bolaSeleccionada is not None):
            self.etiquetaDeSeleccionada = self.obtenerEtiquetaSeleccionada(listaApareada,bolaSeleccionada)
        else:
            self.etiquetaDeSeleccionada = None
        if(self.etiquetaDeSeleccionada == "Negra"):
            self.embocarNegra = True
        self.bolaEnMano = bolaEnMano
        self.dosTiros = dosTiros
        self.mesaAbierta = mesaAbierta
        self.nroTronera = nroTronera

        self.distancia_railes = distancia_railes
        self.distancia_troneras_medias = distancia_troneras_medias
        self.distancia_troneras_esquinas = distancia_troneras_esquinas
        self.limite_velocidad = limite_velocidad
        self.friccion_bolas = friccion_bolas
        self.friccion_railes = friccion_railes
        if(ancho_mesa is not None):
            if(ancho_mesa%2 != 0):
                ancho_mesa += 1
            self.ancho_mesa = ancho_mesa
        else:
            self.ancho_mesa = None
            self.alto_mesa = None
        if(alto_mesa is not None):
            if(alto_mesa%2 != 0):
                alto_mesa +=1
            self.alto_mesa = alto_mesa
            
        self.tam_bolas_simulacion = tam_bolas_simulacion
        self.radio_troneras_ia = radio_troneras_ia
    
    def obtenerEtiquetaSeleccionada(self, listaApareada, bolaSeleccionada):
        for (x,y,r),_,etiqueta in listaApareada:
            xs,ys,rs = bolaSeleccionada
            dist = math.sqrt((x-xs)**2 + (y-ys)**2)
            if(dist <= rs):
                return etiqueta
        return None
    
    @classmethod
    def delete_instance(cls):
        cls._instance = None