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
        self.velocidades=45

    def definir_signos(self,inicio,fin):
        return 1 if inicio[0]<fin[0] else -1,1 if inicio[1]<fin[1] else -1

    def camino_libre(obj1,obj2):
        return None

    def calcular(self):
        (vx,vy)=self.tiros_posibles()
        self.fisicas.setear_velocidad_inicial_blanca(vx,vy) #20 35
        self.fisicas.setear_pasos_tiempo(1)
        self.fisicas.simular()
    
    def tiros_posibles(self):
        tronera=self.troneras_posibles()
        radioBola=8
        xt=tronera[0]-self.XIROI
        yt=tronera[1]-self.YIROI
        (xb,yb,radioBola)=self.listaApareada[0][0]
        (xo,yo,_)=self.listaApareada[2][0]
        angulo=abs(math.atan((yo-yt)/(xo-xt)))
        
        sx,sy=self.definir_signos((xt,yt),(xo,yo))
        xi,yi=(xo+sx*2*radioBola*math.cos(angulo),yo+sy*2*radioBola*math.sin(angulo))
        angulo2=abs(math.atan((yi-yb)/(xi-xb)))
        sx,sy=self.definir_signos((xb,yb),(xi,yi))
        return (sx*self.velocidades*math.cos(angulo2),sy*self.velocidades*math.sin(angulo2))
    
    def troneras_posibles(self):
        return self.troneras[6-1]
   
    