# TiendaPy - tienda Don Aurelio (todo en un solo archivo)
# Correr desde la carpeta tiendapy:  python src/main.py
from pathlib import Path

from tabulate import tabulate

# ==================== Constantes ====================

CATS = ["Lacteos", "Bebidas", "Aseo", "Abarrotes", "Snacks"]

# Acepta la categoría con o sin tilde y en minúscula
ALIAS = {
    "lacteos": "Lacteos",
    "lácteos": "Lacteos",
    "bebidas": "Bebidas",
    "aseo": "Aseo",
    "abarrotes": "Abarrotes",
    "snacks": "Snacks",
}

# Tope para no aceptar números absurdos (ni inf ni nan)
MAX = 1_000_000_000_000

# Ojo: las rutas son relativas, hay que correr desde tiendapy/
RUTA_INV = Path("data") / "inventario.txt"
RUTA_VENTAS = Path("data") / "ventas.txt"

DESC_5 = 50_000
DESC_10 = 100_000

COLS = ["Código", "Nombre", "Categoría", "Precio", "Unidades",
        "Mínimo", "Proveedor"]

MENU = """
===== TIENDAPY - Tienda Don Aurelio =====
1. Inventario (ver y cambiar productos)
2. Registrar una venta
3. Productos por agotarse
4. Cierre del día
5. Guardar cambios
0. Salir
"""

MENU_INV = """
--- Inventario ---
1. Agregar un producto
2. Buscar un producto por su código
3. Ver los productos de una categoría
4. Ver todos los productos
5. Cambiar el precio o las unidades de un producto
6. Eliminar un producto
0. Volver al menú principal
"""


class ReglaNegocioError(Exception):
    pass


# ==================== Formato ====================

def formato_cop(v):
    # 4200.0 -> $4,200
    return f"${v:,.0f}"


def mostrar_tabla(filas, cols):
    print(tabulate(filas, headers=cols, tablefmt="grid"))


def nombre_visible(cat):
    # En el archivo va "Lacteos", en pantalla "Lácteos"
    if cat == "Lacteos":
        return "Lácteos"
    return cat


# ==================== Pedir datos ====================

def pedir_texto(msg):
    # No puede ir vacío ni llevar "|" (es el separador del archivo)
    while True:
        txt = input(msg).strip()
        if txt == "":
            print("Este campo no puede quedar vacío.")
        elif "|" in txt:
            print("No se puede usar el símbolo '|'. Escríbalo sin ese símbolo.")
        else:
            return txt


def pedir_codigo(msg):
    # Siempre en mayúscula y sin espacios, ni ":" ni ";"
    while True:
        cod = pedir_texto(msg).upper()
        if " " in cod or ":" in cod or ";" in cod:
            print("El código no puede tener espacios ni los símbolos ':' o ';'.")
        else:
            return cod


def pedir_entero(msg, mn=1):
    while True:
        try:
            n = int(input(msg).strip())
        except ValueError:
            print("Escriba un número entero, sin letras ni decimales.")
            continue
        if n < mn:
            print(f"Escriba un número mayor o igual a {mn}.")
            continue
        return n


def pedir_decimal_positivo(msg):
    while True:
        try:
            n = float(input(msg).strip())
        except ValueError:
            print("Escriba un número válido, por ejemplo 4200 o 4200.5.")
            continue
        if not 0 < n < MAX:
            print("Escriba un valor mayor que cero.")
            continue
        return n


def pedir_opcion(msg, validas):
    while True:
        op = input(msg).strip().lower()
        if op in validas:
            return op
        print("Esa opción no existe. Intente de nuevo.")


def confirmar(msg):
    return pedir_opcion(msg + " (s = sí, n = no): ", ["s", "n"]) == "s"


def pedir_categoria():
    ops = []
    for i, cat in enumerate(CATS, start=1):
        print(f"  {i}. {nombre_visible(cat)}")
        ops.append(str(i))
    n = pedir_opcion("Elija la categoría (escriba el número): ", ops)
    return CATS[int(n) - 1]


