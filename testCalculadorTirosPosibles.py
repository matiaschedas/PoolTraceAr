from CalculadorTirosFisica import CalculadorTirosFisica
from time import time


ROI=(693.0, 351.0)
XIROI=184
YIROI=84
XDROI=877 
YDROI=435
troneras=[(174, 78),(533, 73),(889, 78), (174, 448), (532, 453),(890, 449)]
radioTronera=19
radioBolas=13 #Max radio
puntosParedes=[(0, 0), (5, 0), (10, 0), (15, 0), (0, 5), (20, 5), (0, 10), (20, 10), (0, 15), (5, 15), (10, 15), (15, 15)]
puntosParedes=[(13+XIROI, -12+YIROI), (319.5+XIROI, -12+YIROI),(373.5+XIROI, -12+YIROI), (684.0+XIROI, -12+YIROI),(13, 375.0), (319.5, 375.0),(373.5, 375.0), (684.0, 375.0),(-10, 18), (-10, 341.0),(713.0, 18),(713.0, 341.0)]
bolaSeleccionada=(100+XIROI,50+YIROI,8) #
bolaBlanca=(350+XIROI,100+YIROI,8)
bs=(bolaSeleccionada[0]-XIROI,bolaSeleccionada[1]-YIROI,bolaSeleccionada[2])
bb=(bolaBlanca[0]-XIROI,bolaBlanca[1]-YIROI,bolaBlanca[2])

listaApareada=[
 (bb, 'crop_1_20230829_165538.png', 'Blanca'),
 ((394, 800, 8), 'crop_2_20230829_165538.png', 'Negra'),
 (bs, 'crop_3_20230829_165538.png', 'Lisa')
]

numeroTronera=2
calculador=CalculadorTirosFisica(True,True,True,listaApareada,bolaSeleccionada,bolaBlanca,ROI,XIROI,YIROI,XDROI,YDROI,troneras,radioTronera,radioBolas,puntosParedes,False,False,False)
#calculador.calcular(bs,(troneras[numeroTronera-1][0]-XIROI,troneras[numeroTronera-1][1]-YIROI),100)
start=time()
#calculador.calcular_tiro_posible()
#calculador.test_tiro_con_banda(bs,4,"Superior")
calculador.calcular(bs,1,50)
print(time()-start)
#calculador.prueba_tiro_banda_borrar_despues()


