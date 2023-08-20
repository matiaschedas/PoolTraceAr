
import threading
import time
import os
from ClasificadorTipoBola import clasificadorTipoBola
from PIL import Image

ListaApareadaConEtiquetas = []
variable_compartida_lock = threading.Lock()


def Etiquetar(path, ListaApareada, eliminarCapturas, guardarHistorial):
    print("inicia hilo etiquetador") 
    global ListaApareadaConEtiquetas
    clasificador = clasificadorTipoBola()

    with variable_compartida_lock:
        for elemento in ListaApareada:
            (((x,y,r),nombreBola)) = elemento
            #reemplazar por llamada al metodo:
            pathFoto = os.path.join(path, nombreBola)
            img = Image.open(pathFoto)
            etiqueta,porcentaje=clasificador.clasificar(img,guardarHistorial)
            ListaApareadaConEtiquetas.append(((x,y,r),nombreBola,etiqueta))
            if(eliminarCapturas):
                BorrarFoto(path, nombreBola)



def BorrarFoto (path, nombreFoto):
    rutaCompleta = os.path.join(path, nombreFoto)
    if (os.path.exists(rutaCompleta)):
        os.remove(rutaCompleta)