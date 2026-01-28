
print("¡Hola Mundo! Todo funciona bien.")

# Verificar carpetas
import os

carpetas = ['data/raw', 'data/processed', 'outputs', 'docs']
for carpeta in carpetas:
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    print(f"Carpeta lista: {carpeta}")

print("\n✅ Proyecto listo para comenzar!")