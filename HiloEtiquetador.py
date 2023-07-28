
import threading
import time
import os

ListaApareadaConEtiquetas = []
variable_compartida_lock = threading.Lock()


def Etiquetar(path, ListaApareada, eliminarCapturas):
    print("inicia hilo etiquetador") 
    global ListaApareadaConEtiquetas
    with variable_compartida_lock:
        for elemento in ListaApareada:
            (((x,y,r),nombreBola)) = elemento
            #reemplazar por llamada al metodo:
            etiqueta = "rayada"
            ListaApareadaConEtiquetas.append(((x,y,r),nombreBola,etiqueta))
            if(eliminarCapturas):
                BorrarFoto(path, nombreBola)
            time.sleep(1)

def BorrarFoto (path, nombreFoto):
    rutaCompleta = os.path.join(path, nombreFoto)
    if (os.path.exists(rutaCompleta)):
        os.remove(rutaCompleta)
