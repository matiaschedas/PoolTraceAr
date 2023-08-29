import math

class SingletonRespuesta:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonRespuesta, cls).__new__(cls)
            cls._instance.init_singletonCompartida(*args, **kwargs)
        return cls._instance
    
    def init_singletonCompartida(self, primerContactoCorrecto=None, cantCorrectas=None, cantIncorrectas=None, embocoNegraError=None, vxBlanca=None, vyBlanca=None, cantRebotesBlanca=None, tiroValido=None):
        self.primerContactoCorrecto = primerContactoCorrecto
        self.cantCorrectas = cantCorrectas
        self.canIncorrectas = cantIncorrectas
        self.embocoNegraError = embocoNegraError
        self.vxBlanca = vxBlanca
        self.vyBlanca = vyBlanca
        if(self.vxBlanca is not None and self.vyBlanca is not None):
            self.velocidad = self.obtener_velocidad(self.vxBlanca, self.vyBlanca)
        self.cantRebotesBlanca = cantRebotesBlanca
        self.tiroValido = tiroValido
       
    def obtener_velocidad(self, velX, velY):
        return math.sqrt(velX**2 + velY**2)

    @classmethod
    def delete_instance(cls):
        cls._instance = None