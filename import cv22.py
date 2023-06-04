import cv2
import numpy as np

class Bola:
    bolas=[]
    id_counter = 1
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.id = Bola.id_counter
        Bola.id_counter += 1
        self.prev_pos=None
        self.prev_time=None
        bolas.append(self)
    def buscar_bola(self,x,y):
        for bola in bolas:
            if bola.x == x and bola.y == y:
                return bola
            return None

def comprobar_bola_existe(x,y,bolas):
    for bola in bolas:
        if bola.x == x and bola.y == y:
                return True
        return False
    return False

def obtener_bola(x,y,bolas):
    for bola in bolas:
        if bola.x == x and bola.y == y:
            return bola
        return None
    return None

def eliminar_bolas(bolas, circles):
    esta = False
    for bola in bolas:
        for (x,y,r) in circles:
            if bola.x == x and bola.y == y:
                esta = True
        if esta==True:
            esta=False
        else:
            bolas.remove(bola)
            esta=False
    return bolas

def button_clicked(x,y):
    print("----------------------------------------------Button %d %d clicked!" % (x, y))  

def mouse_callback(event, x, y, flags, param):
        global buttons
        if event == cv2.EVENT_LBUTTONUP:
         # Buscar el botón que se encuentra en la posición actual
         for xc,yc,rc in circles:
            dist=np.sqrt(((x-100) - xc) ** 2 + ((y-100) - yc) ** 2)
            #print("distancia:")
            #print(f'({dist})')
            if dist < 20:
                 button_clicked(x, y)    
                

# Inicializa la cámara web
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Define las coordenadas de la región de interés
roi_x1, roi_y1 = 100, 100
roi_x2, roi_y2 = 1110, 600
prev_pos = None
prev_time = None
velocity=0
bolas=[]
min_move=5
fps = 30
bola_posiciones_previas = {}
velocidades = []
frame_count=0
velocidad_px_s=0
lChemin = []

while True:
    # Lee el siguiente fotograma de la cámara
    ret, frame = cap.read()
    frame_count += 1
    # Selecciona la región de interés
    roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]

    # Convierte la región de interés a escala de grises
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    #eq = cv2.equalizeHist(gray)
    #thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2) 
    # Aplica un filtro de suavizado
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detecta los círculos en la imagen
    circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1, 17, param1=100, param2=12, minRadius=5, maxRadius=10)
    

    # Si se han detectado círculos
    if circles is not None:
        # Convierte las coordenadas de los círculos a enteros
        circles = np.round(circles[0, :]).astype("int")
        # Para cada círculo
        for (x, y, r) in circles:
            # Calcula la media de los píxeles dentro del círculo
            mean_val = np.mean(gray[y-r:y+r, x-r:x+r])
            white_pixels = np.sum(gray[y-r:y+r, x-r:x+r] > mean_val)
            circle_area = np.pi * r * r
            white_ratio = white_pixels / circle_area
            
            # Dibuja un círculo alrededor de la bola
            cv2.circle(frame, (x+roi_x1, y+roi_y1), r+10, (0, 255, 0), 2)

            # Si la media es menor que un umbral, la bola es rayada
            if white_ratio > 0.5:
                cv2.putText(frame, f"Rayada {white_ratio:.1f}", (x+roi_x1+10, y+roi_y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            else:
                cv2.putText(frame, f"Lisa {white_ratio:.1f}", (x+roi_x1+10, y+roi_y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            #determinar la velocidad de cada bola individual
            if 'previous_centers' not in globals():
                previous_centers = np.array([[x, y]])
            else:
                distances = np.sqrt(np.sum(np.power(previous_centers - np.array([x, y]), 2), axis=1))
                min_distance = np.min(distances)
                index = np.argmin(distances)
                if min_distance < r:
                    velocity = previous_centers[index] - np.array([x, y])
                    diferencia_tiempo_seg = 1.0 / fps
                    velocidad_px_s = np.sqrt(np.sum(np.power(velocity, 2))) / diferencia_tiempo_seg
                    #imprime la velocidad de cada bola
                    cv2.putText(frame,f"V: {velocidad_px_s:.1f}",(x+roi_x1+10, y+roi_y1+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                previous_centers = np.vstack([previous_centers, np.array([x, y])])

        
    # Dibuja un rectángulo que representa la región de interés
    cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (255, 0, 0), 2)
    
    # Muestra la imagen resultante
    cv2.imshow("Output", frame)
    cv2.setMouseCallback("Output", mouse_callback)
    # Espera la tecla 'q' para salir
    if cv2.waitKey(1) == ord('q'):
        break
    
# Libera la cámara y cierra todas las ventanas
cap.release()
cv2.destroyAllWindows()
