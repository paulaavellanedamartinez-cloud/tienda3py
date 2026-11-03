# TiendaPy

Proyecto final del curso Python 0 a 100 (ACM). Es una aplicación de consola para llevar el inventario y las ventas de una tienda de barrio.

## Problema

El caso es la tienda de Don Aurelio, en Kennedy, Bogotá. Él lleva todo en un cuaderno y eso le trae problemas: no se da cuenta de qué productos se le están acabando hasta que un cliente los pide, suma las ventas a mano y se equivoca en el cambio, no sabe qué productos llevan semanas sin venderse, y al final del día no puede saber cuánto vendió. Además el cuaderno se le ha perdido y mojado.

Con TiendaPy puede:

- Agregar, buscar, modificar y eliminar productos del inventario.
- Registrar ventas con varios productos. El programa calcula el descuento, el total y el cambio.
- Ver los productos que se están acabando, agrupados por proveedor.
- Hacer el cierre del día: total vendido, número de ventas, ticket promedio, producto más vendido y productos sin ventas.
- Guardar el inventario y las ventas en archivos para que no se pierdan.

Las reglas que tiene el programa son: no se puede vender más de lo que hay en stock, no se aceptan precios ni cantidades negativas o en cero, los códigos no se pueden repetir, el pago no puede ser menor al total, y hay descuento del 5 % si la compra es de $50.000 o más y del 10 % si es de $100.000 o más.

## Cómo correrlo

1. Clonar el repositorio:

        git clone https://github.com/paulaavellanedamartinez-cloud/tienda3py.git
        cd tienda3py

2. Crear el entorno virtual (venv). En Windows:

        py -m venv venv
        .\venv\Scripts\Activate.ps1

   En Linux o Mac:

        python3 -m venv venv
        source venv/bin/activate

   Cuando está activado aparece (venv) al comienzo de la línea de la terminal.

3. Instalar la librería que necesita:

        pip install -r requirements.txt

4. Correr el programa desde la carpeta principal (la que tiene `src` y `data`):

        python src/main.py

Lo primero que pide es la fecha de hoy, así: 2026-11-02.

## Librería que usamos

Usamos `tabulate` (versión 0.10.0), que es la que recomendaba el enunciado. Sirve para mostrar el inventario, el detalle de la venta y los reportes en tablas. Probamos primero con prints normales, pero las columnas se descuadraban cuando los nombres de los productos eran largos, y con tabulate quedan alineadas y se lee mucho mejor.

## Archivos

    tiendapy/
    |-- README.md
    |-- requirements.txt
    |-- data/
    |   |-- inventario.txt
    |   `-- ventas.txt
    `-- src/
        `-- main.py

Todo el código está en un solo archivo, `main.py`, dividido por secciones: constantes, pedir datos, fechas, persistencia, inventario, ventas, reportes y menús. Lo dejamos en un solo archivo porque el enunciado lo permite y es más fácil de ejecutar. No usamos clases, los productos son diccionarios.

`data/inventario.txt` tiene un producto por línea, separado por `|`:

    codigo|nombre|categoria|precio|stock|stock_minimo|proveedor

`data/ventas.txt` tiene una venta por línea:

    fecha|total|codigo:cantidad;codigo:cantidad

## Errores

Si se escribe una letra donde va un número, el programa avisa y vuelve a preguntar. Si no existe `inventario.txt`, empieza con el inventario vacío. Si una línea del archivo está dañada, la salta y muestra un aviso. Cuando se rompe una regla del negocio se usa `raise` con una excepción que se llama `ReglaNegocioError`, y se atrapa en el menú para que el programa siga funcionando.
