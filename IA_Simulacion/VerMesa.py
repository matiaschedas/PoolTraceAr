class VerMesa:
    def __init__(self, distancia_railes=None,  distancia_troneras_medias=None,distancia_troneras_esquinas=None,limite_velocidad=None, friccion_bolas=None, friccion_railes=None, ancho_mesa=None, tam_bolas_simulacion=None, alto_mesa = None, radio_troneras_ia=None):
        self.distancia_railes = distancia_railes
        self.distancia_troneras_medias = distancia_troneras_medias
        self.distancia_troneras_esquinas = distancia_troneras_esquinas
        self.limite_velocidad = limite_velocidad
        self.friccion_bolas = friccion_bolas
        self.friccion_railes = friccion_railes
        self.radio_troneras_ia = radio_troneras_ia
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
    