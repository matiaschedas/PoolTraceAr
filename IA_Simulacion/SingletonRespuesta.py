
class SingletonRespuesta:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonRespuesta, cls).__new__(cls)
            cls._instance.init_singletonCompartida(*args, **kwargs)
        return cls._instance
    
    def init_singletonCompartida(self, primerContacto=None):
        self.primerContacto = primerContacto
       
    @classmethod
    def delete_instance(cls):
        cls._instance = None