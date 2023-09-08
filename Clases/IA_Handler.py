from IA_Simulacion.genetic import Genetic
from IA_Simulacion.genetic2 import Genetic2

from IA_Simulacion.geneticT1_Normal import GeneticT1_Normal
from IA_Simulacion.geneticT2_Normal import GeneticT2_Normal
from IA_Simulacion.geneticT3_Normal import GeneticT3_Normal
from IA_Simulacion.geneticT4_Normal import GeneticT4_Normal
from IA_Simulacion.geneticT5_Normal import GeneticT5_Normal
from IA_Simulacion.geneticT6_Normal import GeneticT6_Normal

from IA_Simulacion.geneticT1_BolaEnMano import GeneticT1_BolaEnMano
from IA_Simulacion.geneticT2_BolaEnMano import GeneticT2_BolaEnMano
from IA_Simulacion.geneticT3_BolaEnMano import GeneticT3_BolaEnMano
from IA_Simulacion.geneticT4_BolaEnMano import GeneticT4_BolaEnMano
from IA_Simulacion.geneticT5_BolaEnMano import GeneticT5_BolaEnMano
from IA_Simulacion.geneticT6_BolaEnMano import GeneticT6_BolaEnMano

from IA_Simulacion.SingletonCompartida import SingletonCompartida

class IA_Handler ():

    def __init__(self):
        self.genetic = Genetic()
        self.genetic2 = Genetic2()
        self.geneticT1N = GeneticT1_Normal()
        self.geneticT2N = GeneticT2_Normal()
        self.geneticT3N = GeneticT3_Normal()
        self.geneticT4N = GeneticT4_Normal()
        self.geneticT5N = GeneticT5_Normal()
        self.geneticT6N = GeneticT6_Normal()

        self.geneticT1BEN = GeneticT1_BolaEnMano()
        self.geneticT2BEN = GeneticT2_BolaEnMano()
        self.geneticT3BEN = GeneticT3_BolaEnMano()
        self.geneticT4BEN = GeneticT4_BolaEnMano()
        self.geneticT5BEN = GeneticT5_BolaEnMano()
        self.geneticT6BEN = GeneticT6_BolaEnMano()
        


    def invocarIA(self):
        singleton = SingletonCompartida()
        if singleton.embocarNegra == True and singleton.bolaEnMano == False and singleton.nroTronera == 1:
            self.geneticT1N.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == True and singleton.nroTronera == 1:
            self.geneticT1BEN.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == False and singleton.nroTronera == 2:
            self.geneticT2N.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == True and singleton.nroTronera == 2:
            self.geneticT2BEN.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == False and singleton.nroTronera == 3:
            self.geneticT3N.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == True and singleton.nroTronera == 3:
            self.geneticT3BEN.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == False and singleton.nroTronera == 4:
            self.geneticT4N.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == True and singleton.nroTronera == 4:
            self.geneticT4BEN.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == False and singleton.nroTronera == 5:
            self.geneticT5N.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == True and singleton.nroTronera == 5:
            self.geneticT5BEN.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == False and singleton.nroTronera == 6:
            self.geneticT6N.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == True and singleton.nroTronera == 6:
            self.geneticT6BEN.iniciar()
            
        elif singleton.bolaEnMano == True:
            self.genetic2.iniciar() 
        else:
            self.genetic.iniciar()
        self.genetic = None
        self.genetic2 = None
    
    def verSimulacion(self, attrs, best_player):
        self.genetic.ver_simulacion(attrs,best_player)
        self.genetic = None

   