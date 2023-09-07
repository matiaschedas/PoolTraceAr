from IA_Simulacion.genetic import Genetic
from IA_Simulacion.genetic2 import Genetic2
from IA_Simulacion.genetic3 import Genetic3
from IA_Simulacion.genetic4 import Genetic4
from IA_Simulacion.SingletonCompartida import SingletonCompartida

class IA_Handler ():

    def __init__(self):
        self.genetic = Genetic()
        self.genetic2 = Genetic2()
        self.genetic3 = Genetic3()
        self.genetic4 = Genetic4()


    def invocarIA(self):
        singleton = SingletonCompartida()
        if singleton.embocarNegra == True and singleton.bolaEnMano == False:
            self.genetic3.iniciar() 
        elif singleton.embocarNegra == True and singleton.bolaEnMano == True:
            self.genetic4.iniciar()
        elif singleton.bolaEnMano == True:
            self.genetic2.iniciar() 
        else:
            self.genetic.iniciar()
        self.genetic = None
        self.genetic2 = None
    
    def verSimulacion(self, attrs, best_player):
        self.genetic.ver_simulacion(attrs,best_player)
        self.genetic = None

   