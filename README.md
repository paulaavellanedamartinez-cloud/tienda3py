# TiendaPy

App de consola para la tienda Don Aurelio: inventario, ventas, alertas y cierre del día.

## Instalar

    pip install -r requirements.txt

## Correr (desde esta carpeta)

    python src/main.py

## Archivos

- `src/main.py`: todo el programa
- `data/inventario.txt`: `codigo|nombre|categoria|precio|stock|stock_minimo|proveedor`
- `data/ventas.txt`: `fecha|total|cod:cant;cod:cant`
