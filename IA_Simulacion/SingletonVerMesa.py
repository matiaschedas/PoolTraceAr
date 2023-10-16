import threading

class SingletonVerMesa:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SingletonVerMesa, cls).__new__(cls)
                    cls._instance.init_SingletonVerMesa(*args, **kwargs)
        return cls._instance
    
    def init_SingletonVerMesa(self, distancia_railes=None,  distancia_troneras_medias=None,distancia_troneras_esquinas=None,limite_velocidad=None, friccion_bolas=None, friccion_railes=None, ancho_mesa=None, tam_bolas_simulacion=None, alto_mesa = None):
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
    
    @classmethod
    def delete_instance(cls):
        cls._instance = None