def normalizar_categoria(txt):
    # "Lácteos" -> "Lacteos". Si no existe, ValueError
    k = txt.strip().lower()
    if k not in ALIAS:
        raise ValueError(f"la categoría '{txt}' no existe")
    return ALIAS[k]


# ==================== Fechas ====================

def es_bisiesto(anio):
    return (anio % 4 == 0 and anio % 100 != 0) or anio % 400 == 0


def es_fecha_valida(txt):
    # Formato AAAA-MM-DD
    p = txt.split("-")
    if len(p) != 3 or len(p[0]) != 4 or len(p[1]) != 2 or len(p[2]) != 2:
        return False
    try:
        anio = int(p[0])
        mes = int(p[1])
        dia = int(p[2])
    except ValueError:
        return False
    if not 1 <= mes <= 12:
        return False
    dias = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    tope = dias[mes - 1]
    if mes == 2 and es_bisiesto(anio):
        tope = 29
    return 1 <= dia <= tope


def pedir_fecha(msg, defecto=None):
    # Con Enter se usa la fecha por defecto (si hay)
    while True:
        txt = input(msg).strip()
        if txt == "" and defecto is not None:
            return defecto
        if es_fecha_valida(txt):
            return txt
        print("Esa fecha no es válida. Escríbala así: AAAA-MM-DD (ej. 2026-11-20).")


# ==================== Persistencia ====================

def leer_producto(lin):
    # Una línea del archivo -> dict. Si viene mal, ValueError con el motivo
    p = lin.split("|")
    if len(p) != 7:
        raise ValueError(f"debe tener 7 datos separados por '|' y tiene {len(p)}")

    cod = p[0].strip().upper()
    nom = p[1].strip()
    prov = p[6].strip()
    if cod == "" or nom == "" or prov == "":
        raise ValueError("hay datos vacíos")

    cat = normalizar_categoria(p[2])

    try:
        precio = float(p[3])
        stock = int(p[4])
        mn = int(p[5])
    except ValueError:
        raise ValueError("el precio, las unidades o el mínimo no son números")

    # Esta comparación también saca nan e inf
    if not 0 < precio < MAX or stock < 0 or mn < 0:
        raise ValueError("el precio o las cantidades no son válidos")

    return {
        "codigo": cod,
        "nombre": nom,
        "categoria": cat,
        "precio": precio,
        "stock": stock,
        "stock_minimo": mn,
        "proveedor": prov,
    }


def cargar_inventario(ruta=RUTA_INV):
    # Salta las líneas dañadas (avisando). Si no hay archivo, arranca vacío
    inv = {}
    try:
        with ruta.open("r", encoding="utf-8", errors="replace") as f:
            for n, lin in enumerate(f, start=1):
                lin = lin.strip()
                if lin == "":
                    continue
                try:
                    prod = leer_producto(lin)
                except ValueError as e:
                    print(f"Aviso: se saltó la línea {n} del inventario ({e}).")
                    continue
                if prod["codigo"] in inv:
                    print(f"Aviso: se saltó la línea {n} del inventario "
                          f"(el código '{prod['codigo']}' está repetido).")
                    continue
                inv[prod["codigo"]] = prod
    except FileNotFoundError:
        print(f"Aviso: no se encontró el archivo '{ruta}'. Se empieza con el inventario vacío.")
    return inv


def guardar_inventario(inv, ruta=RUTA_INV):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8") as f:
        for p in inv.values():
            f.write(
                f"{p['codigo']}|{p['nombre']}|{p['categoria']}|{p['precio']}|"
                f"{p['stock']}|{p['stock_minimo']}|{p['proveedor']}\n"
            )


