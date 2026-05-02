"""Logica de generacion de menu (sin dependencias de GUI)."""

import random
from datetime import date
from recetas import RECETAS, INGREDIENTES, COLORES_CATEGORIA, DESAYUNOS, FRUTAS, Receta

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MOMENTOS = ["Desayuno", "Comida", "Cena"]

def temporada_actual():
    mes = date.today().month
    if mes in (11, 12, 1, 2):
        return "invierno"
    elif mes in (3, 4):
        return "primavera"
    elif mes in (5, 6, 7, 8, 9):
        return "verano"
    else:
        return "otoño"


def recetas_disponibles(hora, temporada, ingredientes_usuario, tipo=None):
    """Filtra recetas por hora, temporada, ingredientes y opcionalmente tipo."""
    resultado = []
    for r in RECETAS:
        if not r.en_hora(hora):
            continue
        if not r.en_temporada(temporada):
            continue
        if tipo and r.tipo != tipo:
            continue
        if ingredientes_usuario:
            if any(ing in ingredientes_usuario for ing in r.ingredientes):
                resultado.append(r)
        else:
            resultado.append(r)
    if not resultado:
        resultado = [r for r in RECETAS if r.en_hora(hora) and r.en_temporada(temporada) and (not tipo or r.tipo == tipo)]
    return resultado


def nombre_con_segundo(receta, segundo):
    """Combina nombre de acompañamiento + segundo."""
    return f"{receta.nombre} + {segundo.nombre}"


def buscar_receta(nombre):
    """Busca receta por nombre (o nombre compuesto)."""
    for r in RECETAS:
        if r.nombre == nombre:
            return r
    return None


