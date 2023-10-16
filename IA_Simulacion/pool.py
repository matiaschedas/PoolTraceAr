from IA_Simulacion.SingletonCompartida import SingletonCompartida
from IA_Simulacion.utils import *
from IA_Simulacion.SingletonRespuesta import SingletonRespuesta
from IA_Simulacion.SingletonVerMesa import SingletonVerMesa
from IA_Simulacion.Respuesta import Respuesta

import os
import gym
import math

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
os.environ["SDL_VIDEO_WINDOW_POS"] = "50, 200"
gym.logger.set_level(40)

import cv2
import time
import random
import numpy as np
import pymunk as pm
import pygame as pg
from gym import spaces
from gym.utils import seeding
from copy import copy
import pymunk.pygame_util as pygame_util
import keyboard
import sys

primerContacto = None
primerContactoCoordenada = None
primerContactoCorrecto = False
bolasEmbocadas = []
bolasCorrectasEmbocadas = 0
bolasIncorrectasEmbocadas = 0
embocoLaNegraIncorrectamente = False
cantidadRebotesBlanca = 0
velocidadXBlanca = 0
velocidadYBlanca = 0
trayectoriaBlanca = []
trayectorias = None




class PoolEnv:
    metadata = {"render.modes": ["human", "rgb_array"], "video.frames_per_second": 500}

    def __init__(
        self,
        training=TRAINING,
        num_balls=NUM_BALLS,
        draw_screen=DRAW_SCREEN,
        reward_by_steps=REWARD_BY_STEPS,
        total_foul_times=TOTAL_FOUL_TIMES,
        observation_type=OBSERVATION_TYPE,
        bola_en_mano=False,
        graficar = True,
        simulacion = False,
        embocarNegra = False,
        nroTronera = -1
    ):
        # initialize some constants
        self.episodes = 0
        self.total_steps = 0
        self.running = True

        
        self.training = training
        self.num_balls = num_balls
        self.reward_by_steps = reward_by_steps
        self.total_foul_times = total_foul_times
        self.observation_type = observation_type
        self.draw_screen = draw_screen or (observation_type == "image") or not training
        self.graficar = graficar
        self.simulacion = simulacion
        # initialize space
        self.space = pm.Space()
        self.space.gravity = (0, 0)
        self.space.damping = 0.83
        self.space.collision_slop = 0.5
        self.space.idle_speed_threshold = 5
        self.space.sleep_time_threshold = 1e-8


        
        self.default = True
        self.balls = []
        self.balls_copy = []
        self.ancho_ratio = 0
        self.alto_ratio = 0
        self.singleton = SingletonCompartida()
        self.bola_en_mano = bola_en_mano
        if(self.singleton.listaApareada is not None):
            self.default = False    
            self.bola_en_mano = self.singleton.bolaEnMano
        if(self.default == False):
            self.width = self.singleton.ancho_mesa * ZOOM_MULTIPLIER
            self.height = self.singleton.alto_mesa * ZOOM_MULTIPLIER
        else:
            self.width = WIDTH * ZOOM_MULTIPLIER
            self.height = HEIGHT * ZOOM_MULTIPLIER
        self.reiniciar_globales()
        if self.graficar == False:
            self.draw_screen = False
        self.attrs_respuesta = None
        self.best_player_respuesta = None
        self.embocarNegra = embocarNegra
        self.nroTronera = nroTronera
        if self.nroTronera is None:
            self.nroTronera = -1
        if self.singleton.nroTronera is not None:
            self.nroTronera = self.singleton.nroTronera
        self.bola_en_mano_error = False

        self.singletonVerMesa = SingletonVerMesa()
        self.verMesa = False
        if (self.singletonVerMesa.distancia_railes != None):
            self.verMesa = True

        # gym environment
        self.spec = None
        self.num_envs = 1
        self.reward_range = np.array([-1, 1])
        self.action_space = spaces.Box(low=-1, high=1, shape=(2,))
        if self.observation_type == "image":
            if self.default == False:
                image_height = int(IMAGE_WIDTH * (self.singleton.alto_mesa / self.singleton.ancho_mesa))
                self.observation_space = spaces.Box(
                    low=0,
                    high=255,
                    shape=(3, image_height, IMAGE_WIDTH),
                    dtype=np.uint8,
                )
            else:
                self.observation_space = spaces.Box(
                    low=0,
                    high=255,
                    shape=(3, IMAGE_HEIGHT, IMAGE_WIDTH),
                    dtype=np.uint8,
                )
        else:
            # ball_x, ball_y, ball_type(pocketed, solid, strips, 8-ball, cue-ball) x 16 balls
            self.table_info = np.concatenate(
                [np.array(RAIL_POLY).flatten(), POCKET_LOCATION.flatten()]
            )
            self.table_info = self.table_info / self.table_info.max()
            low = np.concatenate(
                [np.array([0, 0, 0] * self.num_balls), [0] * len(self.table_info)]
            )
            high = np.concatenate(
                [np.array([1, 1, 1] * self.num_balls), [1] * len(self.table_info)]
            )
            self.observation_space = spaces.Box(
                low=low,
                high=high,
                dtype=np.float32,
            )

        # speed of the env
        self.dt = 24
        self.step_size = 0.45

        # initialize pygame
        if self.draw_screen:
            pg.init()
            self.screen = pg.display.set_mode((int(self.width), int(self.height)))
            self.clock = pg.time.Clock()
            self.draw_options = pygame_util.DrawOptions(self.screen)

        # 1 --> ball, 2 --> pocket, 3 --> rail
        self.ball_collision_handler = self.space.add_collision_handler(1, 1)
        self.ball_collision_handler.begin = self.ball_contacted
        self.pocket_collision_handler = self.space.add_collision_handler(1, 2)
        self.pocket_collision_handler.begin = self.ball_pocketed
        self.rail_collision_handler = self.space.add_collision_handler(1, 3)
        self.rail_collision_handler.begin = self.rail_contacted
        self.pocket_falso_collision_handler = self.space.add_collision_handler(1, 5)
        self.pocket_falso_collision_handler.begin = self.ball_pocketed_falso
        self.reset()

    def ver_mesa(self):
        flag = True
        while flag == True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # Si se cierra la ventana, sal del bucle de juego
                    flag = False
                    pg.quit()
                    break
            else:
                self.render()
    
    def reiniciar_globales(self):
        global primerContacto, primerContactoCorrecto, bolasEmbocadas, bolasCorrectasEmbocadas, bolasIncorrectasEmbocadas, embocoLaNegraIncorrectamente,cantidadRebotesBlanca,velocidadXBlanca,velocidadYBlanca, trayectorias, trayectoriaBlanca, primerContactoCoordenada
        primerContacto = None
        primerContactoCoordenada = None
        primerContactoCorrecto = False
        bolasEmbocadas = []
        bolasCorrectasEmbocadas = 0
        bolasIncorrectasEmbocadas = 0
        embocoLaNegraIncorrectamente = False
        cantidadRebotesBlanca = 0
        velocidadXBlanca = 0
        velocidadYBlanca = 0
        trayectorias = None
        trayectoriaBlanca = []

    def get_action_meanings(self):
        return ["NOOP", "FIRE", "RIGHT", "LEFT", "RIGHTFIRE", "LEFTFIRE"]

    @property
    def unwrapped(self):
        return self

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def render(self):
        self.process_events()
        self.redraw_screen()

    def add_table(self):
        """
        filter: black ball, solids, cue-ball, pocket, rail
        --> 0b      0         0        0         0      0
        if change 0 to 1, means filter out the 1's
        e.g. 0b00111 means only account for unassigned and solids
        this is very complex and you won't understand hahaha
        """
        static_body = self.space.static_body
        self.rails = []
        if self.verMesa:
            rail_distance = int(self.singletonVerMesa.distancia_railes*ZOOM_MULTIPLIER)
            rail_location = (
                                np.array(
                                    [rail_distance, self.singletonVerMesa.ancho_mesa - rail_distance, rail_distance, self.singletonVerMesa.alto_mesa - rail_distance]
                                )
                                * ZOOM_MULTIPLIER
                            ).astype(int)
            print("Alto de mesa segun singleton-----------------" + str(self.singletonVerMesa.alto_mesa))
            rail_poly = [
                            [
                                [0, CORNER_RAIL_OFFSET],
                                [rail_location[0], rail_location[2] + CORNER_RAIL_OFFSET],
                                [rail_location[0], rail_location[3] - CORNER_RAIL_OFFSET],
                                [0, int(self.singletonVerMesa.alto_mesa * ZOOM_MULTIPLIER) - CORNER_RAIL_OFFSET],
                            ],  # left
                            [
                                [CORNER_RAIL_OFFSET, 0],
                                [int(self.singletonVerMesa.ancho_mesa * ZOOM_MULTIPLIER / 2) - SIDE_RAIL_OFFSET_2, 0],
                                [
                                    int(self.singletonVerMesa.ancho_mesa * ZOOM_MULTIPLIER / 2) - SIDE_RAIL_OFFSET - SIDE_RAIL_OFFSET_2,
                                    rail_location[2],
                                ],
                                [rail_location[0] + CORNER_RAIL_OFFSET, rail_location[2]],
                            ],  # top 1
                            [
                                [int(self.singletonVerMesa.ancho_mesa * ZOOM_MULTIPLIER / 2) + SIDE_RAIL_OFFSET_2, 0],
                                [int(self.singletonVerMesa.ancho_mesa * ZOOM_MULTIPLIER) - CORNER_RAIL_OFFSET, 0],
                                [rail_location[1] - CORNER_RAIL_OFFSET, rail_location[2]],
                                [
                                    int(self.singletonVerMesa.ancho_mesa * ZOOM_MULTIPLIER / 2) + SIDE_RAIL_OFFSET + SIDE_RAIL_OFFSET_2,
                                    rail_location[2],
                                ],
                            ],  # top 2
                            [
                                [rail_location[1], rail_location[2] + CORNER_RAIL_OFFSET],
                                [int(self.singletonVerMesa.ancho_mesa * ZOOM_MULTIPLIER), CORNER_RAIL_OFFSET],
                                [
                                    int(self.singletonVerMesa.ancho_mesa * ZOOM_MULTIPLIER),
                                    int(self.singletonVerMesa.alto_mesa * ZOOM_MULTIPLIER) - CORNER_RAIL_OFFSET,
                                ],
                                [rail_location[1], rail_location[3] - CORNER_RAIL_OFFSET],
                            ],  # right
                            [
                                [rail_location[0] + CORNER_RAIL_OFFSET, rail_location[3]],
                                [
                                    int(self.singletonVerMesa.ancho_mesa * ZOOM_MULTIPLIER / 2) - SIDE_RAIL_OFFSET - SIDE_RAIL_OFFSET_2,
                                    rail_location[3],
                                ],
                                [
                                    int(self.singletonVerMesa.ancho_mesa * ZOOM_MULTIPLIER / 2) - SIDE_RAIL_OFFSET_2,
                                    int(self.singletonVerMesa.alto_mesa * ZOOM_MULTIPLIER),
                                ],
                                [CORNER_RAIL_OFFSET, int(self.singletonVerMesa.alto_mesa * ZOOM_MULTIPLIER)],
                            ],  # bottom 1
                            [
                                [
                                    int(self.singletonVerMesa.ancho_mesa * ZOOM_MULTIPLIER / 2) + SIDE_RAIL_OFFSET + SIDE_RAIL_OFFSET_2,
                                    rail_location[3],
                                ],
                                [rail_location[1] - CORNER_RAIL_OFFSET, rail_location[3]],
                                [
                                    int(self.singletonVerMesa.ancho_mesa * ZOOM_MULTIPLIER) - CORNER_RAIL_OFFSET,
                                    int(self.singletonVerMesa.alto_mesa * ZOOM_MULTIPLIER),
                                ],
                                [
                                    int(self.singletonVerMesa.ancho_mesa * ZOOM_MULTIPLIER / 2) + SIDE_RAIL_OFFSET_2,
                                    int(self.singletonVerMesa.alto_mesa * ZOOM_MULTIPLIER),
                                ],
                            ],  # bottom 2
                        ]
            
            for rail_poly_item in rail_poly:
                rail = pm.Poly(static_body, rail_poly_item)
                rail.color = pg.Color(TABLE_SIDE_COLOR)
                rail.collision_type = 3
                rail.elasticity = RAIL_ELASTICITY
                if self.default == True:  
                    rail.friction = RAIL_FRICTION
                else:
                    rail.friction = self.singletonVerMesa.friccion_railes
                rail.filter = pm.ShapeFilter(categories=0b00001)
                self.rails.append(rail) 
        else:
            if self.default == True:
                for rail_poly in RAIL_POLY:
                    rail = pm.Poly(static_body, rail_poly)
                    rail.color = pg.Color(TABLE_SIDE_COLOR)
                    rail.collision_type = 3
                    rail.elasticity = RAIL_ELASTICITY
                    if self.default == True:  
                        rail.friction = RAIL_FRICTION
                    else:
                        rail.friction = self.singleton.friccion_railes
                    rail.filter = pm.ShapeFilter(categories=0b00001)
                    self.rails.append(rail)
            else:
                rail_distance = int(self.singleton.distancia_railes*ZOOM_MULTIPLIER)
                rail_location = (
                                    np.array(
                                        [rail_distance, self.singleton.ancho_mesa - rail_distance, rail_distance, self.singleton.alto_mesa - rail_distance]
                                    )
                                    * ZOOM_MULTIPLIER
                                ).astype(int)
                print("Alto de mesa segun singleton-----------------" + str(self.singleton.alto_mesa))
                rail_poly = [
                                [
                                    [0, CORNER_RAIL_OFFSET],
                                    [rail_location[0], rail_location[2] + CORNER_RAIL_OFFSET],
                                    [rail_location[0], rail_location[3] - CORNER_RAIL_OFFSET],
                                    [0, int(self.singleton.alto_mesa * ZOOM_MULTIPLIER) - CORNER_RAIL_OFFSET],
                                ],  # left
                                [
                                    [CORNER_RAIL_OFFSET, 0],
                                    [int(self.singleton.ancho_mesa * ZOOM_MULTIPLIER / 2) - SIDE_RAIL_OFFSET_2, 0],
                                    [
                                        int(self.singleton.ancho_mesa * ZOOM_MULTIPLIER / 2) - SIDE_RAIL_OFFSET - SIDE_RAIL_OFFSET_2,
                                        rail_location[2],
                                    ],
                                    [rail_location[0] + CORNER_RAIL_OFFSET, rail_location[2]],
                                ],  # top 1
                                [
                                    [int(self.singleton.ancho_mesa * ZOOM_MULTIPLIER / 2) + SIDE_RAIL_OFFSET_2, 0],
                                    [int(self.singleton.ancho_mesa * ZOOM_MULTIPLIER) - CORNER_RAIL_OFFSET, 0],
                                    [rail_location[1] - CORNER_RAIL_OFFSET, rail_location[2]],
                                    [
                                        int(self.singleton.ancho_mesa * ZOOM_MULTIPLIER / 2) + SIDE_RAIL_OFFSET + SIDE_RAIL_OFFSET_2,
                                        rail_location[2],
                                    ],
                                ],  # top 2
                                [
                                    [rail_location[1], rail_location[2] + CORNER_RAIL_OFFSET],
                                    [int(self.singleton.ancho_mesa * ZOOM_MULTIPLIER), CORNER_RAIL_OFFSET],
                                    [
                                        int(self.singleton.ancho_mesa * ZOOM_MULTIPLIER),
                                        int(self.singleton.alto_mesa * ZOOM_MULTIPLIER) - CORNER_RAIL_OFFSET,
                                    ],
                                    [rail_location[1], rail_location[3] - CORNER_RAIL_OFFSET],
                                ],  # right
                                [
                                    [rail_location[0] + CORNER_RAIL_OFFSET, rail_location[3]],
                                    [
                                        int(self.singleton.ancho_mesa * ZOOM_MULTIPLIER / 2) - SIDE_RAIL_OFFSET - SIDE_RAIL_OFFSET_2,
                                        rail_location[3],
                                    ],
                                    [
                                        int(self.singleton.ancho_mesa * ZOOM_MULTIPLIER / 2) - SIDE_RAIL_OFFSET_2,
                                        int(self.singleton.alto_mesa * ZOOM_MULTIPLIER),
                                    ],
                                    [CORNER_RAIL_OFFSET, int(self.singleton.alto_mesa * ZOOM_MULTIPLIER)],
                                ],  # bottom 1
                                [
                                    [
                                        int(self.singleton.ancho_mesa * ZOOM_MULTIPLIER / 2) + SIDE_RAIL_OFFSET + SIDE_RAIL_OFFSET_2,
                                        rail_location[3],
                                    ],
                                    [rail_location[1] - CORNER_RAIL_OFFSET, rail_location[3]],
                                    [
                                        int(self.singleton.ancho_mesa * ZOOM_MULTIPLIER) - CORNER_RAIL_OFFSET,
                                        int(self.singleton.alto_mesa * ZOOM_MULTIPLIER),
                                    ],
                                    [
                                        int(self.singleton.ancho_mesa * ZOOM_MULTIPLIER / 2) + SIDE_RAIL_OFFSET_2,
                                        int(self.singleton.alto_mesa * ZOOM_MULTIPLIER),
                                    ],
                                ],  # bottom 2
                            ]
                
                for rail_poly_item in rail_poly:
                    rail = pm.Poly(static_body, rail_poly_item)
                    rail.color = pg.Color(TABLE_SIDE_COLOR)
                    rail.collision_type = 3
                    rail.elasticity = RAIL_ELASTICITY
                    if self.default == True:  
                        rail.friction = RAIL_FRICTION
                    else:
                        rail.friction = self.singleton.friccion_railes
                    rail.filter = pm.ShapeFilter(categories=0b00001)
                    self.rails.append(rail)    
            

        self.pockets = []

        if self.verMesa:
            side_pocket_dist = int(self.singletonVerMesa.distancia_troneras_medias*ZOOM_MULTIPLIER)
            corner_pocket_dist = int(self.singletonVerMesa.distancia_troneras_esquinas*ZOOM_MULTIPLIER)
            pocket_location = (
                    np.array(
                        [
                        (corner_pocket_dist, corner_pocket_dist),
                        (self.singletonVerMesa.ancho_mesa // 2, side_pocket_dist),
                        (self.singletonVerMesa.ancho_mesa - corner_pocket_dist, corner_pocket_dist),
                        (corner_pocket_dist, self.singletonVerMesa.alto_mesa - corner_pocket_dist),
                        (self.singletonVerMesa.ancho_mesa // 2, self.singletonVerMesa.alto_mesa - side_pocket_dist),
                        (self.singletonVerMesa.ancho_mesa - corner_pocket_dist, self.singletonVerMesa.alto_mesa - corner_pocket_dist),
                        ]
                    )
                    * ZOOM_MULTIPLIER
                ).astype(int)
            
            for pocket_loc in pocket_location:
                pocket = pm.Circle(static_body, POCKET_RADIUS, pocket_loc.tolist())
                pocket.color = pg.Color(BLACK)
                pocket.collision_type = 2
                pocket.elasticity = 0
                pocket.friction = 0
                pocket.filter = pm.ShapeFilter(categories=0b00010)
                self.pockets.append(pocket)
        else:
            if self.default == True:
                for pocket_loc in POCKET_LOCATION_RESTO:
                    pocket = pm.Circle(static_body, POCKET_RADIUS, pocket_loc.tolist())
                    pocket.color = pg.Color(TABLE_SIDE_COLOR)
                    pocket.collision_type = 5
                    pocket.elasticity = 0
                    pocket.friction = 0
                    pocket.filter = pm.ShapeFilter(categories=0b00001)
                    self.pockets.append(pocket)

                for pocket_loc in POCKET_LOCATION:
                    pocket = pm.Circle(static_body, POCKET_RADIUS, pocket_loc.tolist())
                    pocket.color = pg.Color(BLACK)
                    pocket.collision_type = 2
                    pocket.elasticity = 0
                    pocket.friction = 0
                    pocket.filter = pm.ShapeFilter(categories=0b00010)
                    self.pockets.append(pocket)
            else:
                side_pocket_dist = int(self.singleton.distancia_troneras_medias*ZOOM_MULTIPLIER)
                corner_pocket_dist = int(self.singleton.distancia_troneras_esquinas*ZOOM_MULTIPLIER)
                pocket_location = (
                        np.array(
                            [
                            (corner_pocket_dist, corner_pocket_dist),
                            (self.singleton.ancho_mesa // 2, side_pocket_dist),
                            (self.singleton.ancho_mesa - corner_pocket_dist, corner_pocket_dist),
                            (corner_pocket_dist, self.singleton.alto_mesa - corner_pocket_dist),
                            (self.singleton.ancho_mesa // 2, self.singleton.alto_mesa - side_pocket_dist),
                            (self.singleton.ancho_mesa - corner_pocket_dist, self.singleton.alto_mesa - corner_pocket_dist),
                            ]
                        )
                        * ZOOM_MULTIPLIER
                    ).astype(int)
                
                for pocket_loc in pocket_location:
                    pocket = pm.Circle(static_body, POCKET_RADIUS, pocket_loc.tolist())
                    pocket.color = pg.Color(BLACK)
                    pocket.collision_type = 2
                    pocket.elasticity = 0
                    pocket.friction = 0
                    pocket.filter = pm.ShapeFilter(categories=0b00010)
                    self.pockets.append(pocket)


        self.space.add(*self.rails, *self.pockets)

    
    def remove_all_balls(self):
        for ball in self.balls:
            self.space.remove(ball)


    def setear_bolas(self):
        global trayectorias
        trayectorias = [[] for _ in range(len(self.singleton.listaApareada))]
        self.balls = []
        self.balls_copy = []
        self.num_balls = len(self.singleton.listaApareada)
        positions = []

        
        contadorLisas = 0
        contadorRayadas = 8
        for i, bola in enumerate(self.singleton.listaApareada):
            (x,y,r), _, etiqueta = bola
            if (self.singleton.mesaAbierta == True):
                contadorLisas = contadorLisas + 1
                #No se puede elegir embocar la negra si tengo Mesa abierta
                self.singleton.embocarNegra = False
            else:
                if(etiqueta == "Lisa" and self.singleton.etiquetaDeSeleccionada=="Lisa" ):
                    contadorLisas = contadorLisas + 1
                elif (etiqueta == "Rayada" and self.singleton.etiquetaDeSeleccionada == "Lisa"):
                    contadorRayadas = contadorRayadas + 1
                elif(etiqueta == "Lisa" and self.singleton.etiquetaDeSeleccionada == "Rayada"):
                    contadorRayadas = contadorRayadas + 1
                elif(etiqueta == "Rayada" and self.singleton.etiquetaDeSeleccionada == "Rayada"):
                    contadorLisas = contadorLisas +1
                elif(etiqueta == "Lisa" and self.singleton.etiquetaDeSeleccionada == "Negra"):
                    contadorRayadas = contadorRayadas +1
                elif(etiqueta == "Rayada" and self.singleton.etiquetaDeSeleccionada == "Negra"):
                    contadorRayadas = contadorRayadas +1
            x, y = self.transformar_coordenadas((x,y),self.singleton.ancho, self.singleton.alto)
            position = self.create_ball(etiqueta,(x,y),self.singleton.etiquetaDeSeleccionada,self.singleton.embocarNegra,contadorLisas,contadorRayadas,True)
            positions.append(position)
        
        return positions, contadorLisas, contadorRayadas
    
    def get_number_key(self, bola):
        return bola.number
            
    def transformar_coordenadas(self, punto, ancho, alto):
        if self.default==True:
            self.ancho_ratio = (WIDTH-(RAIL_DISTANCE*2))/ancho
            self.alto_ratio = (HEIGHT-(RAIL_DISTANCE*2))/alto
            x,y = punto
            transformadaX = (x*self.ancho_ratio)+CORNER_POCKET_DIST
            transformadaY = (y*self.alto_ratio)+CORNER_POCKET_DIST
        else:
            rail_distance = int(self.singleton.distancia_railes*ZOOM_MULTIPLIER)
            self.ancho_ratio = (self.singleton.ancho_mesa-(rail_distance*2))/ancho
            self.alto_ratio = (self.singleton.alto_mesa-(rail_distance*2))/alto
            x,y = punto
            corner_pocket_dist =  int(self.singleton.distancia_troneras_esquinas*ZOOM_MULTIPLIER)
            transformadaX = (x*self.ancho_ratio)+corner_pocket_dist
            transformadaY = (y*self.alto_ratio)+corner_pocket_dist
        return transformadaX, transformadaY
    
    def destransformar_coordenadas(self, punto):
        x,y = punto
        if self.default == True:
            if(self.ancho_ratio != 0 and self.alto_ratio != 0):
                destransformadaX = (x-CORNER_POCKET_DIST)/self.ancho_ratio
                destransformadaY = (y-CORNER_POCKET_DIST)/self.alto_ratio
                return (destransformadaX, destransformadaY)
        else:
            if(self.ancho_ratio != 0 and self.alto_ratio != 0):
                corner_pocket_dist = int(self.singleton.distancia_troneras_esquinas*ZOOM_MULTIPLIER)
                destransformadaX = (x-corner_pocket_dist)/self.ancho_ratio
                destransformadaY = (y-corner_pocket_dist)/self.alto_ratio
                return (destransformadaX, destransformadaY)
        return (0,0)
    
    def obtenerEtiquetaSeleccionada(self, listaApareada, bolaSeleccionada):
        (xs,ys,rs) = bolaSeleccionada
        for bola in listaApareada:
            (x,y,r),_,etiqueta = bola
            if(x,y)==(xs,ys):
                return etiqueta
        return None

        
    #al crear las bolas tener en cuenta que la IA siempre mete las lisas
    def create_ball(self, etiqueta, coordenada, etiquetaDeSeleccionada, embocarNegra, contadorSolidas, contadorRayadas, agregarSpace):
        global trayectoriaBlanca,trayectorias
        if self.default == True:
            intertia = pm.moment_for_circle(BALL_MASS, 0, BALL_RADIUS, offset=(0, 0))
        else:
            intertia = pm.moment_for_circle(BALL_MASS, 0, int(self.singleton.tam_bolas_simulacion * ZOOM_MULTIPLIER), offset=(0, 0))
        ball_body = pm.Body(BALL_MASS, intertia)
        ball_body.position = coordenada
        if self.default == True:
            ball = pm.Circle(ball_body, BALL_RADIUS, offset=(0, 0))
        else:
            ball = pm.Circle(ball_body, int(self.singleton.tam_bolas_simulacion * ZOOM_MULTIPLIER), offset=(0, 0))
        ball.elasticity = BALL_ELASTICITY
        if self.default == True:
            ball.friction = BALL_FRICTION
        else:
            ball.friction = self.singleton.friccion_bolas
        ball.collision_type = 1
        ball.filter = pm.ShapeFilter(categories=0b00100)
        ball.userData = etiqueta
        
        if self.singleton.mesaAbierta == True:
            if etiqueta == "Blanca":
                    self.cue_ball = ball
                    ball.observation_number = 4
                    ball.color = pg.Color(WHITE)
                    ball.number = 0
                    trayectoriaBlanca.append(self.destransformar_coordenadas(ball.body.position))

            if etiqueta == "Negra":
                ball.color = pg.Color(BLACK)
                ball.observation_number = 3
                ball.filter = pm.ShapeFilter(categories=0b10000)
                ball.number = 8

            if etiqueta == "Rayada" or etiqueta == "Lisa":
                ball.color = pg.Color(SOLIDS_COLOR)
                ball.observation_number = 1
                ball.filter = pm.ShapeFilter(categories=0b01000)
                ball.number = contadorSolidas

        else:
            if embocarNegra==False:
                if etiqueta == "Blanca":
                    self.cue_ball = ball
                    ball.observation_number = 4
                    ball.color = pg.Color(WHITE)
                    ball.number = 0
                    trayectoriaBlanca.append(self.destransformar_coordenadas(ball.body.position))
                
                if etiqueta == "Negra":
                    ball.color = pg.Color(BLACK)
                    ball.observation_number = 3
                    ball.filter = pm.ShapeFilter(categories=0b10000)
                    ball.number = 8

                if etiqueta=="Lisa" and etiquetaDeSeleccionada=="Lisa":
                    ball.color = pg.Color(SOLIDS_COLOR)
                    ball.observation_number = 1
                    ball.filter = pm.ShapeFilter(categories=0b01000)
                    ball.number = contadorSolidas

                if etiqueta=="Rayada" and etiquetaDeSeleccionada=="Lisa":
                    ball.color = pg.Color(STRIPS_COLOR)
                    ball.observation_number = 2
                    ball.number = contadorRayadas
                
                if etiqueta=="Lisa" and etiquetaDeSeleccionada=="Rayada":
                    ball.color = pg.Color(STRIPS_COLOR)
                    ball.observation_number = 2
                    ball.number = contadorRayadas
                
                if etiqueta=="Rayada" and etiquetaDeSeleccionada=="Rayada":
                    ball.color = pg.Color(SOLIDS_COLOR)
                    ball.observation_number = 1
                    ball.filter = pm.ShapeFilter(categories=0b01000)
                    ball.number = contadorSolidas
            else:
                if etiqueta == "Blanca":
                    self.cue_ball = ball
                    ball.observation_number = 4
                    ball.color = pg.Color(WHITE)
                    ball.number = 0
                    trayectoriaBlanca.append(self.destransformar_coordenadas(ball_body.position))

                if etiqueta == "Negra":
                    ball.color = pg.Color(BLACK)
                    ball.observation_number = 3
                    ball.filter = pm.ShapeFilter(categories=0b10000)
                    ball.number = 8

                if etiqueta=="Rayada" or etiqueta=="Lisa":
                    ball.color = pg.Color(STRIPS_COLOR)
                    ball.observation_number = 2
                    ball.number = contadorRayadas
        #Respetar el orden del codigo
        if etiqueta != 'Blanca':
            trayectorias[len(self.balls)].append(self.destransformar_coordenadas(ball.body.position))
        self.balls.append(ball)
        self.balls_copy.append(ball.copy())
        if(agregarSpace):
            self.space.add(ball, ball_body)
        return ball_body.position


    def add_balls(self):
        # 0 -> cue-ball, 1-7 --> solids, 8 --> 8-ball, 9-15 -- strips
        self.balls = []
        self.balls_copy = []
        if self.default == False:
            positions, cantLisas, cantRayadas = self.setear_bolas()
            return
        
        positions = []
        if self.ver_mesa:
            ball_radius = int(self.singletonVerMesa.tam_bolas_simulacion* ZOOM_MULTIPLIER)
            rail_distance = int(self.singletonVerMesa.distancia_railes* ZOOM_MULTIPLIER)
        else:
            ball_radius = BALL_MASS
            rail_distance = RAIL_DISTANCE
        for i in range(self.num_balls):
                if self.default == True:
                    intertia = pm.moment_for_circle(BALL_MASS, 0, ball_radius, offset=(0, 0))
                else:
                    intertia = pm.moment_for_circle(BALL_MASS, 0, int(self.singleton.tam_bolas_simulacion * ZOOM_MULTIPLIER), offset=(0, 0))
                ball_body = pm.Body(BALL_MASS, intertia)

                # initialize ball at random position
                if self.num_balls < 2:
                    ball_body.position = random.choice(HANGING_BALL_LOCATION).tolist()
                else:
                    ball_body.position = random.randint(
                        rail_distance * 2, self.width - rail_distance * 2
                    ), random.randint(rail_distance * 2, self.height - rail_distance * 2)

                # if overlap with another ball, choose a different location
                if self.verMesa:
                    auxRadio = int(self.singletonVerMesa.tam_bolas_simulacion * ZOOM_MULTIPLIER)
                else:
                    if self.default == True:
                        auxRadio = BALL_RADIUS
                    else:
                        auxRadio = int(self.singleton.tam_bolas_simulacion * ZOOM_MULTIPLIER)
                
                while 1:
                    for pos in positions:
                            if (
                                distance_between_two_points(ball_body.position, pos)
                                < auxRadio * 2
                            ):
                                break
                    else:
                        break
                    if self.num_balls < 2:
                        ball_body.position = random.choice(HANGING_BALL_LOCATION).tolist()
                    else:
                        ball_body.position = random.randint(
                            rail_distance * 2, self.width - rail_distance * 2
                        ), random.randint(
                            rail_distance * 2, self.height - rail_distance * 2
                        )
                if self.default == True:
                    ball = pm.Circle(ball_body, ball_radius, offset=(0, 0))
                else:
                    ball = pm.Circle(ball_body, int(self.singleton.tam_bolas_simulacion * ZOOM_MULTIPLIER), offset=(0, 0))
                ball.elasticity = BALL_ELASTICITY
                ball.friction = BALL_FRICTION
                ball.collision_type = 1
                ball.number = i
                ball.filter = pm.ShapeFilter(categories=0b00100)
                ball.userData="default"

                # separate ball types
                # observation_number: pocketed 0, solid 1, strips 2, 8-ball 3, cue-ball 4
                if i == 0:
                    ball.color = pg.Color(WHITE)
                    ball.observation_number = 4
                    self.cue_ball = ball
                elif i < 8:
                    ball.color = pg.Color(SOLIDS_COLOR)
                    ball.observation_number = 1
                    ball.filter = pm.ShapeFilter(categories=0b01000)
                elif i == 8:
                    ball.color = pg.Color(BLACK)
                    ball.observation_number = 3
                    ball.filter = pm.ShapeFilter(categories=0b10000)
                else:
                    ball.color = pg.Color(STRIPS_COLOR)
                    ball.observation_number = 2

                positions.append(ball_body.position)
                self.balls.append(ball)
                self.space.add(ball, ball_body)
            

    
    def ball_contacted(self, arbiter, space, data):
        global trayectoriaBlanca, trayectorias
        # count bank/carrom shot collisions
        global primerContacto, cantidadRebotesBlanca, primerContactoCoordenada
        ball_shape_1, ball_shape_2 = arbiter.shapes

        if(ball_shape_1.userData == "Blanca" or ball_shape_2.userData == "Blanca"):
            cantidadRebotesBlanca = cantidadRebotesBlanca + 1

        if(ball_shape_1.userData=="Blanca" and primerContacto == None):
            primerContacto = ball_shape_2
        if ball_shape_1.userData=="Blanca" and primerContactoCoordenada == None:
            primerContactoCoordenada = ball_shape_2.copy()
            
        elif (ball_shape_2.userData == "Blanca" and primerContacto == None):
            primerContacto = ball_shape_1 
        if ball_shape_2.userData == "Blanca"  and primerContactoCoordenada == None:
            primerContactoCoordenada = ball_shape_1.copy()

        if( trayectorias is not None ):
            if(ball_shape_1.userData == 'Blanca' ):
                trayectoriaBlanca.append(self.destransformar_coordenadas(ball_shape_1.body.position))
                indexBall2 = self.balls_copy.index(ball_shape_2)
                trayectorias[indexBall2].append(self.destransformar_coordenadas(ball_shape_2.body.position))
            elif(ball_shape_2.userData == 'Blanca'):
                trayectoriaBlanca.append(self.destransformar_coordenadas(ball_shape_2.body.position))
                indexBall1 = self.balls_copy.index(ball_shape_1)
                trayectorias[indexBall1].append(self.destransformar_coordenadas(ball_shape_1.body.position))
            else:
                indexBall1 = self.balls_copy.index(ball_shape_1)
                indexBall2 = self.balls_copy.index(ball_shape_2)
                trayectorias[indexBall1].append(self.destransformar_coordenadas(ball_shape_1.body.position))
                trayectorias[indexBall2].append(self.destransformar_coordenadas(ball_shape_2.body.position))        

        if (
            data["pocket_tracking"]["first_contacted_ball"] in arbiter.shapes
            and not data["pocket_tracking"]["potted_balls"]
        ):
            data["pocket_tracking"]["fcb_collision_count"] += 1

        cb, bs = {data["cue_ball"]}, set(arbiter.shapes)
        if bs.issuperset(cb):
            other_ball = bs.difference(cb).pop()
            if data["pocket_tracking"]["first_contacted_ball"] is None:
                data["pocket_tracking"]["first_contacted_ball"] = other_ball
        return True

    def ball_pocketed_falso(self, arbiter, space, data):
        global bolasEmbocadas, trayectorias, trayectoriaBlanca
        ball, pocket = arbiter.shapes
        bolasEmbocadas.append(ball.copy())

        try:
            data["balls"].remove(ball)
        except ValueError:
            pass
        space.remove(ball, ball.body)
        return False

        

    def ball_pocketed(self, arbiter, space, data):
        global bolasEmbocadas, trayectorias, trayectoriaBlanca
        # arbiter: [ball, pocket]
        ball, pocket = arbiter.shapes
        data["pocket_tracking"]["potted_balls"].append(ball.number)
        bolasEmbocadas.append(ball.copy())

        if (ball.userData == 'Blanca'):
            trayectoriaBlanca.append(self.destransformar_coordenadas(ball.body.position))
        elif ( trayectorias is not None ):
            index = self.balls_copy.index(ball)
            trayectorias[index].append(self.destransformar_coordenadas(ball.body.position))
    
        if ball.number == 0:
            data["pocket_tracking"]["cue_ball_pocketed"] = True
        elif ball.number == 8:
            # check for solids winning
            data["pocket_tracking"]["black_ball_pocketed"] = True
            if (
                any([b.number >= 1 and b.number <= 7 for b in data["balls"]])
                or data["pocket_tracking"]["first_contacted_ball"].number != 8
            ):
                data["pocket_tracking"]["is_won"] = False
            else:
                data["pocket_tracking"]["is_won"] = True
        elif 1 <= ball.number <= 7:
            data["pocket_tracking"]["total_potted_balls"] += 1

        try:
            data["balls"].remove(ball)
        except ValueError:
            pass
        space.remove(ball, ball.body)
        return False

    
    def rail_contacted(self, arbiter, space, data):
        global cantidadRebotesBlanca, trayectorias, trayectoriaBlanca, bolasEmbocadas, primerContactoCoordenada
        ball, rail = arbiter.shapes
  
        if(ball.userData == "Blanca"):
            cantidadRebotesBlanca = cantidadRebotesBlanca + 1
            trayectoriaBlanca.append(self.destransformar_coordenadas(ball.body.position))
            if primerContactoCoordenada is None:
                if(self.default == False):
                    if ball.body.position.x > (self.singleton.ancho_mesa/2):
                        primerContactoCoordenada = 1
                else:
                    if ball.body.position.x > (WIDTH/2):
                        primerContactoCoordenada = 1

        elif( trayectorias is not None ):
            index = self.balls_copy.index(ball)
            trayectorias[index].append(self.destransformar_coordenadas(ball.body.position))
        if (
            data["pocket_tracking"]["first_contacted_ball"] == ball
            and not data["pocket_tracking"]["potted_balls"]
        ):
            data["pocket_tracking"]["fcb_collision_count"] += 1

        if ball.number == 0 and data["pocket_tracking"]["first_contacted_ball"] is None:
            data["pocket_tracking"]["rail_collision_count"] += 1

        return True

    def redraw_screen(self):
        if self.draw_screen:
            self.screen.fill(pg.Color(TABLE_COLOR))
            self.space.debug_draw(self.draw_options)
            pg.display.flip()
            self.clock.tick(FPS)

    def process_events(self):
        if self.draw_screen == True:
            for event in pg.event.get():
                if (
                    event.type == pg.QUIT
                    or event.type == pg.KEYDOWN
                    and event.key == pg.K_q
                ):
                    self.running = False

    def process_action(self, action):
        if self.default == True:
            velocidades = (np.array(action) * VELOCITY_LIMIT).tolist()
        else:
            velocidades = (np.array(action) * int(self.singleton.limite_velocidad * ZOOM_MULTIPLIER)).tolist()
        return velocidades

    def process_observation(self):
        if self.observation_type == "image":
            img = pg.surfarray.pixels3d(self.screen)
            image_height = IMAGE_HEIGHT
            
            if(self.default == False):
                print(image_height)
                image_height = int(IMAGE_WIDTH * (self.singleton.alto_mesa / self.singleton.ancho_mesa) )
                img = cv2.resize(img, (IMAGE_WIDTH, image_height))
            else:
                img = cv2.resize(img, (IMAGE_WIDTH, IMAGE_HEIGHT))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.rotate(img, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
            img = cv2.flip(img, 0)

            # cv2.imshow("", cv2.resize(img, (300, 300)))
            # if cv2.waitKey(1) == ord("q"):
            #    os._exit(0)
            if(self.default == False):
                return img.reshape(3, int(IMAGE_WIDTH * (self.singleton.alto_mesa / self.singleton.ancho_mesa) ), IMAGE_WIDTH)
            else:
                return img.reshape(3, IMAGE_HEIGHT, image_height)
            # return (img.reshape(3, IMAGE_HEIGHT, IMAGE_WIDTH) if (self.default) else img.reshape(3, IMAGE_HEIGHT, image_height))
        elif self.observation_type == "vector":
            # observation_number: pocketed 0, solid 1, strips 2, 8-ball 3, cue-ball 4
            width_multiplier = (IMAGE_WIDTH / (self.width)) / IMAGE_WIDTH
            if(self.default == False):
                image_height = int(IMAGE_WIDTH * (self.singleton.alto_mesa / self.singleton.ancho_mesa) )
                height_multiplier = (image_height / (self.height)) / image_height
            else: 
                height_multiplier = (IMAGE_HEIGHT / (self.height)) / IMAGE_HEIGHT
            obs = np.array(
                [
                    np.array(
                        [
                            x.body.position[0] * width_multiplier,
                            x.body.position[1] * height_multiplier,
                            x.observation_number / 4,
                        ]
                    )
                    for x in self.balls
                ]
            )

            balls_to_fill = self.num_balls - len(self.balls)
            if len(self.balls) == 0:
                # if no balls on table
                obs = (
                    np.repeat(np.array([0, 0, 0]), balls_to_fill, axis=0)
                    .reshape(balls_to_fill, 3)
                    .flatten()
                )
            if balls_to_fill > 0:
                # if some balls are pocketed
                obs = np.vstack(
                    (
                        obs,
                        np.repeat(np.array([0, 0, 0]), balls_to_fill, axis=0).reshape(
                            balls_to_fill, 3
                        ),
                    )
                ).flatten()
            else:
                obs = obs.flatten()
            obs = np.concatenate([obs, self.table_info])
            return obs
        else:
            return

    def process_reward(self, reward=None):
        # normalizing the reward to range(-1, 1)
        if reward is None:
            reward = self.reward
        if self.reward_by_steps:
            return np.clip((reward / 50) * 2 - 1, -1, 1)
        else:
            return np.clip((reward / 500) * 2 - 1, -1, 1)

    def setear_respuesta(self):
        global bolasCorrectasEmbocadas, bolasIncorrectasEmbocadas, embocoLaNegraIncorrectamente, primerContactoCorrecto, trayectoriaBlanca, trayectorias
        tiroValido = True
        for bola in bolasEmbocadas:
            if bola.userData == self.singleton.etiquetaDeSeleccionada:
                bolasCorrectasEmbocadas = bolasCorrectasEmbocadas + 1 
            else:
                bolasIncorrectasEmbocadas = bolasIncorrectasEmbocadas + 1
                self.tiroValido = False

            if self.singleton.embocarNegra == False and bola.userData == "Negra":
                embocoLaNegraIncorrectamente = True
                tiroValido = False
            if bola.userData == "Blanca":
                tiroValido = False

        if primerContacto is not None:
            if primerContacto.userData == self.singleton.etiquetaDeSeleccionada:
                primerContactoCorrecto = True
            else:
                primerContactoCorrecto = False
                tiroValido = False
        else:
            primerContactoCorrecto = False
            tiroValido = False
        return Respuesta(primerContactoCorrecto, bolasCorrectasEmbocadas, bolasIncorrectasEmbocadas, embocoLaNegraIncorrectamente, velocidadXBlanca, velocidadYBlanca, cantidadRebotesBlanca, tiroValido, trayectorias ,trayectoriaBlanca, self.attrs_respuesta, self.best_player_respuesta)

    def verificarBolaEnMano(self):
        global primerContactoCoordenada
        reward = 1
        if BOLA_EN_MANO == False:
            return reward
        if primerContactoCoordenada is not None and primerContactoCoordenada != 1:
            if(self.default == False):
                if primerContactoCoordenada.body.position[0] < (self.singleton.ancho_mesa/2):
                    self.bola_en_mano_error = True
                    self.reward = 0
            else: 
                if primerContactoCoordenada.body.position[0] < (WIDTH/2):
                    self.bola_en_mano_error = True
                    self.reward = 0
        print(self.process_reward())
        return reward


    def step(self, action, *args, **kwargs):
        global velocidadXBlanca, velocidadYBlanca
        self.best_player_respuesta = action
        # waiting for all balls to stop
        action = self.process_action(action)
        velocidadXBlanca = action[0]
        velocidadYBlanca = action[1]
        self.cue_ball.body.activate()
        pm.Body.update_velocity(self.cue_ball.body, action, damping=0, dt=1)

        # reset some constants
        done = False
        info = {}
        if self.reward_by_steps:
            self.reward = 7
        closest_ball_dist = 1e6
        closest_pocket_dist = 1e6
        self.pocket_tracking["potted_balls"].clear()
        self.pocket_tracking["fcb_collision_count"] = 0
        self.pocket_tracking["rail_collision_count"] = 0
        self.pocket_tracking["cue_ball_pocketed"] = False
        self.pocket_tracking["first_contacted_ball"] = None
        while self.running:
            # check if all balls stopped
            for ball in self.balls:
                if not ball.body.is_sleeping:
                    break
            else:
                break

            # reward for how close cue_ball to ball and ball to pocket
            fcb = self.pocket_tracking["first_contacted_ball"]
            if self.score_tracking["pot_count"] == 7:
                if fcb is None:
                    bl = self.space.point_query_nearest(
                        tuple(self.cue_ball.body.position),
                        self.width * 0.8,
                        pm.ShapeFilter(mask=pm.ShapeFilter.ALL_MASKS() ^ 0b01111),
                    )
                    if bl is not None:
                        closest_ball_dist = min(bl.distance, closest_ball_dist)
                elif fcb.number == 8:
                    poc = self.space.point_query_nearest(
                        tuple(fcb.body.position),
                        self.width * 0.5,
                        pm.ShapeFilter(mask=pm.ShapeFilter.ALL_MASKS() ^ 0b11101),
                    )
                    if poc is not None:
                        closest_pocket_dist = min(poc.distance, closest_pocket_dist)
            elif fcb is None:
                # filter out everything but balls
                bl = self.space.point_query_nearest(
                    tuple(self.cue_ball.body.position),
                    self.width * 0.8,
                    pm.ShapeFilter(mask=pm.ShapeFilter.ALL_MASKS() ^ 0b10111),
                )
                if bl is not None:
                    closest_ball_dist = min(bl.distance, closest_ball_dist)
            elif 1 <= fcb.number <= 7:
                # filter out everything but pockets
                poc = self.space.point_query_nearest(
                    tuple(fcb.body.position),
                    self.width * 0.5,
                    pm.ShapeFilter(mask=pm.ShapeFilter.ALL_MASKS() ^ 0b11101),
                )
                if poc is not None:
                    closest_pocket_dist = min(poc.distance, closest_pocket_dist)

            # step through
            if not self.training:
                self.process_events()
                self.redraw_screen()
                self.space.step(self.step_size / self.dt)
            else:
                for _ in range(self.dt):
                    self.space.step(self.step_size / self.dt)

        
        if (trayectorias is not None):
            for bola in self.balls_copy:
                if bola.userData == "Blanca" and bola not in bolasEmbocadas:
                        trayectoriaBlanca.append(self.destransformar_coordenadas(bola.body.position))
                else:
                    if(bola not in bolasEmbocadas):
                        indexBall2 = self.balls_copy.index(bola)
                        trayectorias[indexBall2].append(self.destransformar_coordenadas(bola.body.position))
        # rewarding
        # if cue ball touch the rail first, subtract the reward
        self.reward -= 2 * self.pocket_tracking["rail_collision_count"]
    
        fcb = self.pocket_tracking["first_contacted_ball"]
        if (
            fcb is not None
            and not self.pocket_tracking["cue_ball_pocketed"]
            and (
                1 <= fcb.number <= 7
                or (self.score_tracking["pot_count"] == 7 and fcb.number == 8)
            )
        ):
            pck_arr = np.array(self.pocket_tracking["potted_balls"])
            if any(pck_arr[(pck_arr >= 1) & (pck_arr <= 8)]):
                # potted the correct ball
                self.score_tracking["foul_count"] = 0
                self.score_tracking["touch_count"] += 1
                self.score_tracking["pot_count"] += 1
                if self.reward_by_steps:
                    self.reward += 35
                else:
                    self.reward += 40

                self.reward -= self.pocket_tracking["fcb_collision_count"]
            else:
                # touched the correct ball
                # although didn't pot ball, still reward by how close ball gets to the pocket
                self.score_tracking["foul_count"] = 0
                self.score_tracking["touch_count"] += 1
                self.reward += 5
                if closest_pocket_dist < 600:
                    self.reward += 55 / np.sqrt(max(closest_pocket_dist, 1e-6))
        else:
            # touched the wrong ball or not touching anything at all
            # although fouled, still reward by how close it gets to the ball
            self.score_tracking["foul_count"] += 1
            self.score_tracking["total_foul"] += 1
            self.score_tracking["touch_count"] = 0
            self.reward -= 5
            if closest_ball_dist < 600:
                self.reward += 25 / np.sqrt(max(closest_ball_dist, 1e-6))

        # total episode reward
        if self.reward_by_steps:
            self.episode_reward.append(self.process_reward())

        # only cue ball left when use less balls
        if self.num_balls < 9 and len(self.balls) < 2 and self.cue_ball in self.balls:
            self.pocket_tracking["black_ball_pocketed"] = True
            self.pocket_tracking["is_won"] = True

        # check endgame condition
        if self.pocket_tracking["black_ball_pocketed"] or self.score_tracking[
            "total_foul"
        ] > self.total_foul_times / (self.score_tracking["pot_count"] * 0.2 + 1):
            self.episodes += 1
            done = True
            if (
                self.pocket_tracking["is_won"]
                and not self.pocket_tracking["cue_ball_pocketed"]
            ):
                if self.observation_type != "none":
                    if self.reward_by_steps:
                        self.reward = 50
                        self.episode_reward.append(self.process_reward())
                    else:
                        self.reward = 500
            else:
                self.reward = 0

            # update caption every 5 episodes
            if self.episodes == 1 or self.episodes % 5 == 0:
                self.fps = 1 / (
                    (time.time() - self.starting_time) / (self.episode_steps + 1e-8)
                )
                if self.draw_screen:
                    if not self.reward_by_steps:
                        pg.display.set_caption(
                            f"FPS: {self.fps:.0f}   REWARD: {self.process_reward():.3f}   POTTED_BALLS: {self.pocket_tracking['total_potted_balls']}   STEPS: {self.episode_steps}   TOTAL_STEPS: {self.total_steps}   EPISODES: {self.episodes}   ACTION: {np.array(action, dtype=int)}"
                        )
                    else:
                        pg.display.set_caption(
                            f"FPS: {self.fps:.0f}   TOT_REWARD: {np.sum(self.episode_reward):.2f}   POTTED_BALLS: {self.pocket_tracking['total_potted_balls']}   STEPS: {self.episode_steps}   TOTAL_STEPS: {self.total_steps}   EPISODES: {self.episodes}   ACTION: {np.array(action, dtype=int)}"
                        )
        if self.draw_screen:
            if not self.training:
                pg.display.set_caption(
                    f"FPS: {self.clock.get_fps():.0f}   REWARD: {self.process_reward():.3f}   POTTED_BALLS: {self.pocket_tracking['total_potted_balls']}   STEPS: {self.episode_steps}   TOTAL_STEPS: {self.total_steps}   EPISODES: {self.episodes}   ACTION: {np.array(action, dtype=int).tolist()}"
                )

        # prepare observation
        if self.draw_screen:
            self.process_events()
            self.redraw_screen()

        self.episode_steps += 1
        self.total_steps += 1

        # adding cue ball back to table if potted
        if self.pocket_tracking["cue_ball_pocketed"]:
            cuerpo_existe = any(shape.body == self.cue_ball.body for shape in self.space.shapes)
            if(cuerpo_existe == False):
                self.space.add(self.cue_ball.body, self.cue_ball)
            if(self.cue_ball not in self.balls):
                self.balls.append(self.cue_ball)

            pm.Body.update_velocity(self.cue_ball.body, (0, 0), damping=0, dt=1)
            self.cue_ball.body.position = random.randint(
                RAIL_DISTANCE * 2, self.width - RAIL_DISTANCE * 2
            ), random.randint(RAIL_DISTANCE * 2, self.height - RAIL_DISTANCE * 2)
            self.cue_ball.body.activate()
        
        rw = self.verificarBolaEnMano()

        if(self.simulacion != True):
            respuesta = self.setear_respuesta()
            return self.process_observation(), self.process_reward(), done, info, respuesta
        else: 
             return self.process_observation(), self.process_reward(), done, info, None

    def cantidad_para_embocar(self):
        cant = 0
        for ball in self.balls:
            if ball.observation_number == 1:
                cant = cant + 1   
        return cant
    
    def reset(self, *args, **kwargs):
        for x in self.space.shapes:
            try:
                self.space.remove(x)
                self.space.remove(x.body)
            except AssertionError:
                pass

        self.add_table()
        self.add_balls()
        if self.verMesa:
            SingletonVerMesa.delete_instance()

        cant = self.cantidad_para_embocar()
        resto = 7 - cant

        self.reward = self.total_foul_times * 5
        self.episode_reward = []
        self.episode_steps = 0
        self.starting_time = time.time()
        if( self.singleton.embocarNegra):
            self.score_tracking = {
                "foul_count": 0,
                "touch_count": 7,
                "pot_count": 7,
                "total_foul": 0,
            }
            self.pocket_tracking = {
                "cue_ball_pocketed": False,
                "black_ball_pocketed": False,
                "is_won": None,
                "cue_ball_first_contact": None,  # 1 --> ball, 2 --> pocket, 3 --> rail
                "first_contacted_ball": self.balls[0],
                "total_potted_balls": 14,
                "fcb_collision_count": 0,
                "rail_collision_count": 0,
                "potted_balls": [],
            }
        else:
            self.score_tracking = {
                "foul_count": 0,
                "touch_count": 0,
                "pot_count": 0,
                "total_foul": 0,
            }
            self.pocket_tracking = {
                "cue_ball_pocketed": False,
                "black_ball_pocketed": False,
                "is_won": None,
                "cue_ball_first_contact": None,  # 1 --> ball, 2 --> pocket, 3 --> rail
                "first_contacted_ball": None,
                "total_potted_balls": 0,
                "fcb_collision_count": 0,
                "rail_collision_count": 0,
                "potted_balls": [],
            }

        self.ball_collision_handler.data["cue_ball"] = self.cue_ball
        self.ball_collision_handler.data["pocket_tracking"] = self.pocket_tracking
        self.pocket_collision_handler.data["balls"] = self.balls
        self.pocket_collision_handler.data["pocket_tracking"] = self.pocket_tracking
        self.rail_collision_handler.data["pocket_tracking"] = self.pocket_tracking
        self.pocket_falso_collision_handler.data["balls"]=self.balls
        self.pocket_falso_collision_handler.data["pocket_tracking"]=self.pocket_tracking

        if self.draw_screen:
            self.process_events()
            self.redraw_screen()
        return self.process_observation()

    def get_attrs(self):
        def get_balls(x):
            return {
                "position": list(x.body.position),
                "number": x.number,
                "color": x.color,
                "etiqueta": x.userData,
                # "filter": x.filter,
                "collision_type": x.collision_type,
                "observation_number": x.observation_number,
            }

        return {
            "balls_attrs": [get_balls(x) for x in self.balls],
            "reward": copy(self.reward),
            "episodes": copy(self.episodes),
            "episode_reward": copy(self.episode_reward),
            "episode_steps": copy(self.episode_steps),
            "total_steps": copy(self.total_steps),
            "starting_time": copy(self.starting_time),
            "score_tracking": copy(self.score_tracking),
            "pocket_tracking": copy(self.pocket_tracking),
            "cantidad_bolas": len(self.balls),
            "bola_en_mano": self.bola_en_mano,
            "nroTronera": self.singleton.nroTronera
        }

    def apply_attrs(self, attrs):
        self.attrs_respuesta = attrs
        balls_attrs = attrs["balls_attrs"]
        self.reward = attrs["reward"]
        self.episodes = attrs["episodes"]
        self.episode_reward = attrs["episode_reward"]
        self.episode_steps = attrs["episode_steps"]
        self.total_steps = attrs["total_steps"]
        self.starting_time = attrs["starting_time"]
        self.score_tracking = attrs["score_tracking"]
        self.pocket_tracking = attrs["pocket_tracking"]
        del attrs

        balls = []
        for i in range(len(balls_attrs)):
            if i < len(self.balls):
                cuerpo_existe = any(shape.body == self.balls[i].body for shape in self.space.shapes)
                if(cuerpo_existe):
                    self.space.remove(self.balls[i].body, self.balls[i])
            if self.default == True:
                intertia = pm.moment_for_circle(BALL_MASS, 0, BALL_RADIUS, offset=(0, 0))
            else:
                intertia = pm.moment_for_circle(BALL_MASS, 0, int(self.singleton.tam_bolas_simulacion * ZOOM_MULTIPLIER), offset=(0, 0))
            ball_body = pm.Body(BALL_MASS, intertia)
            ball_body.position = balls_attrs[i]["position"]
            if self.default == True:
                ball = pm.Circle(ball_body, BALL_RADIUS, offset=(0, 0))
            else:
                ball = pm.Circle(ball_body, int(self.singleton.tam_bolas_simulacion * ZOOM_MULTIPLIER), offset=(0, 0))
            ball.elasticity = BALL_ELASTICITY
            ball.friction = BALL_FRICTION
            ball.collision_type = balls_attrs[i]["collision_type"]
            ball.number = balls_attrs[i]["number"]
            ball.color = balls_attrs[i]["color"]
            ball.observation_number = balls_attrs[i]["observation_number"]
            etiqueta = balls_attrs[i]["etiqueta"]
            ball.userData = etiqueta
            # ball.filter = balls_attrs[i]["filter"]
            ball.filter = pm.ShapeFilter(categories=0b00100)
            
            if ball.number == 0:
                self.cue_ball = ball
            elif ball.number < 8:
                ball.filter = pm.ShapeFilter(categories=0b01000)
            elif ball.number == 8:
                ball.filter = pm.ShapeFilter(categories=0b10000)
            else:
                ball.filter = pm.ShapeFilter(categories=0b00100)
            
            self.space.add(ball_body, ball)
            balls.append(ball)
        self.balls = balls
        self.balls_copy = balls.copy()

        self.ball_collision_handler.data["cue_ball"] = self.cue_ball
        self.ball_collision_handler.data["pocket_tracking"] = self.pocket_tracking
        self.pocket_collision_handler.data["balls"] = self.balls
        self.pocket_collision_handler.data["pocket_tracking"] = self.pocket_tracking
        self.rail_collision_handler.data["pocket_tracking"] = self.pocket_tracking
        self.pocket_falso_collision_handler.data["balls"] = self.balls
        self.pocket_falso_collision_handler.data["pocket_tracking"] = self.pocket_tracking

    def run(self, model=None):
        observation = self.reset()
        while self.running:
            if model is not None:
                velocity = model.predict(observation)[0].tolist()
            else:
                velocity = (random.uniform(-1, 1), random.uniform(-1, 1))
            observation, reward, done, info = self.step(velocity)
            # whether use space to move through each step
            """ while 1:
                for event in pg.event.get():
                    if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                        break
                else:
                    continue
                break"""
            if done:
                if not self.training:
                    if (
                        self.pocket_tracking["is_won"]
                        and not self.pocket_tracking["cue_ball_pocketed"]
                    ):
                        print("WIN !!")
                    else:
                        print("LOSE!!")
                self.reset()
    def close(self):
        pg.quit()
        del self.space  # Liberar el espacio pymunk



def main():
    import pstats
    import pathlib
    import cProfile

    pool = PoolEnv(training=False, draw_screen=True, observation_type="vector")

    # with cProfile.Profile() as pr:
    pool.run()

    # stats = pstats.Stats(pr)
    # stats.sort_stats(pstats.SortKey.TIME)
    # stats.dump_stats("profiling.prof")


if __name__ == "__main__":
    main()