def registrar_venta(fecha, total, carro, ruta=RUTA_VENTAS):
    # Agrega al final: fecha|total|cod:cant;cod:cant
    det = ""
    for cod, cant in carro.items():
        if det != "":
            det += ";"
        det += f"{cod}:{cant}"

    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("a", encoding="utf-8") as f:
        f.write(f"{fecha}|{total}|{det}\n")


def leer_venta(lin):
    p = lin.split("|")
    if len(p) != 3:
        raise ValueError("debe tener 3 datos separados por '|'")
    fecha = p[0].strip()
    if not es_fecha_valida(fecha):
        raise ValueError("fecha inválida")
    items = {}
    for par in p[2].split(";"):
        cod, cant = par.split(":")  # si no vienen 2 partes, ValueError
        cod = cod.strip()
        items[cod] = items.get(cod, 0) + int(cant)
    return {"fecha": fecha, "total": float(p[1]), "items": items}


def cargar_ventas(ruta=RUTA_VENTAS):
    # Salta las líneas dañadas
    res = []
    try:
        with ruta.open("r", encoding="utf-8", errors="replace") as f:
            for n, lin in enumerate(f, start=1):
                lin = lin.strip()
                if lin == "":
                    continue
                try:
                    res.append(leer_venta(lin))
                except ValueError:
                    print(f"Aviso: se saltó la línea {n} del historial de ventas "
                          "porque tiene un formato inválido.")
    except FileNotFoundError:
        pass  # sin archivo todavía, no pasa nada
    return res


# ==================== Inventario ====================

def obtener_producto(inv, cod):
    if cod not in inv:
        raise ReglaNegocioError(f"No existe ningún producto con el código '{cod}'.")
    return inv[cod]


def crear_producto(inv, cod, nom, cat, precio, stock, mn, prov):
    if cod in inv:
        raise ReglaNegocioError(f"Ya hay un producto con el código '{cod}'.")
    if precio <= 0 or stock <= 0:
        raise ReglaNegocioError("El precio y las unidades deben ser mayores que cero.")
    if mn < 0:
        raise ReglaNegocioError("El stock mínimo no puede ser negativo.")
    inv[cod] = {
        "codigo": cod, "nombre": nom, "categoria": cat,
        "precio": float(precio), "stock": stock,
        "stock_minimo": mn, "proveedor": prov,
    }


def modificar_precio(inv, cod, precio):
    prod = obtener_producto(inv, cod)
    if precio <= 0:
        raise ReglaNegocioError("El precio debe ser mayor que cero.")
    prod["precio"] = float(precio)


def modificar_stock(inv, cod, stock):
    prod = obtener_producto(inv, cod)
    if stock <= 0:
        raise ReglaNegocioError("Las unidades deben ser mayores que cero.")
    prod["stock"] = stock


def eliminar_producto(inv, cod):
    obtener_producto(inv, cod)
    return inv.pop(cod)


def buscar_por_categoria(inv, cat):
    res = []
    for p in inv.values():
        if p["categoria"] == cat:
            res.append(p)
    return res


def mostrar_productos(prods):
    filas = []
    for p in prods:
        filas.append([p["codigo"], p["nombre"], nombre_visible(p["categoria"]),
                      formato_cop(p["precio"]), p["stock"], p["stock_minimo"],
                      p["proveedor"]])
    mostrar_tabla(filas, COLS)


# Opciones del menú de inventario (el menú atrapa los errores)

def registrar_producto(inv):
    print("\n--- Registrar producto ---")
    cod = pedir_codigo("Código del producto (ej. LAC001): ")
    # Se revisa ya para no pedir el resto de datos en vano
    if cod in inv:
        raise ReglaNegocioError(f"Ya hay un producto con el código '{cod}'.")
    nom = pedir_texto("Nombre del producto: ")
    cat = pedir_categoria()
    precio = pedir_decimal_positivo("Precio de venta en pesos: ")
    stock = pedir_entero("Unidades que hay ahora: ")
    mn = pedir_entero("Cantidad mínima para que avise (stock mínimo): ", 0)
    prov = pedir_texto("Nombre del proveedor: ")
    crear_producto(inv, cod, nom, cat, precio, stock, mn, prov)
    print("Producto agregado al inventario.")