def generar_menu(ingredientes_usuario, exclusiones, celdas_fijas):
    """
    Genera menú semanal balanceado.
    - Comidas (no pescado) dan para 2 días consecutivos
    - Acompañamientos se emparejan con un segundo
    - Huevos 3-4/semana por ingrediente
    - No repite en días consecutivos
    """
    temporada = temporada_actual()
    menu = {}
    conteo_huevos = 0
    conteo_frituras = 0
    conteo_pasta = 0

    # --- Desayunos ---
    for dia in DIAS:
        clave = (dia, "Desayuno")
        if clave in celdas_fijas:
            menu[clave] = celdas_fijas[clave]
        elif clave in exclusiones:
            menu[clave] = None
        elif dia == "Sábado":
            menu[clave] = "Desayuno libre 🎉"
        else:
            fruta = random.choice(FRUTAS)
            desayuno = random.choice(DESAYUNOS)
            menu[clave] = f"{desayuno} + {fruta}"
            if "huevo" in desayuno.lower():
                conteo_huevos += 1

    # --- Comidas (raciones para 2 días, excepto pescado) ---
    comidas_completas = recetas_disponibles("comida", temporada, ingredientes_usuario, "completo")
    comidas_acomp = recetas_disponibles("comida", temporada, ingredientes_usuario, "acompañamiento")
    comidas_segundo = recetas_disponibles("comida", temporada, ingredientes_usuario, "segundo")
    comidas_pool = comidas_completas + comidas_acomp
    random.shuffle(comidas_pool)

    # Pares alternos para raciones dobles (no pescado): Lun-Mie, Mar-Jue
    pares_alternos = [("Lunes", "Miércoles"), ("Martes", "Jueves")]
    dias_comida = [d for d in DIAS if (d, "Comida") not in exclusiones and (d, "Comida") not in celdas_fijas]
    dias_asignados = set()

    def elegir_receta(dia):
        nonlocal conteo_huevos, conteo_frituras, conteo_pasta
        idx_dia = DIAS.index(dia)
        recetas_ayer = set()
        if idx_dia > 0:
            dia_ant = DIAS[idx_dia - 1]
            for m in ("Comida", "Cena"):
                val = menu.get((dia_ant, m))
                if val:
                    recetas_ayer.add(val)
        opciones = [r for r in comidas_pool if r.nombre not in recetas_ayer]
        if conteo_frituras >= 2:
            opciones = [r for r in opciones if not (r.fritura or r.categoria == "fritura")]
        if conteo_pasta >= 2:
            opciones = [r for r in opciones if r.categoria != "pasta_arroz"]
        if not opciones:
            opciones = [r for r in comidas_pool if not (conteo_frituras >= 2 and (r.fritura or r.categoria == "fritura"))]
        if not opciones:
            opciones = comidas_pool
        receta = random.choice(opciones) if opciones else None
        if not receta:
            return None, None
        if receta.tipo == "acompanamiento" and comidas_segundo:
            segundo = random.choice(comidas_segundo)
            texto = nombre_con_segundo(receta, segundo)
            if segundo.lleva_huevo():
                conteo_huevos += 1
        else:
            texto = receta.nombre
            if receta.lleva_huevo():
                conteo_huevos += 1
        if receta.fritura or receta.categoria == "fritura":
            conteo_frituras += 1
        if receta.categoria == "pasta_arroz":
            conteo_pasta += 1
        return receta, texto

    # Asignar pares alternos (raciones dobles en dias no consecutivos)
    for dia1, dia2 in pares_alternos:
        if dia1 in dias_comida and dia1 not in dias_asignados:
            receta, texto = elegir_receta(dia1)
            if receta and texto:
                menu[(dia1, "Comida")] = texto
                dias_asignados.add(dia1)
                es_pescado = receta.categoria in ("pescado_azul", "pescado_blanco")
                if not es_pescado and dia2 in dias_comida and dia2 not in dias_asignados:
                    menu[(dia2, "Comida")] = texto
                    dias_asignados.add(dia2)

    # Asignar dias restantes individualmente
    for dia in dias_comida:
        if dia not in dias_asignados:
            receta, texto = elegir_receta(dia)
            if receta and texto:
                menu[(dia, "Comida")] = texto
                dias_asignados.add(dia)

    # --- Cenas ---
    cenas_completas = recetas_disponibles("cena", temporada, ingredientes_usuario, "completo")
    cenas_acomp = recetas_disponibles("cena", temporada, ingredientes_usuario, "acompañamiento")
    cenas_segundo = recetas_disponibles("cena", temporada, ingredientes_usuario, "segundo")
    cenas_pool = cenas_completas + cenas_acomp
    random.shuffle(cenas_pool)

    dias_cena = [d for d in DIAS if (d, "Cena") not in exclusiones and (d, "Cena") not in celdas_fijas]
    for dia in dias_cena:
        clave = (dia, "Cena")
        idx_dia = DIAS.index(dia)

        evitar = set()
        comida_hoy = menu.get((dia, "Comida"))
        if comida_hoy:
            evitar.add(comida_hoy)
        if idx_dia > 0:
            dia_ant = DIAS[idx_dia - 1]
            for m in ("Comida", "Cena"):
                val = menu.get((dia_ant, m))
                if val:
                    evitar.add(val)

        # Preferir recetas con huevo si no llegamos a 3-4/semana
        preferir_huevo = conteo_huevos < 3
        opciones = [r for r in cenas_pool if r.nombre not in evitar]
        if conteo_frituras >= 2:
            opciones = [r for r in opciones if not (r.fritura or r.categoria == "fritura")]
        if conteo_pasta >= 2:
            opciones = [r for r in opciones if r.categoria != "pasta_arroz"]
        if not opciones:
            opciones = cenas_pool

        if preferir_huevo:
            con_huevo = [r for r in opciones if r.lleva_huevo()]
            if con_huevo:
                opciones = con_huevo

        receta = random.choice(opciones) if opciones else None
        if receta:
            if receta.tipo == "acompañamiento" and cenas_segundo:
                segundo = random.choice(cenas_segundo)
                texto = nombre_con_segundo(receta, segundo)
                if receta.lleva_huevo() or segundo.lleva_huevo():
                    conteo_huevos += 1
            else:
                texto = receta.nombre
                if receta.lleva_huevo():
                    conteo_huevos += 1
            if receta.fritura or receta.categoria == "fritura":
                conteo_frituras += 1
            menu[clave] = texto

    # Añadir celdas fijas y exclusiones
    for clave, valor in celdas_fijas.items():
        menu[clave] = valor
    for clave in exclusiones:
        if clave not in celdas_fijas:
            menu[clave] = None

    return menu


def color_para_nombre(nombre):
    """Busca color por nombre. Soporta nombres compuestos (acomp + segundo)."""
    # Intentar con el nombre completo primero
    for r in RECETAS:
        if r.nombre == nombre:
            return COLORES_CATEGORIA.get(r.categoria, "#FFFFFF")
    # Si es compuesto, usar la primera parte
    if " + " in nombre:
        parte = nombre.split(" + ")[0]
        for r in RECETAS:
            if r.nombre == parte:
                return COLORES_CATEGORIA.get(r.categoria, "#FFFFFF")
    return "#FFFFFF"


