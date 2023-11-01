from PIL import Image, ImageDraw
import os
import cv2
from datetime import datetime

def crop_circles(image, coordinates, output_dir):
    margin = 3
    id = 0
    listaApareada = []
    image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Iterar sobre las coordenadas para recortar círculos
    for i, (x, y, r) in enumerate(coordinates):
        # Ajustar las coordenadas para garantizar que el recorte sea simétrico
        left = int(x - r - margin)
        top = int(y - r - margin)
        right = int(x + r + margin)
        bottom = int(y + r + margin)
        # Recortar el círculo
        crop = image.crop((left, top, right, bottom))

        # Crear una máscara rectangular
        mask = Image.new('L', crop.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rectangle((0, 0, crop.width, crop.height), fill=255)

        # Aplicar la máscara al recorte
        crop.putalpha(mask)

        # Guardar el recorte como una imagen individual
        fecha_hora_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        id = id + 1
        nombreBola = f"crop_{id}_{fecha_hora_actual}.png"
        output_path = os.path.join(output_dir, nombreBola)
        if crop.mode == "RGBA":
            crop = crop.convert("RGB")
        crop.save(output_path)
        listaApareada.append(((x, y, r), nombreBola))

    print("Círculos recortados y guardados como imágenes individuales en:", output_dir)
    return listaApareada




# if __name__ == "__main__":
#     image_path = "C:\\Users\\matia\\Desktop\\Proyecto fin de carrera\\repo\\Proyecto-fin-de-carrera\\grupo113-PoolTraceAR\\Capturas\\Mesa_20230727_185813.png"
#     coordinates = ([544, 340,  16],
#        [ 76, 436,  16],
#        [ 50, 466,  14],
#        [ 50, 466,  16],
#        [132, 122,  15],
#        [132, 122,  18],
#        [102, 324,  13],
#        [102, 324,  16],
#        [322, 152,  16],
#        [608, 312,  16],
#        [500, 372,  14],
#        [500, 372,  16],
#        [828,  28,  13],
#        [828,  28,  16],
#        [ 54, 192,  16])  
#     output_dir="C:/Users/matia/Desktop/Proyecto fin de carrera/repo/Proyecto-fin-de-carrera/grupo113-PoolTraceAR/Capturas/Bolas"
#     crop_circles(image_path,coordinates,output_dir)
    # Lista de coordenadas (x, y) # Tamaño del recorte (ancho y alto)