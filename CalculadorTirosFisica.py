from  Clases.Fisicas import Fisicas
from math import sqrt,cos,sin,acos

class CalculadorTirosFisica:
    def __init__(self, verSimulacion, verGrafico, verResultadosConsola, listaApareada, bolaSeleccionada, bolaBlanca, ROI, XIROI, YIROI, XDROI, YDROI, troneras, radioTronera, radioBolas, puntosParedes, bolaEnMano, dosTiros, mesaAbierta):
        self.verSimulacion=verSimulacion
        self.verGrafico=verGrafico
        self.verResultadosConsola=verResultadosConsola
        self.listaApareada=listaApareada
        self.bolaSeleccionada=bolaSeleccionada
        self.bolaBlanca=bolaBlanca
        self.ROI=ROI
        self.XIROI=XIROI
        self.YIROI=YIROI
        self.XDROI=XDROI
        self.YDROI=YDROI
        self.troneras=troneras
        self.radioTronera=radioTronera
        self.radioBolas=radioBolas
        self.puntosParedes=puntosParedes
        self.bolaEnMano=bolaEnMano
        self.dosTiros=dosTiros
        self.mesaAbierta=mesaAbierta
        self.fisicas = Fisicas(verSimulacion, verGrafico,verResultadosConsola, listaApareada, bolaSeleccionada, bolaBlanca, ROI, XIROI, YIROI,XDROI,YDROI, troneras,radioTronera, radioBolas,puntosParedes,bolaEnMano,dosTiros,mesaAbierta)
        self.velocidades=[50,60,40,20]
        self.bolaBlancaSinROI=(bolaBlanca[0]-XIROI,bolaBlanca[1]-YIROI,bolaBlanca[2])
        self.bolaSeleccionadaSinROI=(bolaSeleccionada[0]-XIROI,bolaSeleccionada[1]-YIROI,bolaBlanca[2])
        self.fisicas.setear_pasos_tiempo(1000)
        self.tronerasSinROI=[]
        for tronera in troneras:
            self.tronerasSinROI.append((tronera[0]-XIROI,tronera[1]-YIROI))
        self.diametroBola=self.bolaBlancaSinROI[2]*2
                
        self.bandaSuperior=[(13, -12), (319.5, -12),(373.5, -12), (684.0, -12)]
        self.bandaInferior=[(13, 375.0), (319.5, 375.0),(373.5, 375.0), (684.0, 375.0)]
        self.bandaIzquierda=[(-10, 18), (-10, 341.0)]
        self.bandaDerecha=[(713.0, 18),(713.0, 341.0)]
        
    
    def simular_tiro(self, vector_velocidad):
        for velocidad in self.velocidades:
            self.fisicas.setear_bolas_y_reiniciar_simulacion(self.listaApareada,self.bolaSeleccionada,self.bolaBlanca)
            self.fisicas.setear_ver_simulacion_graficos_resultados(True,True,True)
            self.fisicas.setear_velocidad_inicial_blanca(vector_velocidad[0]*velocidad,vector_velocidad[1]*velocidad)
            trayectoriaBlanca, trayectoriaSeleccionada, tiroValido, entroLaBlanca, entroLaSeleccionada, entroLaNegra, puntos_trayectoria_blanca, puntos_trayectoria_seleccionada, puntos_trayectorias=self.fisicas.simular()
            with open("trayec.txt","w") as file:
                file.write(str(trayectoriaBlanca))
            if not  entroLaSeleccionada:
                return False 
            if not entroLaBlanca and not entroLaNegra:
                if self.verSimulacion is True:
                    self.fisicas.setear_bolas_y_reiniciar_simulacion(self.listaApareada,self.bolaSeleccionada,self.bolaBlanca)
                    self.fisicas.setear_ver_simulacion_graficos_resultados(True,True,True)
                    self.fisicas.setear_velocidad_inicial_blanca(vector_velocidad[0]*velocidad,vector_velocidad[1]*velocidad)
                    self.fisicas.simular()
                return True
            



    def calcular_tiro_posible(self):
        for tronera in self.tronerasSinROI:
            vector_velocidad=self.tiro_directo(self.bolaSeleccionadaSinROI,tronera)    
            if vector_velocidad is not None and self.simular_tiro(vector_velocidad) is True:
                print("Tiro posible!")
        return  None

                
                

    
    def camino_libre(obj1,obj2):
        return None
    
    def calcular(self,bolaSeleccionada,tronera,velocidad):
        (vx,vy)=self.tiro_directo(bolaSeleccionada,self.tronerasSinROI[tronera-1])
        self.fisicas.setear_velocidad_inicial_blanca(vx*velocidad,vy*velocidad) 
        trayectoriaBlanca, trayectoriaSeleccionada, tiroValido, entroLaBlanca, entroLaSeleccionada, entroLaNegra, puntos_trayectoria_blanca, puntos_trayectoria_seleccionada, puntos_trayectorias=self.fisicas.simular()


    def definir_signos(self,inicio,fin):
        return 1 if inicio[0]<fin[0] else -1,1 if inicio[1]<fin[1] else -1
    
    def normalizar_vector(self,vector):
        norma=sqrt(vector[0]**2+vector[1]**2)
        return (vector[0]/norma,vector[1]/norma)

    def tiro_directo(self,bolaSeleccionada,tronera):
        (xt,yt)   = tronera
        (xb,yb,_) = self.bolaBlancaSinROI
        (xo,yo,_) = bolaSeleccionada
        direccion=self.normalizar_vector((xo-xt,yo-yt))
        xi,yi=(xo+self.diametroBola*direccion[0],yo+self.diametroBola*direccion[1])
        return self.normalizar_vector((xi-xb,yi-yb))
    


    def test_tiro_con_banda(self,bolaSeleccionada,tronera,banda):
        vx,vy=self.tiro_con_banda(self.bolaSeleccionadaSinROI,self.tronerasSinROI[tronera-1],banda)
        self.simular_tiro((vx,vy))

    def distancia_bola_a_banda(self,bola,banda):
        radioBola=self.diametroBola/2
        if banda=="Superior":
            return bola[1]-self.bandaSuperior[0][1]-radioBola
        if banda=="Inferior":
            return self.bandaInferior[0][1]-self.bola[1]-radioBola
        if banda=="Izquierda":
            return bola[0]-self.bandaIzquierda[0][0]-radioBola
        if banda=="Derecha":
            return self.bandaDerecha[0][0]-bola[0]-radioBola
    
    def tiro_con_banda(self,bolaSeleccionada,tronera,banda):
        (xt,yt)   = tronera
        (xb,yb,_) = self.bolaBlancaSinROI
        (xo,yo,_) = bolaSeleccionada
        direccion=self.normalizar_vector((xo-xt,yo-yt))
        xi,yi=(xo+self.diametroBola*direccion[0],yo+self.diametroBola*direccion[1])

        a=self.distancia_bola_a_banda(bolaSeleccionada,banda)
        b=self.distancia_bola_a_banda(self.bolaBlancaSinROI,banda)
        c=sqrt((xi-xb)**2+(yi-yb)**2) #Distancia entre las bolas
        angulo=acos(sqrt((a**2+b**2+2*a*b)/(c**2+4*a*b))) #angulo entre la trayectoria de la blanca y la recta normal a la banda. La formula sale de despejar el teorema del coseno
        return -sin(angulo),-cos(angulo)
        print("")