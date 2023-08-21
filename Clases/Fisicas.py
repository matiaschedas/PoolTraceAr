import pymunk
import matplotlib.pyplot as plt
import math
import pygame


bolaBlancaPrimerColision = False
bolaPrimerColision = None

class Fisicas():
    #el constructor luego va a recibir tambien todos los checkbox que debera tener en cuenta para cumplir las reglas de pool:
    def __init__(self, verSimulacion, verGrafico, verResultadosConsola, listaApareada, bolaSeleccionada, bolaBlanca, ROI, XIROI, YIROI, XDROI, YDROI, troneras, radioTronera, radioBolas, puntosParedes):
        self.verSimulacion = verSimulacion
        self.verGrafico = verGrafico
        self.verResultadosConsola = verResultadosConsola
        self.listaApareada = listaApareada
        self.bolaSeleccionada = bolaSeleccionada
        self.bolaBlanca = bolaBlanca
        self.ROI = ROI
        self.balls = []
        self.XIROI = XIROI
        self.YIROI = YIROI
        self.XDROI = XDROI
        self.YDROI = YDROI
        self.blanca = None
        self.velBlancaX = 0
        self.velBlancaY = 0
        self.troneras = troneras
        self.radioTronera = radioTronera
        self.seleccionada = None
        self.listaTroneras = []
        self.entraron = []
        self.seleccionadaEtiqueta = None
        self.primerColisionEtiqueta = None
        self.entroLaBlanca = False
        self.radioBolas = radioBolas
        self.entroLaSeleccionada = False
        self.entroLaNegra = False
        self.pasos = 5
        self.puntosParedes = puntosParedes

    #setea la velocidad en Y y en X de la bola blanca:
    def setear_velocidad_inicial_blanca(self, viX, viY):
        self.velBlancaX = viX
        self.velBlancaY = viY
    
    #setea el paso del tiempo de la simulacion:
    #ajustar para conseguir mesa real:
    def setear_pasos_tiempo(self, pasos):
        self.pasos = pasos

    #si requiero simular nuevamente un tiro usar:
    def reiniciar_simulacion(self):
        self.balls = []
        self.blanca = None
        self.seleccionada = None
        self.listaTroneras = []
        self.entraron = []
        self.seleccionadaEtiqueta = None
        self.primerColisionEtiqueta = None
        self.entroLaBlanca = False
        self.entroLaSeleccionada = False
        self.entroLaNegra = False

    def create_ball(self, space, x, y, radius, mass, etiqueta):
        body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
        body.position = x, y
        shape = pymunk.Circle(body, radius)
        #ajustar para conseguir mesa real:
        shape.elasticity = 0.9 #determina cuanta energia cinetica se conserva en la colision (1.0 es 100% elastica)
        #con estos filtros seteo que las bolas puedan colisionar con las paredes y con otras bolas:
        shape.filter = pymunk.ShapeFilter(categories=0b0010, mask = 0b0100 | 0b0010)
        shape.userData = etiqueta
        space.add(body, shape)
        return body
    
    def create_tronera(self, space, x, y, radius, nro):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = x,y
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.9
        shape.filter = pymunk.ShapeFilter(categories=0b0001)
        shape.userData = "Tronera " + str(nro)
        space.add(body, shape)
        return body

    #aplica la friccion de la bola contra la mesa (tambien se puede no usar este metodo y aplicarl la friccion al crear la bola):
    #ajustar para conseguir mesa real:
    def apply_friction(self, body, friction_coefficient):
        velocity = body.velocity
        body.apply_impulse_at_local_point((-velocity.x * friction_coefficient, -velocity.y * friction_coefficient))

    def create_segment(self,space, x1,y1, x2,y2):
        segment_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        segment_shape = pymunk.Segment(segment_body, (x1, y1), (x2,y2),5)
        #ajustar para conseguir mesa real:
        segment_shape.elasticity = 0.5
        #ajustar para conseguir mesa real:
        segment_shape.friction = 0.1
        segment_shape.filter = pymunk.ShapeFilter(categories=0b0100, mask=0b0010)
        space.add(segment_body,segment_shape)
        return segment_body

    def create_walls(self, space, width, height):
        mitad = width/2
        wallsPy = []
        walls = []
        puntos = self.puntosParedes.copy()
        for i, punto in enumerate(puntos):
            xp, yp = punto
            if i>=0 and i<=3:
                puntos[i]=(xp-self.XIROI,self.YIROI-self.YIROI)
            if i==4 or i == 5:
                puntos[i]=(self.XDROI-self.XIROI,yp-self.YIROI)
            if i>=6 and i<=9:
                puntos[i]=(xp-self.XIROI,self.YDROI-self.YIROI)
            if i==10 or i == 11:
                puntos[i]=(self.XIROI-self.XIROI,yp-self.YIROI)

        walls = [[(puntos[0]),(puntos[1])],
                 [(puntos[2]),(puntos[3])],
                 [(puntos[4]),(puntos[5])],
                 [(puntos[6]),(puntos[7])],
                 [(puntos[8]),(puntos[9])],
                 [(puntos[10]),(puntos[11])]]
            
        # walls = [[(0+self.radioTronera,0),(mitad-self.radioTronera,0)],
        #          [(mitad+self.radioTronera,0),(width-self.radioTronera,0)],
        #          [(width,0+self.radioTronera),(width,height-self.radioTronera)],
        #          [(width-self.radioTronera,height),(mitad+self.radioTronera,height)],
        #          [(mitad-self.radioTronera,height),(0+self.radioTronera,height)],
        #          [(0,height-self.radioTronera),(0,0+self.radioTronera)]]
 
        for wall in walls:
            (x1, y1),(x2,y2) = wall 
            wallsPy.append(self.create_segment(space,x1,y1,x2,y2))
        return walls

    def distancia(self, punto1, punto2):
        return math.sqrt((punto1[0] - punto2[0]) ** 2 + (punto1[1] - punto2[1]) ** 2)
    
    #metodo que se ejecuta cuando hay colision entre 2 objetos:
    def on_collision_begin(self, arbiter, space, data):
        global bolaBlancaPrimerColision, bolaPrimerColision
        # Obtiene los cuerpos involucrados en la colisión
        ball_shape_1, ball_shape_2 = arbiter.shapes
        if(isinstance(ball_shape_1, pymunk.Circle) and isinstance( ball_shape_2, pymunk.Circle)):
            etiqueta_bola_1 = ball_shape_1.userData
            etiqueta_bola_2 = ball_shape_2.userData
            if(ball_shape_1.body.position == self.seleccionada.position):
                self.puntos_trayectoria_seleccionada.append(self.seleccionada.position)
            if(ball_shape_2.body.position == self.seleccionada.position):
                self.puntos_trayectoria_seleccionada.append(self.seleccionada.position)
            # Verifica si una de las bolas es la bola blanca
            if (etiqueta_bola_1 == "Blanca" or etiqueta_bola_2 == "Blanca") and (bolaBlancaPrimerColision==False):
                bolaBlancaPrimerColision = True
                if(etiqueta_bola_1 == "Blanca"):
                    self.primerColisionEtiqueta = ball_shape_2.userData
                else:
                    self.primerColisionEtiqueta = ball_shape_1.userData
            if (etiqueta_bola_1 == "Blanca"):
               self.puntos_trayectoria_blanca.append(ball_shape_1.body.position)
            elif (etiqueta_bola_2 == "Blanca"):                
               self.puntos_trayectoria_blanca.append(ball_shape_2.body.position)
            
            if(ball_shape_1.body.position != self.seleccionada.position and ball_shape_1.body.position != self.blanca.position):
                if(self.balls is not None):
                    for ball in self.balls:
                        if(ball.position == ball_shape_1.body.position):
                            index = self.balls.index(ball)
                            self.puntos_trayectorias[index].append(ball_shape_1.body.position)

            if(ball_shape_2.body.position != self.seleccionada.position and ball_shape_2.body.position != self.blanca.position):
                if(self.balls is not None):
                    for ball in self.balls:
                            if(ball.position == ball_shape_2.body.position):
                                index = self.balls.index(ball)
                                self.puntos_trayectorias[index].append(ball_shape_2.body.position)

        if(isinstance(ball_shape_1,pymunk.Segment) and isinstance(ball_shape_2,pymunk.Circle) or isinstance(ball_shape_2,pymunk.Segment) and isinstance(ball_shape_1,pymunk.Circle)):
            if(isinstance(ball_shape_1,pymunk.Segment)):
                if(ball_shape_2.body.position == self.seleccionada.position):
                     self.puntos_trayectoria_seleccionada.append(self.seleccionada.position)
                if(ball_shape_2.body.position != self.seleccionada.position and ball_shape_2.body.position != self.blanca.position):
                    if(self.balls is not None):
                        for ball in self.balls:
                            if(ball.position == ball_shape_2.body.position):
                                index = self.balls.index(ball)
                                self.puntos_trayectorias[index].append(ball_shape_2.body.position)
            if(isinstance(ball_shape_2,pymunk.Segment)):
                if(ball_shape_1.body.position == self.seleccionada.position):
                     self.puntos_trayectoria_seleccionada.append(self.seleccionada.position)
                if(ball_shape_1.body.position != self.seleccionada.position and ball_shape_1.body.position != self.blanca.position):
                    if(self.balls is not None):
                        for ball in self.balls:
                            if(ball.position == ball_shape_1.body.position):
                                index = self.balls.index(ball)
                                self.puntos_trayectorias[index].append(ball_shape_1.body.position)
            if(isinstance(ball_shape_1,pymunk.Segment)):
                etiqueta_bola_2 = ball_shape_2.userData
                etiqueta_bola_1 = ""
            else:
                etiqueta_bola_1 = ball_shape_1.userData
                etiqueta_bola_2 = ""
            # Verifica si una de las bolas es la bola blanca
            if (etiqueta_bola_1 == "Blanca"):                
                self.puntos_trayectoria_blanca.append(ball_shape_1.body.position)
            elif (etiqueta_bola_2 == "Blanca"):
                self.puntos_trayectoria_blanca.append(ball_shape_2.body.position)
        return True 
    
    def distancia_entre_puntos(self, punto1, punto2):
        return math.sqrt((punto1[0] - punto2[0]) ** 2 + (punto1[1] - punto2[1]) ** 2)

    
    def simular(self):
        self.puntos_trayectoria_blanca = []
        self.puntos_trayectoria_seleccionada = []
        self.puntos_trayectorias =[[] for _ in range(len(self.listaApareada))]
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
        #ajustar para conseguir mesa real:
        space.gravity = (0, 0)
         
        #se crean las bolas:
        for bola in self.listaApareada:
            (x,y,r), _, etiqueta = bola
            (xs,ys,rs) = self.bolaSeleccionada
            xs = xs - self.XIROI
            ys = ys - self.YIROI
            if(etiqueta == "Blanca"):
               self.blanca  = self.create_ball(space, x, y, r, 1, etiqueta)
               self.blanca.velocity = (self.velBlancaX,self.velBlancaY)
               self.balls.append(self.blanca)
               self.puntos_trayectoria_blanca.append(self.blanca.position)
            elif(int(x) == int(xs) and int(y) == int(ys)):
                self.seleccionada = self.create_ball(space, x, y, r, 1, etiqueta)
                shape = list(self.seleccionada.shapes)[0]
                self.seleccionadaEtiqueta = shape.userData
                self.balls.append(self.seleccionada)
                self.puntos_trayectoria_seleccionada.append(self.seleccionada.position)
            else:
                bola = self.create_ball(space, x, y, r, 1, etiqueta)
                self.balls.append(bola)
                index = self.balls.index(bola)
                self.puntos_trayectorias[index].append(bola.position)
                

        # Nuevas listas para almacenar las trayectorias de todas las bolas

        #comento las trayectorias de las demas bolas para mejorar performance:
        trajectories = [[] for _ in range(len(self.balls))]
        trayectoriaBlanca = []
        trayectoriaSeleccionada = []
        

        dt = 1.0 / 10
        total_steps = 100
        (ancho, alto) = self.ROI
        #se crean las paredes:
        walls = self.create_walls(space, ancho, alto)
        #se crean las troneras:
        i=1
        for tronera in self.troneras:
            (xt,yt) = tronera
            xt = xt - self.XIROI
            yt = yt - self.YIROI
            troneraBody = self.create_tronera(space, xt,yt,self.radioTronera,i)
            self.listaTroneras.append(troneraBody)
            i=i+1

        all_balls_stopped = False

        #se crea el manejador de eventos de colisiones:
        handler = space.add_collision_handler(0, 0)
        handler.begin = self.on_collision_begin

        while not all_balls_stopped:
        
            if(self.verSimulacion):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        all_balls_stopped = True
                        for ball in self.balls:
                            if(list(ball.shapes)[0].userData == "Blanca"):
                                self.puntos_trayectoria_blanca.append(ball.position)
                            if(list(ball.shapes)[0].userData != "Blanca" and ball.position != self.seleccionada.position):
                                index = self.balls.index(ball)
                                self.puntos_trayectorias[index].append(ball.position)
                        self.puntos_trayectoria_seleccionada.append(self.seleccionada.position)
                        break
            
            bolas_para_eliminar = []
            #pasos de tiempo para la simulacion fisica:
            for _ in range(self.pasos):
                space.step(dt)

            if self.verSimulacion:
                screen.fill((255, 255, 255))

            # Guardar la posición actual de todas las bolas en sus trayectorias
            for ball_index, ball in enumerate(self.balls):
                self.apply_friction(ball, 0.01)
                x, y = ball.position
                ball_shape = list(ball.shapes)[0]
                etiqueta_bola = ball_shape.userData
            
                if (ball == self.seleccionada):
                    trayectoriaSeleccionada.append((x,y))
                elif(ball == self.blanca):
                    trayectoriaBlanca.append((x,y))
                #comento trayectorias de las demas bolas para mejorar performance:
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
                etiqueta = ball_shape.userData
                if (etiqueta == "Blanca"):
                    self.entroLaBlanca = True
                if(self.seleccionada == ball):
                    self.entroLaSeleccionada = True
                if(etiqueta == "Negra"):
                    self.entroLaNegra = True
                space.remove(ball_shape.body, ball_shape)
                self.balls.remove(ball)

            if(self.verSimulacion):
                for ball in self.balls:
                    x, y = ball.position
                    pygame.draw.circle(screen, (0, 0, 255), (int(x), int(y)), self.radioBolas)
                for tronera in self.listaTroneras:
                    x,y = tronera.position
                    pygame.draw.circle(screen, (0, 255, 0), (int(x), int(y)), self.radioTronera)

                for segment in space.shapes:
                    if isinstance(segment, pymunk.Segment):
                        body = segment.body
                        p1 = body.local_to_world(segment.a)
                        p2 = body.local_to_world(segment.b)
                        pygame.draw.line(screen, (0, 255, 0), p1, p2)
                pygame.display.flip()
                clock.tick(60)

            total_velocity = sum(ball.velocity.length for ball in self.balls)
            if total_velocity < 5:
                for ball in self.balls:
                            if(list(ball.shapes)[0].userData == "Blanca"):
                                self.puntos_trayectoria_blanca.append(ball.position)
                            if(list(ball.shapes)[0].userData != "Blanca" and ball.position != self.seleccionada.position):
                                index = self.balls.index(ball)
                                self.puntos_trayectorias[index].append(ball.position)
                self.puntos_trayectoria_seleccionada.append(self.seleccionada.position)
                all_balls_stopped = True



        if(self.verSimulacion):   
            pygame.quit()

        # # Graficar las trayectorias después de cerrar la simulación
        #esto grafica las rectas de todas las trayectorias, son las misma rectas que vamos a tener que retornar y luego graficar con opencv
        if(self.verGrafico):
            plt.figure()
            
            for ball_index, trajectory in enumerate(trajectories):
                if len(trajectory) > 0:
                    x_values, y_values = zip(*trajectory)
                    plt.plot(x_values, y_values, color="blue", label=f'Bola {ball_index + 1}')
                    plt.scatter(x_values[-1], y_values[-1], color='blue', s=self.radioBolas*2)

            if len(trayectoriaBlanca) > 0:
                x_values, y_values = zip(*trayectoriaBlanca)
                plt.plot(x_values, y_values, color="black", label=f'Bola Blanca')
                plt.scatter(x_values[-1], y_values[-1], color='black', s=self.radioBolas*2)

            if len(trayectoriaSeleccionada) > 0:
                x_values, y_values = zip(*trayectoriaSeleccionada)
                plt.plot(x_values, y_values, color ="red", label=f'Bola Seleccionada')
                plt.scatter(x_values[-1], y_values[-1], color='red', s=self.radioBolas*2)

            for tronera in self.listaTroneras:
                (x,y) = tronera.position
                plt.scatter(x,y,color="green", s=self.radioTronera*2)
            
            for wall in walls:
                (x1,y1) , (x2,y2) = wall
                plt.plot([x1,x2],[y1,y2], color="green")
                
            plt.xlabel('Posición X')
            plt.ylabel('Posición Y')
            plt.title('Trayectorias de Todas las Bolas')
            (ancho, alto) = self.ROI
            plt.xlim(-50, ancho+50)
            plt.ylim(-50, alto+50)
            plt.gca().invert_yaxis()
            plt.legend()
            plt.show()

                
        if(self.verResultadosConsola):
            print(f"La bola blanca choco?: {bolaBlancaPrimerColision}")
        tiroValido = False
        if(self.primerColisionEtiqueta is not None):
            if(self.verResultadosConsola):
                print(f"primer colision de la blanca fue con: {self.primerColisionEtiqueta}")
            if(self.seleccionadaEtiqueta == self.primerColisionEtiqueta):
                    tiroValido = True
        if(self.entroLaBlanca):
            tiroValido = False
        if(self.verResultadosConsola):
            print(f"tiro valido: {tiroValido}")
            print(f"Entro la blanca: {self.entroLaBlanca}")
            print("Bolas que entraron: ")
            for ball, etiqueta in self.entraron:
                print(etiqueta)
        return trayectoriaBlanca, trayectoriaSeleccionada, tiroValido, self.entroLaBlanca, self.entroLaSeleccionada, self.entroLaNegra, self.puntos_trayectoria_blanca, self.puntos_trayectoria_seleccionada, self.puntos_trayectorias
         