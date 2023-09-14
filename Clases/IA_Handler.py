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
import os

template_dir = '../templates/templateconfig.py'
config_dir = '../IA_Simulacion/utils/config.py'

array_nro_tronera = [
"(CORNER_POCKET_DIST, CORNER_POCKET_DIST)",
"(WIDTH // 2, SIDE_POCKET_DIST)",
"(WIDTH - CORNER_POCKET_DIST, CORNER_POCKET_DIST)",
"(CORNER_POCKET_DIST, HEIGHT - CORNER_POCKET_DIST)",
"(WIDTH // 2, HEIGHT - SIDE_POCKET_DIST)",
"(WIDTH - CORNER_POCKET_DIST, HEIGHT - CORNER_POCKET_DIST)"
]
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
        with open(template_dir, 'r') as archivoTemplate:
            contenidoTemplate = archivoTemplate.read()
        contenidoTemplateModificado = contenidoTemplate.replace("POCKET_LOCATION = None", self.pockets)
        with open(config_dir, 'w') as archivoConfig:
            archivoConfig.write(contenidoTemplateModificado)
        if(singleton.embocarNegra == False):
            pocket = """POCKET_LOCATION = (
                    np.array(
                        [
                        (CORNER_POCKET_DIST, CORNER_POCKET_DIST),
                        (WIDTH // 2, SIDE_POCKET_DIST),
                        (WIDTH - CORNER_POCKET_DIST, CORNER_POCKET_DIST),
                        (CORNER_POCKET_DIST, HEIGHT - CORNER_POCKET_DIST),
                        (WIDTH // 2, HEIGHT - SIDE_POCKET_DIST),
                        (WIDTH - CORNER_POCKET_DIST, HEIGHT - CORNER_POCKET_DIST),
                        ]
                    )
                    * ZOOM_MULTIPLIER
                ).astype(int)"""
        if(singleton.embocarNegra == True):
            pocket = """POCKET_LOCATION = (
                np.array(
                    [
                    """+array_nro_tronera[singleton.nroTonera - 1]+"""
                    ]
                )
                * ZOOM_MULTIPLIER
            ).astype(int)"""

        singleton = SingletonCompartida()
        response = None
        if singleton.embocarNegra == True and singleton.bolaEnMano == False and singleton.nroTronera == 1:
            response = self.geneticT1N.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == True and singleton.nroTronera == 1:
            response = self.geneticT1BEN.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == False and singleton.nroTronera == 2:
            response = self.geneticT2N.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == True and singleton.nroTronera == 2:
            response = self.geneticT2BEN.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == False and singleton.nroTronera == 3:
            response = self.geneticT3N.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == True and singleton.nroTronera == 3:
            response = self.geneticT3BEN.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == False and singleton.nroTronera == 4:
            response = self.geneticT4N.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == True and singleton.nroTronera == 4:
            response = self.geneticT4BEN.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == False and singleton.nroTronera == 5:
            response = self.geneticT5N.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == True and singleton.nroTronera == 5:
            response = self.geneticT5BEN.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == False and singleton.nroTronera == 6:
            response = self.geneticT6N.iniciar()
        elif singleton.embocarNegra == True and singleton.bolaEnMano == True and singleton.nroTronera == 6:
            response = self.geneticT6BEN.iniciar()
            
        elif singleton.bolaEnMano == True:
            response = self.genetic2.iniciar() 
        else:
            response = self.genetic.iniciar()
        self.genetic = None
        self.genetic2 = None
        return response
    
    def verSimulacion(self, attrs, best_player):
        self.genetic.ver_simulacion(attrs,best_player)
        self.genetic = None

   