def consultar_por_codigo(inv):
    cod = pedir_codigo("Código del producto que busca: ")
    mostrar_productos([obtener_producto(inv, cod)])


def consultar_por_categoria(inv):
    cat = pedir_categoria()
    prods = buscar_por_categoria(inv, cat)
    if not prods:
        print(f"No hay productos en la categoría {nombre_visible(cat)}.")
    else:
        mostrar_productos(prods)


def listar_todos(inv):
    if not inv:
        print("Todavía no hay productos en el inventario.")
    else:
        mostrar_productos(list(inv.values()))


def modificar_producto(inv):
    cod = pedir_codigo("Código del producto que quiere cambiar: ")
    prod = obtener_producto(inv, cod)
    mostrar_productos([prod])
    print("1. Cambiar el precio\n2. Cambiar las unidades disponibles")
    op = input("Elija una opción: ").strip()
    if op == "1":
        modificar_precio(inv, cod, pedir_decimal_positivo("Nuevo precio en pesos: "))
        print("Precio actualizado.")
    elif op == "2":
        modificar_stock(inv, cod, pedir_entero("Nuevas unidades disponibles: "))
        print("Unidades actualizadas.")
    else:
        print("Esa opción no existe.")


def borrar_producto(inv):
    cod = pedir_codigo("Código del producto que quiere eliminar: ")
    mostrar_productos([obtener_producto(inv, cod)])
    if confirmar("¿Está seguro de eliminar este producto?"):
        eliminar_producto(inv, cod)
        print("Producto eliminado.")
    else:
        print("No se eliminó nada.")


# ==================== Ventas ====================

def calcular_porcentaje_descuento(sub):
    # 5 % desde $50.000 y 10 % desde $100.000
    if sub >= DESC_10:
        return 0.10
    if sub >= DESC_5:
        return 0.05
    return 0.0


def agregar_al_carrito(inv, carro, cod, cant):
    # Suma al carrito sin pasarse del stock
    prod = obtener_producto(inv, cod)
    if cant <= 0:
        raise ReglaNegocioError("La cantidad debe ser mayor que cero.")
    ya = carro.get(cod, 0)
    if prod["stock"] == 0:
        raise ReglaNegocioError(f"'{prod['nombre']}' está agotado.")
    if ya + cant > prod["stock"]:
        msg = (f"No hay suficientes unidades de '{prod['nombre']}': "
               f"quedan {prod['stock']}")
        if ya > 0:
            msg += f" y ya tiene {ya} en el carrito"
        raise ReglaNegocioError(msg + ".")
    carro[cod] = ya + cant


def calcular_totales(inv, carro):
    # Devuelve (subtotal, descuento, total)
    sub = 0.0
    for cod, cant in carro.items():
        sub += inv[cod]["precio"] * cant
    desc = round(sub * calcular_porcentaje_descuento(sub), 2)
    return sub, desc, round(sub - desc, 2)


def calcular_cambio(total, pago):
    if pago < total:
        raise ReglaNegocioError(f"El pago no alcanza: faltan {formato_cop(total - pago)}.")
    return pago - total


def confirmar_venta(inv, carro):
    # Primero revisa todo el carrito; si algo falla, el inventario no cambia
    for cod, cant in carro.items():
        prod = obtener_producto(inv, cod)
        if cant > prod["stock"]:
            raise ReglaNegocioError(f"No hay suficientes unidades de '{prod['nombre']}'.")
    for cod, cant in carro.items():
        inv[cod]["stock"] -= cant


