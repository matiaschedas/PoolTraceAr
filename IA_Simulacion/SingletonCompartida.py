
class SingletonCompartida:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonCompartida, cls).__new__(cls)
            cls._instance.init_singletonCompartida(*args, **kwargs)
        return cls._instance
    
    def init_singletonCompartida(self, listaApareada=None, bolaSeleccionada=None, tamROI=None, embocarNegra=None):
        self.listaApareada = listaApareada
        self.bolaSeleccionada = bolaSeleccionada
        self.tamROI = tamROI
        if(self.tamROI is not None):
            self.ancho, self.alto = self.tamROI
        self.embocarNegra = embocarNegra
        if(listaApareada is not None and bolaSeleccionada is not None):
            self.etiquetaDeSeleccionada = self.obtenerEtiquetaSeleccionada(listaApareada,bolaSeleccionada)
        else:
            self.etiquetaDeSeleccionada = None

    
    def obtenerEtiquetaSeleccionada(self, listaApareada, bolaSeleccionada):
        for (x,y,r),_,etiqueta in listaApareada:
            xs,ys,rs = bolaSeleccionada
            if(x==xs and y==ys):
                return etiqueta
        return None
    
    @classmethod
    def delete_instance(cls):
        cls._instance = None