"""Logica de generacion de menu (sin dependencias de GUI)."""

import random
from datetime import date
from recetas import RECETAS, INGREDIENTES, COLORES_CATEGORIA, DESAYUNOS, FRUTAS, FRUTAS_TEMPORADA, Receta

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


def fruta_semana():
    """Devuelve una fruta de temporada para la semana."""
    temp = temporada_actual()
    opciones = FRUTAS_TEMPORADA.get(temp, FRUTAS)
    return random.choice(opciones)


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
            desayuno = random.choice(DESAYUNOS)
            menu[clave] = desayuno
            if "huevo" in desayuno.lower():
                conteo_huevos += 1

    # --- Comidas (raciones para 2 días, excepto pescado) ---
    comidas_completas = recetas_disponibles("comida", temporada, ingredientes_usuario, "completo")
    comidas_acomp = recetas_disponibles("comida", temporada, ingredientes_usuario, "acompanamiento")
    comidas_segundo = recetas_disponibles("comida", temporada, ingredientes_usuario, "segundo")
    comidas_pool = comidas_completas + comidas_acomp
    random.shuffle(comidas_pool)

    # Pares alternos para raciones dobles (no pescado): Lun-Mie, Mar-Jue
    pares_alternos = [("Lunes", "Miércoles"), ("Martes", "Jueves")]
    dias_comida = [d for d in DIAS if (d, "Comida") not in exclusiones and (d, "Comida") not in celdas_fijas]
    dias_asignados = set()

    def elegir_receta(dia, preferir_doble=None, excluir_cats=None):
        nonlocal conteo_huevos, conteo_frituras, conteo_pasta
        idx_dia = DIAS.index(dia)
        recetas_ayer = set()
        if idx_dia > 0:
            dia_ant = DIAS[idx_dia - 1]
            for m in ("Comida", "Cena"):
                val = menu.get((dia_ant, m))
                if val:
                    recetas_ayer.add(val)
        # Comprobar dias recientes para restricciones de proximidad
        def es_fritura_nombre(nombre):
            for rec in RECETAS:
                if rec.nombre == nombre:
                    return rec.fritura or rec.categoria == "fritura"
            return False
        def es_pasta_nombre(nombre):
            for rec in RECETAS:
                if rec.nombre == nombre:
                    return rec.categoria == "pasta_arroz"
            return False

        # Fritura en los 2 dias anteriores?
        fritura_reciente = False
        for offset in range(1, 3):
            if idx_dia - offset >= 0:
                d = DIAS[idx_dia - offset]
                for m in ("Comida", "Cena"):
                    val = menu.get((d, m))
                    if val and es_fritura_nombre(val):
                        fritura_reciente = True

        # Pasta en los 2 dias anteriores consecutivos?
        pasta_consecutiva = 0
        for offset in range(1, 3):
            if idx_dia - offset >= 0:
                d = DIAS[idx_dia - offset]
                val = menu.get((d, "Comida"))
                if val and es_pasta_nombre(val):
                    pasta_consecutiva += 1
                else:
                    break

        opciones = [r for r in comidas_pool if r.nombre not in recetas_ayer]
        if conteo_frituras >= 2 or fritura_reciente:
            opciones = [r for r in opciones if not (r.fritura or r.categoria == "fritura")]
        if conteo_pasta >= 2 or pasta_consecutiva >= 2:
            opciones = [r for r in opciones if r.categoria != "pasta_arroz"]
        if not opciones:
            opciones = [r for r in comidas_pool if not (conteo_frituras >= 2 and (r.fritura or r.categoria == "fritura"))]
        if not opciones:
            opciones = comidas_pool
        # Excluir categorias si se pide
        if excluir_cats:
            filtrado = [r for r in opciones if r.categoria not in excluir_cats]
            if filtrado:
                opciones = filtrado
        # Filtrar por raciones si se pide
        if preferir_doble is True:
            dobles = [r for r in opciones if r.raciones == 2]
            if dobles:
                opciones = dobles
        elif preferir_doble is False:
            simples = [r for r in opciones if r.raciones == 1]
            if simples:
                opciones = simples
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

    # Asignar pares alternos (raciones=2 van en dias alternos: Lun-Mie, Mar-Jue)
    categorias_pares = set()
    for dia1, dia2 in pares_alternos:
        if dia1 in dias_comida and dia1 not in dias_asignados:
            # Excluir categoria ya usada en par anterior
            pool_par = [r for r in comidas_pool if r.raciones == 2 and r.categoria not in categorias_pares]
            if not pool_par:
                pool_par = [r for r in comidas_pool if r.raciones == 2]
            receta, texto = elegir_receta(dia1, preferir_doble=True, excluir_cats=categorias_pares)
            if receta and texto:
                menu[(dia1, "Comida")] = texto
                dias_asignados.add(dia1)
                categorias_pares.add(receta.categoria)
                if receta.raciones == 2 and dia2 in dias_comida and dia2 not in dias_asignados:
                    menu[(dia2, "Comida")] = texto
                    dias_asignados.add(dia2)

    # Asignar dias restantes individualmente (solo raciones=1)
    for dia in dias_comida:
        if dia not in dias_asignados:
            receta, texto = elegir_receta(dia, preferir_doble=False)
            if receta and texto:
                menu[(dia, "Comida")] = texto
                dias_asignados.add(dia)

    # --- Cenas ---
    cenas_completas = recetas_disponibles("cena", temporada, ingredientes_usuario, "completo")
    cenas_acomp = recetas_disponibles("cena", temporada, ingredientes_usuario, "acompanamiento")
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

        # No repetir proteina principal de la comida del mismo dia
        proteinas = {"pollo","pechuga de pollo","solomillo de pavo","filete de ternera","tacos de ternera",
                     "lomo","filetes de lomo","solomillo de cerdo","chuletas de cerdo","chuletillas de cordero",
                     "costillas de cerdo","costillar de cerdo",
                     "salmon","atun suprema","dorada","lubina","bacalao","gambas","sepia"}
        proteinas_comida = set()
        if comida_hoy:
            for rec in RECETAS:
                if rec.nombre in comida_hoy:
                    proteinas_comida.update(set(rec.ingredientes) & proteinas)
                    break

        def comparte_proteina(receta):
            if not proteinas_comida:
                return False
            return bool(set(receta.ingredientes) & proteinas_comida)

        # Preferir recetas con huevo si no llegamos a 3-4/semana
        preferir_huevo = conteo_huevos < 3
        opciones = [r for r in cenas_pool if r.nombre not in evitar and not comparte_proteina(r)]
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
            if receta.tipo == "acompanamiento" and cenas_segundo:
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