def mostrar_detalle(inv, carro):
    filas = []
    for cod, cant in carro.items():
        precio = inv[cod]["precio"]
        filas.append([inv[cod]["nombre"], cant, formato_cop(precio),
                      formato_cop(precio * cant)])
    mostrar_tabla(filas, ["Producto", "Cantidad", "Precio unidad", "Valor"])


def flujo_venta(inv, fecha):
    # Arma la venta. Devuelve el total, o None si se canceló
    carro = {}
    print("\n--- Nueva venta ---")
    print("Escriba el código de cada producto. Cuando termine escriba 'fin',")
    print("o escriba 'cancelar' si no quiere hacer la venta.")

    while True:
        cod = input("Código del producto: ").strip().upper()
        if cod == "FIN":
            break
        if cod == "CANCELAR":
            print("Venta cancelada.")
            return None
        try:
            prod = obtener_producto(inv, cod)
            print(f"  {prod['nombre']} - {formato_cop(prod['precio'])} "
                  f"- quedan {prod['stock']} unidades")
            cant = pedir_entero("  ¿Cuántas unidades? ")
            agregar_al_carrito(inv, carro, cod, cant)
        except ReglaNegocioError as e:
            print(f"Error: {e}")
        else:
            print("  Listo, agregado al carrito.")

    if not carro:
        print("No se agregó ningún producto, así que no se hizo la venta.")
        return None

    print("\nDetalle de la venta:")
    mostrar_detalle(inv, carro)
    sub, desc, total = calcular_totales(inv, carro)
    print(f"Subtotal:  {formato_cop(sub)}")
    print(f"Descuento: {formato_cop(desc)}")
    print(f"TOTAL A PAGAR: {formato_cop(total)}")

    # Se repite hasta que el pago alcance
    while True:
        pago = pedir_decimal_positivo("¿Con cuánto paga el cliente? ")
        try:
            cambio = calcular_cambio(total, pago)
            break
        except ReglaNegocioError as e:
            print(f"Error: {e}")
            if not confirmar("¿Quiere escribir el pago otra vez?"):
                print("Venta cancelada.")
                return None

    if not confirmar("¿Confirmar la venta?"):
        print("Venta cancelada.")
        return None

    confirmar_venta(inv, carro)
    try:
        registrar_venta(fecha, total, carro)
    except OSError:
        # No se pudo guardar: devolvemos el stock para que todo cuadre
        for cod, cant in carro.items():
            inv[cod]["stock"] += cant
        raise
    print(f"Venta registrada. Devuelva de cambio: {formato_cop(cambio)}")
    return total


# ==================== Reportes ====================

def productos_en_alerta(inv):
    # Productos con stock <= mínimo, agrupados por proveedor
    res = {}
    for p in inv.values():
        if p["stock"] <= p["stock_minimo"]:
            prov = p["proveedor"]
            if prov not in res:
                res[prov] = []
            res[prov].append(p)
    return res


def mostrar_alertas(inv):
    print("\n--- Productos por agotarse ---")
    res = productos_en_alerta(inv)
    if not res:
        print("Por ahora ningún producto se está agotando.")
        return
    for prov in sorted(res):
        print(f"\nProveedor: {prov}")
        filas = []
        for p in res[prov]:
            est = "AGOTADO" if p["stock"] == 0 else "Quedan pocas"
            filas.append([p["codigo"], p["nombre"], p["stock"],
                          p["stock_minimo"], est])
        mostrar_tabla(filas, ["Código", "Producto", "Unidades", "Mínimo", "Estado"])


