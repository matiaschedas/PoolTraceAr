from  Clases.Fisicas import Fisicas
from math import sqrt

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
        self.velocidades=[200,100,60,40,20]
        self.bolaBlancaSinROI=(bolaBlanca[0]-XIROI,bolaBlanca[1]-YIROI,bolaBlanca[2])
        self.bolaSeleccionadaSinROI=(bolaSeleccionada[0]-XIROI,bolaSeleccionada[1]-YIROI,bolaBlanca[2])
        self.fisicas.setear_pasos_tiempo(1000)
        self.tronerasSinROI=[]
        for tronera in troneras:
            self.tronerasSinROI.append((tronera[0]-XIROI,tronera[1]-YIROI))
        self.diametroBola=self.bolaBlancaSinROI[2]*2

    def simular_tiro(self, vector_velocidad):
        for velocidad in self.velocidades:
            self.fisicas.setear_bolas_y_reiniciar_simulacion(self.listaApareada,self.bolaSeleccionada,self.bolaBlanca)
            self.fisicas.setear_ver_simulacion_graficos_resultados(False,False,False)
            self.fisicas.setear_velocidad_inicial_blanca(vector_velocidad[0]*velocidad,vector_velocidad[1]*velocidad)
            trayectoriaBlanca, trayectoriaSeleccionada, tiroValido, entroLaBlanca, entroLaSeleccionada, entroLaNegra, puntos_trayectoria_blanca, puntos_trayectoria_seleccionada, puntos_trayectorias=self.fisicas.simular()
            if  entroLaSeleccionada and not entroLaBlanca and not entroLaNegra:
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
        (vx,vy)=self.tiro_directo(bolaSeleccionada,tronera)
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

    