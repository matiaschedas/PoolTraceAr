from CalculadorTirosFisica import CalculadorTirosFisica




ROI=(693.0, 351.0)
XIROI=184
YIROI=84
XDROI=877 
YDROI=435
troneras=[(174, 78),(533, 73),(889, 78), (174, 448), (532, 453),(890, 449)]
radioTronera=19
radioBolas=13 #Max radio
puntosParedes=[(0, 0), (5, 0), (10, 0), (15, 0), (0, 5), (20, 5), (0, 10), (20, 10), (0, 15), (5, 15), (10, 15), (15, 15)]

bolaSeleccionada=(350+XIROI,100+YIROI,8)
bolaBlanca=(400+XIROI,200+YIROI,9)
bs=(bolaSeleccionada[0]-XIROI,bolaSeleccionada[1]-YIROI,bolaSeleccionada[2])
bb=(bolaBlanca[0]-XIROI,bolaBlanca[1]-YIROI,bolaBlanca[2])

listaApareada=[
 (bb, 'crop_1_20230829_165538.png', 'Blanca'),
 ((394, 800, 9), 'crop_2_20230829_165538.png', 'Negra'),
 (bs, 'crop_3_20230829_165538.png', 'Lisa')
]

calculador=CalculadorTirosFisica(True,True,True,listaApareada,bolaSeleccionada,bolaBlanca,ROI,XIROI,YIROI,XDROI,YDROI,troneras,radioTronera,radioBolas,puntosParedes,False,False,False)
calculador.calcular()
