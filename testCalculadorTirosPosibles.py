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
              

bolaSeleccionada=(70, 100, 8) 
bolaBlanca=(400, 200, 9)

bs=(bolaSeleccionada[0], bolaSeleccionada[1], bolaSeleccionada[2])
bb=(bolaBlanca[0], bolaBlanca[1], bolaBlanca[2])

#la lista apareada no lleva la suma de ROI
listaApareada=[
 (bb, 'crop_1_20230829_165538.png', 'Blanca'),
 ((394, 800, 8), 'crop_2_20230829_165538.png', 'Negra'),
 (bs, 'crop_3_20230829_165538.png', 'Rayada'),
 ((394, 500, 8), 'crop_3_20230829_165538.png', 'Lisa')
]

#print(bolaSeleccionada)

calculador=CalculadorTirosFisica(True,False,True,listaApareada,bolaSeleccionada,bolaBlanca,ROI,XIROI,YIROI,XDROI,YDROI,troneras,radioTronera,radioBolas,puntosParedes,False,False,False)
calculador.calcular()
# for n in range(0, 6, 1):
#     calculador=CalculadorTirosFisica(True,False,True,listaApareada,bolaSeleccionada,bolaBlanca,ROI,XIROI,YIROI,XDROI,YDROI,troneras,radioTronera,radioBolas,puntosParedes,False,False,False)
#     calculador.calcular()
