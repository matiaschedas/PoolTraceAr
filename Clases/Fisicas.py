import pymunk
import random
import matplotlib.pyplot as plt
import math

bolaBlancaPrimerColision = False
bolaPrimerColision = None

class Fisicas():
    #el constructor luego va a recibir tambien todos los checkbox que debera tener en cuenta para cumplir las reglas de pool:
    def __init__(self, listaApareada, bolaSeleccionada, bolaBlanca, ROI, XIROI, YIROI, velBlancaX, velBlancaY, troneras):
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
        self.seleccionada = None

    def create_ball(self, space, x, y, radius, mass, etiqueta):
        body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
        body.position = x, y
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 1.0
        shape.userData = etiqueta
        space.add(body, shape)
        return body

    def apply_friction(self, body, friction_coefficient):
        velocity = body.velocity
        body.apply_impulse_at_local_point((-velocity.x * friction_coefficient, -velocity.y * friction_coefficient))

    def create_walls(self, space, width, height):
        walls = [pymunk.Segment(space.static_body, (0, 0), (0, height), 5),
                pymunk.Segment(space.static_body, (0, height), (width, height), 5),
                pymunk.Segment(space.static_body, (width, height), (width, 0), 5),
                pymunk.Segment(space.static_body, (0, 0), (width, 0), 5)]
        for wall in walls:
            wall.elasticity = 1.0
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
                    bolaPrimerColision = ball_shape_2
                else:
                    bolaPrimerColision = ball_shape_1
        return True 

    def simular(self):
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
               #en vez de  harcodearlo se debera enviar como parametro del contructor:
               self.blanca.velocity = (self.velBlancaX,self.velBlancaY)
               self.balls.append(self.blanca)
            elif(int(x) == int(xs) and int(y) == int(ys)):
                self.seleccionada = self.create_ball(space, x, y, r, 1, etiqueta)
                self.balls.append(self.seleccionada)
            else:
                self.balls.append(self.create_ball(space, x, y, r, 1, etiqueta))

        # Crear una bola adicional en movimiento
        #moving_ball = self.create_ball(space, 700, 500, 20, 1, "hola")
        #vx0, vy0 = random.uniform(-50, 50), random.uniform(-50, 50)
        #moving_ball.velocity = (vx0, vy0)
        #balls.append(moving_ball)

        # Nuevas listas para almacenar las trayectorias de todas las bolas


        trajectories = [[] for _ in range(len(self.balls))]
        trayectoriaBlanca = []
        trayectoriaSeleccionada = []


        dt = 1.0 / 10
        total_steps = 100
        (ancho, alto) = self.ROI
        walls = self.create_walls(space, ancho, alto)

        all_balls_stopped = False
        ball_selected_approached_corner = False

        handler = space.add_collision_handler(0, 0)
        handler.begin = self.on_collision_begin
        
        while not all_balls_stopped:
            for _ in range(5):
                space.step(dt)

            for ball in self.balls:
                self.apply_friction(ball, 0.01)

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


            total_velocity = sum(ball.velocity.length for ball in self.balls)
            if total_velocity < 5:
                all_balls_stopped = True

            selected_ball = self.balls[-1]
            x, y = selected_ball.position

            distancia_a_esquinas = [
                self.distancia((x, y), (0, 0)),
                self.distancia((x, y), (1280, 0)),
                self.distancia((x, y), (0, 720)),
                self.distancia((x, y), (1280, 720))
            ]

            # Obtener el radio de la bola seleccionada
            radio_bola_seleccionada = list(selected_ball.shapes)[0].radius

            # Calcular la distancia desde el centro de la bola a las esquinas y comparar con el radio
            if min(distancia_a_esquinas) < 60:
                ball_selected_approached_corner = True
        

        # # Graficar las trayectorias después de cerrar la simulación
        #esto grafica las rectas de todas las trayectorias, son las misma rectas que vamos a tener que retornar y luego graficar con opencv
        for ball_index, trajectory in enumerate(trajectories):
            if len(trajectory) > 0:
                x_values, y_values = zip(*trajectory)
                plt.plot(x_values, y_values, label=f'Bola {ball_index + 1}')
                plt.scatter(x_values[-1], y_values[-1], color='blue')

        if len(trayectoriaBlanca) > 0:
            x_values, y_values = zip(*trayectoriaBlanca)
            plt.plot(x_values, y_values, label=f'Bola Blanca')
            plt.scatter(x_values[-1], y_values[-1], color='black')

        if len(trayectoriaSeleccionada) > 0:
            x_values, y_values = zip(*trayectoriaSeleccionada)
            plt.plot(x_values, y_values, label=f'Bola Seleccionada')
            plt.scatter(x_values[-1], y_values[-1], color='red')
                
        

        plt.xlabel('Posición X')
        plt.ylabel('Posición Y')
        plt.title('Trayectorias de Todas las Bolas')
        (ancho, alto) = self.ROI
        plt.xlim(0, ancho)
        plt.ylim(0, alto)
        plt.gca().invert_yaxis()
        plt.legend()
        plt.show()
        print(f"La bola blanca choco?: {bolaBlancaPrimerColision}")
        seleccionadaShape = list(self.seleccionada.shapes)[0]
        tiroValido = False
        if(bolaPrimerColision is not None):
            if(seleccionadaShape.userData == bolaPrimerColision.userData):
                tiroValido = True
        print(f"tiro valido: {tiroValido}")
        return ball_selected_approached_corner, tiroValido

#main viejo: esto llamaba a simular() que antes era el main():
# if __name__ == "__main__":
#     for i in range (1000):
#         entro = main()
#         if entro:
#             lista.append((i, entro))
#             contador = contador + 1
#     print (lista)
#     print ("entraron: ")
#     print (contador)
