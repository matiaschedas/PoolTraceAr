from IA_Simulacion.pool import PoolEnv
from IA_Simulacion.genetic import Genetic

class IA_Handler ():

    def __init__(self):
        self.poolEnv = PoolEnv(training=False,default=False)    
        self.genetic = Genetic()

    def invocarIA(self, listaApareada, bolaSeleccionada, tamROI, embocarNegra):
        etiquetaSeleccionada = self.obtenerEtiquetaSeleccionada(listaApareada,bolaSeleccionada)
        ancho, alto = tamROI
        self.poolEnv.setearInfo(listaApareada, etiquetaSeleccionada, alto, ancho, embocarNegra)
        self.poolEnv.reset()
        self.genetic.iniciar(self.poolEnv)
        self.poolEnv.close()
        self.poolEnv = None
        self.genetic = None

    def obtenerEtiquetaSeleccionada(self, listaApareada, bolaSeleccionada):
        for (x,y,r),_,etiqueta in listaApareada:
            xs,ys,rs = bolaSeleccionada
            if(x==xs and y==ys):
                return etiqueta
        return None