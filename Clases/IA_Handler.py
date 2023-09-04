from IA_Simulacion.genetic import Genetic
from IA_Simulacion.genetic2 import Genetic2
from IA_Simulacion.SingletonCompartida import SingletonCompartida

class IA_Handler ():

    def __init__(self):
        self.genetic = Genetic()
        self.genetic2 = Genetic2()

    def invocarIA(self):
        #self.poolEnv.reset()
        singleton = SingletonCompartida()
        if singleton.bolaEnMano == True:
            self.genetic2.iniciar() 
        else:
            self.genetic.iniciar()
        self.genetic = None
        self.genetic2 = None
    
    def verSimulacion(self, attrs, best_player):
        self.genetic.ver_simulacion(attrs,best_player)
        self.genetic = None

   