def calcular_cierre(inv, ventas, fecha):
    # Números del día en un dict
    total = 0.0
    n_ventas = 0
    unid = {}  # unidades vendidas por código ese día

    for v in ventas:
        if v["fecha"] != fecha:
            continue
        n_ventas += 1
        total += v["total"]
        for cod, cant in v["items"].items():
            unid[cod] = unid.get(cod, 0) + cant

    ticket = total / n_ventas if n_ventas > 0 else 0.0

    top = None
    mayor = 0
    for cod, cant in unid.items():
        if cant > mayor:
            mayor = cant
            nom = inv[cod]["nombre"] if cod in inv else cod
            top = (nom, cant)

    sin_ventas = []
    for cod, p in inv.items():
        if cod not in unid:
            sin_ventas.append(p["nombre"])

    cats = set()
    for cod in unid:
        if cod in inv:
            cats.add(inv[cod]["categoria"])

    return {
        "total": total, "ventas": n_ventas, "ticket": ticket,
        "mas_vendido": top, "sin_ventas": sin_ventas,
        "categorias": sorted(cats),
    }


def mostrar_cierre(inv, ventas, fecha):
    c = calcular_cierre(inv, ventas, fecha)
    print(f"\n--- Cierre del día {fecha} ---")
    if c["mas_vendido"] is not None:
        nom, cant = c["mas_vendido"]
        top = f"{nom} ({cant} uds)"
    else:
        top = "Ninguno"
    cats = ""
    for cat in c["categorias"]:
        if cats != "":
            cats += ", "
        cats += nombre_visible(cat)
    if cats == "":
        cats = "Ninguna"
    mostrar_tabla([
        ["Total vendido", formato_cop(c["total"])],
        ["Ventas realizadas", c["ventas"]],
        ["Promedio por venta (ticket)", formato_cop(c["ticket"])],
        ["Producto más vendido", top],
        ["Categorías que se vendieron", cats],
    ], ["Resumen del día", "Valor"])

    print("\nProductos que no se vendieron:")
    if c["sin_ventas"]:
        for nom in c["sin_ventas"]:
            print(f"  - {nom}")
    else:
        print("  (todos los productos se vendieron)")


# ==================== Menús ====================

def menu_inventario(inv):
    acciones = {
        "1": registrar_producto,
        "2": consultar_por_codigo,
        "3": consultar_por_categoria,
        "4": listar_todos,
        "5": modificar_producto,
        "6": borrar_producto,
    }
    while True:
        print(MENU_INV)
        op = pedir_opcion("Elija una opción: ", ["0", "1", "2", "3", "4", "5", "6"])
        if op == "0":
            return
        try:
            acciones[op](inv)
        except ReglaNegocioError as e:
            print(f"Error: {e}")


def guardar(inv):
    try:
        guardar_inventario(inv)
    except OSError as e:
        print(f"No se pudo guardar el inventario ({e}). "
              "Revise que el archivo no esté abierto en otro programa.")
    else:
        print("Inventario guardado.")


def menu_principal(inv, hoy):
    while True:
        print(MENU)
        op = pedir_opcion("Elija una opción: ", ["0", "1", "2", "3", "4", "5"])
        try:
            if op == "1":
                menu_inventario(inv)
            elif op == "2":
                # Si hubo venta se guarda de una vez, así no se pierde el stock
                if flujo_venta(inv, hoy) is not None:
                    guardar(inv)
            elif op == "3":
                mostrar_alertas(inv)
            elif op == "4":
                fecha = pedir_fecha(
                    f"Fecha del cierre (AAAA-MM-DD). Enter para usar {hoy}: ", hoy)
                mostrar_cierre(inv, cargar_ventas(), fecha)
            elif op == "5":
                guardar(inv)
            else:
                return
        except ReglaNegocioError as e:
            print(f"Error: {e}")
        except OSError as e:
            print(f"Problema con un archivo: {e}")


def main():
    inv = cargar_inventario()
    print(f"Se cargaron {len(inv)} productos del inventario.")
    hoy = pedir_fecha("¿Qué fecha es hoy? Escríbala así, AAAA-MM-DD (ej. 2026-11-20): ")
    try:
        menu_principal(inv, hoy)
    except (KeyboardInterrupt, EOFError):
        print("\nSe interrumpió el programa.")
    finally:
        guardar(inv)
        print("¡Hasta pronto!")


main()
