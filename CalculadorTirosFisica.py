from  Clases.Fisicas import Fisicas
import math
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
        self.velocidades=[20,40,60,80,100]
        self.bolaBlancaSinROI=(bolaBlanca[0]-XIROI,bolaBlanca[1]-YIROI,bolaBlanca[2])
        self.bolaSeleccionadaSinROI=(bolaSeleccionada[0]-XIROI,bolaSeleccionada[1]-YIROI,bolaBlanca[2])


    def simular_tiro(self, vector_velocidad):
        self.fisicas.verSimulacion=False
        self.fisicas.verResultadosConsola=False
        self.fisicas.verGrafico=False
        self.fisicas.setear_pasos_tiempo(1)
        for velocidad in self.velocidades:
            self.fisicas.setear_velocidad_inicial_blanca(vector_velocidad[0]*velocidad,vector_velocidad[1]*velocidad)
            trayectoriaBlanca, trayectoriaSeleccionada, tiroValido, entroLaBlanca, entroLaSeleccionada, entroLaNegra, puntos_trayectoria_blanca, puntos_trayectoria_seleccionada, puntos_trayectorias=self.fisicas.simular()
            if  entroLaSeleccionada and not entroLaBlanca and not entroLaNegra:
                return True
            



    def calcular_tiro_posible(self):
        for tronera in self.troneras:
            vector_velocidad=self.tiro_directo((self.bolaSeleccionada[0]-self.XIROI,self.bolaSeleccionada[1]-self.YIROI),tronera)    
            if vector_velocidad is not None and self.simular_tiro(vector_velocidad) is True:
                return vector_velocidad
        return  None

                
                

    
    def camino_libre(obj1,obj2):
        return None
    
    def calcular(self,bolaSeleccionada,tronera,velocidad):
        (vx,vy)=self.tiro_directo(bolaSeleccionada,tronera)
        self.fisicas.setear_velocidad_inicial_blanca(vx*velocidad,vy*velocidad) 
        self.fisicas.setear_pasos_tiempo(1)
        trayectoriaBlanca, trayectoriaSeleccionada, tiroValido, entroLaBlanca, entroLaSeleccionada, entroLaNegra, puntos_trayectoria_blanca, puntos_trayectoria_seleccionada, puntos_trayectorias=self.fisicas.simular()
        with open("trayectoria.txt","w") as file:
            file.write(str(trayectoriaBlanca))
        with open("trayectoriaseleccionada.txt","w") as file:
            file.write(str(trayectoriaSeleccionada))
        print("")
        
    def definir_signos(self,inicio,fin):
        return 1 if inicio[0]<fin[0] else -1,1 if inicio[1]<fin[1] else -1
    
    def tiro_directo(self,bolaSeleccionada,tronera):
        radioBola=8
        xt=tronera[0]-self.XIROI
        yt=tronera[1]-self.YIROI
        (xb,yb,_)=self.bolaBlancaSinROI #self.listaApareada[0][0]
        (xo,yo,_)= bolaSeleccionada #self.listaApareada[2][0]
        angulo=abs(math.atan((yo-yt)/(xo-xt)))
        
        sx,sy=self.definir_signos((xt,yt),(xo,yo))
        xi,yi=(xo+sx*2*radioBola*math.cos(angulo),yo+sy*2*radioBola*math.sin(angulo))
        angulo2=abs(math.atan((yi-yb)/(xi-xb)))
        sx,sy=self.definir_signos((xb,yb),(xi,yi))
        return (sx*math.cos(angulo2),sy*math.sin(angulo2))
    