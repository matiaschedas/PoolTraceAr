from PIL import Image
import os

def resize_images(input_folder, output_folder, new_size=(50, 50)):
    # Asegurarse de que la carpeta de salida exista
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Recorrer todas las imágenes en la carpeta de entrada
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        try:
            # Abrir la imagen
            img = Image.open(input_path)

            # Redimensionar la imagen
            resized_img = img.resize(new_size)

            # Guardar la imagen redimensionada en la carpeta de salida
            resized_img.save(output_path)

            print(f"Imagen {filename} redimensionada con éxito.")
        except Exception as e:
            print(f"Error al procesar la imagen {filename}: {str(e)}")

# Especificar la carpeta de entrada y salida
input_folder = "C:\\Users\\matia\\Desktop\\training_data\\Rayada"
output_folder = "C:\\Users\\matia\\Desktop\\training_data\\RayadaOutput"

# Llamar a la función para redimensionar las imágenes
resize_images(input_folder, output_folder)