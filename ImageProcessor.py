from PIL import Image, ImageDraw
import os


def crop_circles(image_path, coordinates, output_dir):
    try:
        # Cargamos la imagen original
        image = Image.open(image_path)
        margin = 5
        # Iteramos sobre las coordenadas para recortar círculos
        for i, (x, y, r) in enumerate(coordinates):
            left = x - r - margin
            top = y - r - margin
            right = x + r + margin
            bottom = y + r + margin

            # Recortamos el círculo
            crop = image.crop((left, top, right, bottom))

            # Creamos una máscara de círculo
            mask = Image.new('L', crop.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 2 * r + 2 * margin, 2 * r + 2 * margin), fill=255)

            # Aplicamos la máscara al recorte
            crop.putalpha(mask)

            # Guardamos el recorte como una imagen individual
            output_path = f"{output_dir}/crop_{i+1}.png"
            crop.save(output_path)

        print("Círculos recortados y guardados como imágenes individuales en:", output_dir)
        os.remove(image_path)
    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    image_path = "C:\\Users\\matia\\Desktop\\Proyecto fin de carrera\\repo\\Proyecto-fin-de-carrera\\grupo113-PoolTraceAR\\Capturas\\Mesa_20230727_185813.png"
    coordinates = ([544, 340,  16],
       [ 76, 436,  16],
       [ 50, 466,  14],
       [ 50, 466,  16],
       [132, 122,  15],
       [132, 122,  18],
       [102, 324,  13],
       [102, 324,  16],
       [322, 152,  16],
       [608, 312,  16],
       [500, 372,  14],
       [500, 372,  16],
       [828,  28,  13],
       [828,  28,  16],
       [ 54, 192,  16])  
    output_dir="C:/Users/matia/Desktop/Proyecto fin de carrera/repo/Proyecto-fin-de-carrera/grupo113-PoolTraceAR/Capturas/Bolas"
    crop_circles(image_path,coordinates,output_dir)
    # Lista de coordenadas (x, y) # Tamaño del recorte (ancho y alto)