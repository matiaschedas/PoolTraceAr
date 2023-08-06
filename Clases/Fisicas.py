import pymunk
import random
import matplotlib.pyplot as plt
import math
import pygame
import copy

bolaBlancaPrimerColision = False
bolaPrimerColision = None

class Fisicas():
    #el constructor luego va a recibir tambien todos los checkbox que debera tener en cuenta para cumplir las reglas de pool:
    def __init__(self, verSimulacion, listaApareada, bolaSeleccionada, bolaBlanca, ROI, XIROI, YIROI, velBlancaX, velBlancaY, troneras, radioTronera):
        self.verSimulacion = verSimulacion
        self.listaApareada = listaApareada
        self.bolaSeleccionada = bolaSeleccionada
        self.bolaBlanca = bolaBlanca
        self.ROI = ROI
        self.balls = []
        self.XIROI = XIROI
        self.YIROI = YIROI
        self.blanca = None
        self.velBlancaX = velBlancaX
        self.velBlancaY = velBlancaY
        self.troneras = troneras
        self.radioTronera = radioTronera
        self.seleccionada = None
        self.listaTroneras = []
        self.entraron = []
        self.seleccionadaEtiqueta = None
        self.primerColisionEtiqueta = None

    def create_ball(self, space, x, y, radius, mass, etiqueta):
        body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
        body.position = x, y
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 1.0
        #con estos filtros seteo que las bolas puedan colisionar con las paredes y con otras bolas:
        shape.filter = pymunk.ShapeFilter(categories=0b0010, mask = 0b0100 | 0b0010)
        shape.userData = etiqueta
        space.add(body, shape)
        return body
    
    def create_tronera(self, space, x, y, radius, nro):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = x,y
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 1.0
        shape.filter = pymunk.ShapeFilter(categories=0b0001)
        shape.userData = "Tronera " + str(nro)
        space.add(body, shape)
        return body

    def apply_friction(self, body, friction_coefficient):
        velocity = body.velocity
        body.apply_impulse_at_local_point((-velocity.x * friction_coefficient, -velocity.y * friction_coefficient))

    def create_walls(self, space, width, height):
        mitad = width/2
        # walls = [pymunk.Segment(space.static_body, (0, 0), (0, height), 5),
        #         pymunk.Segment(space.static_body, (0, height), (width, height), 5),
        #         pymunk.Segment(space.static_body, (width, height), (width, 0), 5),
        #         pymunk.Segment(space.static_body, (0, 0), (width, 0), 5)]
        walls = [pymunk.Segment(space.static_body, (0+self.radioTronera,0),(mitad-self.radioTronera,0),5),
                 pymunk.Segment(space.static_body, (mitad+self.radioTronera,0),(width-self.radioTronera,0),5),
                 pymunk.Segment(space.static_body, (width,0+self.radioTronera),(width,height-self.radioTronera),5),
                 pymunk.Segment(space.static_body, (width-self.radioTronera,height),(mitad+self.radioTronera,height),5),
                 pymunk.Segment(space.static_body, (mitad-self.radioTronera,height),(0+self.radioTronera,height),5),
                 pymunk.Segment(space.static_body, (0,height-self.radioTronera),(0,0+self.radioTronera),5)]
 
        for wall in walls:
            wall.elasticity = 1.0
            wall.filter = pymunk.ShapeFilter(categories=0b0100,  mask=0b0010)
            space.add(wall)
        return walls

    def distancia(self, punto1, punto2):
        return math.sqrt((punto1[0] - punto2[0]) ** 2 + (punto1[1] - punto2[1]) ** 2)
    
    def on_collision_begin(self, arbiter, space, data):
        global bolaBlancaPrimerColision, bolaPrimerColision
        # Obtiene los cuerpos involucrados en la colisión
        ball_shape_1, ball_shape_2 = arbiter.shapes
        if(isinstance(ball_shape_1, pymunk.Circle) and isinstance( ball_shape_2, pymunk.Circle)):
            etiqueta_bola_1 = ball_shape_1.userData
            etiqueta_bola_2 = ball_shape_2.userData

            # Verifica si una de las bolas es la bola blanca
            if (etiqueta_bola_1 == "Blanca" or etiqueta_bola_2 == "Blanca") and (bolaBlancaPrimerColision==False):
                bolaBlancaPrimerColision = True
                if(etiqueta_bola_1 == "Blanca"):
                    self.primerColisionEtiqueta = ball_shape_2.userData
                else:
                    self.primerColisionEtiqueta = ball_shape_1.userData
        return True 
    
    def distancia_entre_puntos(self, punto1, punto2):
        return math.sqrt((punto1[0] - punto2[0]) ** 2 + (punto1[1] - punto2[1]) ** 2)

    
    def simular(self):
        if self.verSimulacion:
            pygame.init()
            (ancho, alto) = self.ROI
            plt.xlim(0, ancho)
            plt.ylim(0, alto)
            screen_width, screen_height = ancho+50, alto+50
            screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption("Billiards Simulation")
            clock = pygame.time.Clock()
            screen.fill((255, 255, 255))

        space = pymunk.Space()
        space.gravity = (0, 0)
         
        # Posiciones iniciales de las bolas que están quietas
        for bola in self.listaApareada:
            (x,y,r), _, etiqueta = bola
            (xs,ys,rs) = self.bolaSeleccionada
            xs = xs - self.XIROI
            ys = ys - self.YIROI
            if(etiqueta == "Blanca"):
               self.blanca  = self.create_ball(space, x, y, r, 1, etiqueta)
               self.blanca.velocity = (self.velBlancaX,self.velBlancaY)
               self.balls.append(self.blanca)
            elif(int(x) == int(xs) and int(y) == int(ys)):
                self.seleccionada = self.create_ball(space, x, y, r, 1, etiqueta)
                shape = list(self.seleccionada.shapes)[0]
                self.seleccionadaEtiqueta = shape.userData
                self.balls.append(self.seleccionada)
            else:
                self.balls.append(self.create_ball(space, x, y, r, 1, etiqueta))

        # Nuevas listas para almacenar las trayectorias de todas las bolas

        trajectories = [[] for _ in range(len(self.balls))]
        trayectoriaBlanca = []
        trayectoriaSeleccionada = []
        

        dt = 1.0 / 10
        total_steps = 100
        (ancho, alto) = self.ROI
        walls = self.create_walls(space, ancho, alto)
        i=1
        for tronera in self.troneras:
            (xt,yt) = tronera
            xt = xt - self.XIROI
            yt = yt - self.YIROI
            troneraBody = self.create_tronera(space, xt,yt,self.radioTronera,i)
            self.listaTroneras.append(troneraBody)
            i=i+1

        all_balls_stopped = False

        handler = space.add_collision_handler(0, 0)
        handler.begin = self.on_collision_begin
        
        while not all_balls_stopped:
           if(self.verSimulacion):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    all_balls_stopped = True
                    break
            
            bolas_para_eliminar = []

            for _ in range(5):
                space.step(dt)

            for ball in self.balls:
                self.apply_friction(ball, 0.01)
            
            if self.verSimulacion:
                screen.fill((255, 255, 255))

            # Guardar la posición actual de todas las bolas en sus trayectorias
            for ball_index, ball in enumerate(self.balls):
                x, y = ball.position
                ball_shape = list(ball.shapes)[0]
                etiqueta_bola = ball_shape.userData
         
                if (ball == self.seleccionada):
                    trayectoriaSeleccionada.append((x,y))
                elif(ball == self.blanca):
                    trayectoriaBlanca.append((x,y))
                else:
                    trajectories[ball_index].append((x, y))
                for tronera in self.listaTroneras:
                    tronera_x, tronera_y = tronera.position
                    distancia_bola_tronera = self.distancia_entre_puntos((x, y), (tronera_x, tronera_y))
                    if ball_shape.radius+ (0.2*ball_shape.radius) >= distancia_bola_tronera:
                        # Eliminar la bola que entra en la tronera
                        self.entraron.append((ball, etiqueta_bola))
                        bolas_para_eliminar.append(ball)
                        break

            for ball in bolas_para_eliminar:
                ball_shape = list(ball.shapes)[0]
                space.remove(ball_shape.body, ball_shape)
                self.balls.remove(ball)

            if(self.verSimulacion):
                for ball in self.balls:
                    x, y = ball.position
                    pygame.draw.circle(screen, (0, 0, 255), (int(x), int(y)), 20)
                for tronera in self.listaTroneras:
                    x,y = tronera.position
                    pygame.draw.circle(screen, (0, 255, 0), (int(x), int(y)), 20)
                pygame.display.flip()
                for wall in walls:
                    p1 = wall.a
                    p2 = wall.b
                    pygame.draw.line(screen, (255,0,0),p1,p2,5)
                clock.tick(60)

            total_velocity = sum(ball.velocity.length for ball in self.balls)
            if total_velocity < 5:
                all_balls_stopped = True


        #comentar si no necesito ver animacion:    
        if(self.verSimulacion):   
            pygame.quit()

        # # Graficar las trayectorias después de cerrar la simulación
        #esto grafica las rectas de todas las trayectorias, son las misma rectas que vamos a tener que retornar y luego graficar con opencv
        for ball_index, trajectory in enumerate(trajectories):
            if len(trajectory) > 0:
                x_values, y_values = zip(*trajectory)
                plt.plot(x_values, y_values, color="blue", label=f'Bola {ball_index + 1}')
                plt.scatter(x_values[-1], y_values[-1], color='blue')

        if len(trayectoriaBlanca) > 0:
            x_values, y_values = zip(*trayectoriaBlanca)
            plt.plot(x_values, y_values, color="black", label=f'Bola Blanca')
            plt.scatter(x_values[-1], y_values[-1], color='black')

        if len(trayectoriaSeleccionada) > 0:
            x_values, y_values = zip(*trayectoriaSeleccionada)
            plt.plot(x_values, y_values, color ="red", label=f'Bola Seleccionada')
            plt.scatter(x_values[-1], y_values[-1], color='red')

        for tronera in self.listaTroneras:
            (x,y) = tronera.position
            plt.scatter(x,y,color="green")
        
        for wall in walls:
            p1 = wall.a
            p2 = wall.b
            x_values = [p1.x, p2.x]
            y_values = [p1.y, p2.y]
            plt.plot(x_values,y_values, color="green")
            

                
        

        plt.xlabel('Posición X')
        plt.ylabel('Posición Y')
        plt.title('Trayectorias de Todas las Bolas')
        (ancho, alto) = self.ROI
        plt.xlim(-50, ancho+50)
        plt.ylim(-50, alto+50)
        plt.gca().invert_yaxis()
        plt.legend()
        plt.show()
        print(f"La bola blanca choco?: {bolaBlancaPrimerColision}")
        tiroValido = False
        if(self.primerColisionEtiqueta is not None):
            if(self.seleccionadaEtiqueta == self.primerColisionEtiqueta):
                    tiroValido = True
        print(f"tiro valido: {tiroValido}")
        print("Bolas que entraron: ")
        for ball, etiqueta in self.entraron:
            print(etiqueta)
        return trayectoriaBlanca, trayectoriaSeleccionada, tiroValido
         

#main viejo: esto llamaba a simular 1000 veces:
# if __name__ == "__main__":
#     for i in range (1000):
#         entro = main()
#         if entro:
#             lista.append((i, entro))
#             contador = contador + 1
#     print (lista)
#     print ("entraron: ")
#     print (contador)
