from IA_Simulacion.genetic import Genetic
from IA_Simulacion.genetic2 import Genetic2

from IA_Simulacion.SingletonCompartida import SingletonCompartida

import os

directorio_actual = os.path.dirname(os.path.abspath(__file__))

template_dir = os.path.join(directorio_actual, '../Templates/templateconfig.py')
config_dir = os.path.join(directorio_actual, '../IA_Simulacion/utils/config.py')


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
    
    def setearConfig(self, rail_distance, side_pocket_dist, corner_pocket_dist, limite_velocidad, friccion_bola, friccion_railes, ancho_mesa, tam_bolas_simulacion, alto_mesa, radio_troneras_ia):
        singleton = SingletonCompartida()
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
        pocket_resto = "POCKET_LOCATION_RESTO = []"
            
        if(singleton.embocarNegra == True):
            pocket = """POCKET_LOCATION = (
                        np.array(
                            [
                            """+array_nro_tronera[singleton.nroTronera - 1]+"""
                            ]
                        )
                        * ZOOM_MULTIPLIER
                    ).astype(int)"""
            resto = ""
            for i in range(6):
                if i != singleton.nroTronera-1:
                   resto += array_nro_tronera[i]+","
            pocket_resto = """POCKET_LOCATION_RESTO = (
                        np.array(
                            [
                            """+resto+"""
                            ]
                        )
                        * ZOOM_MULTIPLIER
                    ).astype(int)"""
            
        #hacer configurable por el usuario todos los parametros:
        #medidas para mesa grande:
            #rail_distance: int(54 * ZOOM_MULTIPLIER)
            #side_pocket_dist: int(30 * ZOOM_MULTIPLIER)
            #corner_pocket_dist: int(52 * ZOOM_MULTIPLIER)
        
        #friccion normal de las bolas: 0.9
        #friccion normal de los railes: 0.5
        #limite de velocidad normal: int(320 * ZOOM_MULTIPLIER)
        #ancho alto 
        #tam bolas por defecto: BALL_RADIUS = int(12 * ZOOM_MULTIPLIER)
        rail_distance = "RAIL_DISTANCE = int("+str(rail_distance)+"* ZOOM_MULTIPLIER)"
        side_pocket_dist = "SIDE_POCKET_DIST = int("+str(side_pocket_dist)+"* ZOOM_MULTIPLIER)"
        corner_pocket_dist = "CORNER_POCKET_DIST = int("+str(corner_pocket_dist)+"* ZOOM_MULTIPLIER)"
        bola_en_mano = "BOLA_EN_MANO = False"
        limite_velocidad = "VELOCITY_LIMIT = int("+str(limite_velocidad)+"* ZOOM_MULTIPLIER)"
        friccion_bola = "BALL_FRICTION = "+str(friccion_bola)
        friccion_railes = "RAIL_FRICTION = "+str(friccion_railes)
        if singleton.bolaEnMano == True:
            bola_en_mano = "BOLA_EN_MANO = True"
        if(ancho_mesa%2 != 0):
            ancho_mesa+=1
        ancho = ancho_mesa
        if (alto_mesa%2 != 0):
            alto_mesa+=1
        alto = alto_mesa
        anchoAlto = "WIDTH, HEIGHT = "+str(ancho)+","+ str(alto)
        tamBolas = "BALL_RADIUS = int("+str(tam_bolas_simulacion)+"* ZOOM_MULTIPLIER)"
        radio_troneras =  "POCKET_RADIUS = int("+str(radio_troneras_ia)+"* ZOOM_MULTIPLIER)"

        with open(template_dir, 'r') as archivoTemplate:
            contenidoTemplate = archivoTemplate.read()
        contenidoTemplateModificado = contenidoTemplate.replace("POCKET_LOCATION = None", pocket)
        contenidoTemplateModificado = contenidoTemplateModificado.replace("POCKET_LOCATION_RESTO = []", pocket_resto)
        contenidoTemplateModificado = contenidoTemplateModificado.replace("RAIL_DISTANCE = None",rail_distance)
        contenidoTemplateModificado = contenidoTemplateModificado.replace("SIDE_POCKET_DIST = None",side_pocket_dist)
        contenidoTemplateModificado = contenidoTemplateModificado.replace("CORNER_POCKET_DIST = None",corner_pocket_dist)
        contenidoTemplateModificado = contenidoTemplateModificado.replace("BOLA_EN_MANO = None",bola_en_mano)
        contenidoTemplateModificado = contenidoTemplateModificado.replace("RAIL_FRICTION = None", friccion_railes)
        contenidoTemplateModificado = contenidoTemplateModificado.replace("BALL_FRICTION = None",friccion_bola)
        contenidoTemplateModificado = contenidoTemplateModificado.replace("VELOCITY_LIMIT = None", limite_velocidad)
        contenidoTemplateModificado = contenidoTemplateModificado.replace("WIDTH, HEIGHT = 1000, 500", anchoAlto)
        contenidoTemplateModificado = contenidoTemplateModificado.replace("BALL_RADIUS = int(12 * ZOOM_MULTIPLIER)",tamBolas)
        contenidoTemplateModificado = contenidoTemplateModificado.replace("POCKET_RADIUS = int(20 * ZOOM_MULTIPLIER)",radio_troneras)
        with open(config_dir, 'w') as archivoConfig:
            archivoConfig.write(contenidoTemplateModificado)


    def invocarIA(self, rail_distance, side_pocket_dist, corner_pocket_dist, limite_velocidad, friccion_bola, friccion_railes, ancho_mesa, tam_bolas_simulacion, alto_mesa, radio_troneras_ia):
        self.setearConfig(rail_distance, side_pocket_dist, corner_pocket_dist, limite_velocidad, friccion_bola, friccion_railes, ancho_mesa, tam_bolas_simulacion, alto_mesa, radio_troneras_ia)
        singleton = SingletonCompartida()

        response = None

        if singleton.bolaEnMano == True:
            response = self.genetic2.iniciar() 
        else:
            response = self.genetic.iniciar()
        self.genetic = None
        self.genetic2 = None
        return response
    
    def verSimulacion(self, attrs, best_player):
        self.genetic.ver_simulacion(attrs,best_player)
        self.genetic = None

    def verMesa(self, objetoVerMesa):
        self.genetic.ver_mesa(objetoVerMesa)
        self.genetic = None

   