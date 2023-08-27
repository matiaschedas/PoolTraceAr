from IA_Simulacion.pool import PoolEnv
from IA_Simulacion.genetic import Genetic

class IA_Handler ():

    def __init__(self):
        self.genetic = Genetic()

    def invocarIA(self):
        #self.poolEnv.reset()
        self.genetic.iniciar()
        self.genetic = None

   