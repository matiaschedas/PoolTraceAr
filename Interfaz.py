import tkinter as tk
import cv2
from PIL import Image, ImageTk
import time

class VentanaVideo:
    def __init__(self, ventana, video_path):
        self.ventana = ventana
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = 0
        self.start_time = time.time()
        
        self.canvas = tk.Canvas(ventana)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.actualizar_video()

    def actualizar_video(self):
        ret, frame = self.cap.read()

        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen = Image.fromarray(frame_rgb)
            
            # Redimensionar la imagen al tamaño de la ventana
            imagen_resized = imagen.resize((self.ventana.winfo_width(), self.ventana.winfo_height()), Image.ANTIALIAS)
            
            self.imagen_tk = ImageTk.PhotoImage(image=imagen_resized)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imagen_tk)
        
        self.frame_count += 1
        tiempo_actual = time.time() - self.start_time
        tiempo_espera = max(1, int((self.frame_count / self.fps - tiempo_actual) * 1000))
        
        self.ventana.after(tiempo_espera, self.actualizar_video)

# Crear la ventana principal
ventana = tk.Tk()
ventana.geometry("1280x720")

# Crear una instancia de la clase VentanaVideo
video_path = 'video.mp4'  # Reemplaza con la ruta a tu video
ventana_video = VentanaVideo(ventana, video_path)

# Ejecutar el bucle principal de la ventana
ventana.mainloop()
