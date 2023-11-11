import math

class Respuesta:
    def __init__(self, primerContactoCorrecto=None, cantCorrectas=None, cantIncorrectas=None, embocoNegraError=None, vxBlanca=None, vyBlanca=None, cantRebotesBlanca=None, tiroValido=None, trayectorias = None, trayectoriaBlanca = None, attrs=None, best_player=None):
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
        self.trayectorias = trayectorias
        self.trayectoriaBlanca = trayectoriaBlanca
        self.attrs = attrs
        self.best_player = best_player

    def obtener_velocidad(self, velX, velY):
        return math.sqrt(velX**2 + velY**2)
    def set_balls(self,balls):
        self.balls = balls
