
import threading

ListaApareadaConEtiquetas = []
variable_compartida_lock = threading.Lock()

def Etiquetar(path, ListaApareada):
    print("inicia hilo etiquetador") 
    global ListaApareadaConEtiquetas
    with variable_compartida_lock:
        for elemento in ListaApareada:
            (((x,y,r),nombreBola)) = elemento
            #reemplazar por llamada al metodo:
            etiqueta = "rayada"
            ListaApareadaConEtiquetas.append(((x,y,r),nombreBola,etiqueta))