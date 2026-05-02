"""
Generador de Menú Semanal Balanceado
- Raciones: comidas dan para 2 días (excepto pescado)
- No repite receta en días consecutivos
- Temporada según mes actual
- Acompañamientos se emparejan con un segundo
- Huevos 3-4/semana controlado por ingrediente
- Exclusiones clickando en el calendario
- Celdas editables / click derecho regenera celda
"""

import tkinter as tk
from tkinter import ttk
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


# --- INTERFAZ GRÁFICA ---

class VentanaNevera:
    def __init__(self, parent, ingredientes_seleccionados):
        self.win = tk.Toplevel(parent)
        self.win.title("🧊 Mi Nevera / Congelador")
        self.win.geometry("700x500")
        self.win.configure(bg="#E8F8F5")
        self.resultado = ingredientes_seleccionados

        tk.Label(self.win, text="Marca los ingredientes que tienes:",
                 font=("Segoe UI", 11, "bold"), bg="#E8F8F5").pack(pady=8)

        frame = ttk.Frame(self.win)
        frame.pack(fill="both", expand=True, padx=10)

        self.vars = {}
        cols = 4
        for i, ing in enumerate(INGREDIENTES):
            var = tk.BooleanVar(value=ing in self.resultado)
            cb = ttk.Checkbutton(frame, text=ing, variable=var)
            cb.grid(row=i // cols, column=i % cols, sticky="w", padx=6, pady=2)
            self.vars[ing] = var

        btn_frame = ttk.Frame(self.win)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="✅ Guardar", bg="#27AE60", fg="white",
                  font=("Segoe UI", 10), relief="flat", command=self._guardar).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Limpiar", bg="#95A5A6", fg="white",
                  font=("Segoe UI", 10), relief="flat", command=self._limpiar).pack(side="left", padx=5)

    def _guardar(self):
        self.resultado.clear()
        self.resultado.update(ing for ing, var in self.vars.items() if var.get())
        self.win.destroy()

    def _limpiar(self):
        for var in self.vars.values():
            var.set(False)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("🥗 Menú Semanal Balanceado")
        self.root.geometry("1250x680")
        self.root.configure(bg="#FDFEFE")

        self.ingredientes_seleccionados = set()
        self.exclusiones = set()
        self.celdas = {}
        self.menu_actual = {}

        self._crear_interfaz()

    def _crear_interfaz(self):
        # --- Barra superior ---
        top = tk.Frame(self.root, bg="#2C3E50", height=45)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text=f"🥗 Menú Semanal — {temporada_actual().capitalize()}",
                 bg="#2C3E50", fg="white", font=("Segoe UI", 13, "bold")).pack(side="left", padx=15, pady=8)
        tk.Button(top, text="🧊 Nevera", bg="#3498DB", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  command=self._abrir_nevera).pack(side="right", padx=15, pady=8)

        # --- Botones ---
        btn_frame = tk.Frame(self.root, bg="#FDFEFE")
        btn_frame.pack(fill="x", padx=10, pady=8)
        tk.Button(btn_frame, text="🍽️ Generar Menú", bg="#27AE60", fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", padx=15,
                  command=self._generar).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🔄 Regenerar", bg="#8E44AD", fg="white",
                  font=("Segoe UI", 10), relief="flat", padx=10,
                  command=self._generar).pack(side="left", padx=5)
        tk.Label(btn_frame, text="(Click derecho sobre una celda = cambiar receta)",
                 bg="#FDFEFE", fg="#7F8C8D", font=("Segoe UI", 8, "italic")).pack(side="left", padx=10)

        # Leyenda
        leyenda_frame = tk.Frame(btn_frame, bg="#FDFEFE")
        leyenda_frame.pack(side="right")
        leyenda = [("Pasta", "pasta_arroz"), ("Legum.", "legumbres"), ("P.Azul", "pescado_azul"),
                   ("P.Blanco", "pescado_blanco"), ("C.Blanca", "carne_blanca"),
                   ("C.Roja", "carne_roja"), ("Ensalada", "ensalada"),
                   ("Verdura", "verdura"), ("Desay.", "desayuno")]
        for nombre, cat in leyenda:
            tk.Label(leyenda_frame, text=f" {nombre} ", bg=COLORES_CATEGORIA[cat],
                     font=("Segoe UI", 7)).pack(side="left", padx=1)

        # --- Calendario/Grid ---
        self.frame_cal = tk.Frame(self.root, bg="#FDFEFE")
        self.frame_cal.pack(fill="both", expand=True, padx=10, pady=5)
        self._crear_calendario()

        # --- Lista de la compra ---
        lf_compra = tk.LabelFrame(self.root, text="🛒 Lista de la compra", font=("Segoe UI", 9))
        lf_compra.pack(fill="x", padx=10, pady=5)
        self.txt_compra = tk.Text(lf_compra, height=3, wrap="word", font=("Segoe UI", 9))
        self.txt_compra.pack(fill="x", padx=5, pady=3)

    def _crear_calendario(self):
        for w in self.frame_cal.winfo_children():
            w.destroy()

        self.celdas = {}
        self.excl_vars = {}
        self.celdas_fijadas = set()

        tk.Label(self.frame_cal, text="", bg="#FDFEFE", width=9).grid(row=0, column=0)
        for j, dia in enumerate(DIAS):
            tk.Label(self.frame_cal, text=dia, bg="#2C3E50", fg="white",
                     font=("Segoe UI", 9, "bold"), width=16, pady=4).grid(row=0, column=j+1, padx=1, pady=1)

        for i, momento in enumerate(MOMENTOS):
            tk.Label(self.frame_cal, text=momento, bg="#5D6D7E", fg="white",
                     font=("Segoe UI", 9, "bold"), width=9, pady=6).grid(row=i+1, column=0, padx=1, pady=1)
            for j, dia in enumerate(DIAS):
                cell_frame = tk.Frame(self.frame_cal, bg="#ECF0F1", relief="groove", bd=1)
                cell_frame.grid(row=i+1, column=j+1, padx=1, pady=1, sticky="nsew")

                var = tk.BooleanVar()
                cb = tk.Checkbutton(cell_frame, text="✖", variable=var, bg="#ECF0F1",
                                    fg="#E74C3C", font=("Segoe UI", 7), indicatoron=False,
                                    selectcolor="#FADBD8", relief="flat")
                cb.pack(anchor="ne")
                self.excl_vars[(dia, momento)] = var

                entry = tk.Entry(cell_frame, font=("Segoe UI", 8), width=18,
                                 justify="center", relief="flat", bg="#ECF0F1")
                entry.pack(fill="both", expand=True, padx=2, pady=2)
                self.celdas[(dia, momento)] = entry

                clave = (dia, momento)
                entry.bind("<Button-3>", lambda e, k=clave: self._regenerar_celda(k))
                entry.bind("<Key>", lambda e, k=clave: self.celdas_fijadas.add(k))

        for j in range(8):
            self.frame_cal.columnconfigure(j, weight=1)
        for i in range(4):
            self.frame_cal.rowconfigure(i, weight=1)

    def _abrir_nevera(self):
        VentanaNevera(self.root, self.ingredientes_seleccionados)

    def _regenerar_celda(self, clave):
        dia, momento = clave
        self.celdas_fijadas.discard(clave)
        temporada = temporada_actual()

        if momento == "Desayuno":
            if dia == "Sábado":
                nuevo = "Desayuno libre 🎉"
            else:
                nuevo = f"{random.choice(DESAYUNOS)} + {random.choice(FRUTAS)}"
        else:
            hora = "comida" if momento == "Comida" else "cena"
            pool = recetas_disponibles(hora, temporada, self.ingredientes_seleccionados)
            if pool:
                receta = random.choice(pool)
                if receta.tipo == "acompañamiento":
                    segundos = recetas_disponibles(hora, temporada, self.ingredientes_seleccionados, "segundo")
                    if segundos:
                        nuevo = nombre_con_segundo(receta, random.choice(segundos))
                    else:
                        nuevo = receta.nombre
                else:
                    nuevo = receta.nombre
            else:
                nuevo = "—"

        entry = self.celdas[clave]
        entry.delete(0, "end")
        entry.insert(0, nuevo)
        if momento == "Desayuno":
            entry.configure(bg=COLORES_CATEGORIA["desayuno"])
        else:
            entry.configure(bg=color_para_nombre(nuevo))
        self.menu_actual[clave] = nuevo
        self._actualizar_compra()

    def _generar(self):
        self.exclusiones = {k for k, v in self.excl_vars.items() if v.get()}

        celdas_fijas = {}
        for clave in self.celdas_fijadas:
            entry = self.celdas[clave]
            texto = entry.get().strip()
            if texto and clave not in self.exclusiones:
                celdas_fijas[clave] = texto

        self.menu_actual = generar_menu(self.ingredientes_seleccionados, self.exclusiones, celdas_fijas)

        for (dia, momento), entry in self.celdas.items():
            clave = (dia, momento)
            valor = self.menu_actual.get(clave)

            if clave in celdas_fijas:
                color = color_para_nombre(celdas_fijas[clave])
                entry.configure(bg=color if color != "#FFFFFF" else "#D5F5E3")
                continue

            entry.delete(0, "end")
            if valor is None:
                entry.configure(bg="#D5D8DC")
                entry.insert(0, "—")
            else:
                entry.insert(0, valor)
                if momento == "Desayuno":
                    entry.configure(bg=COLORES_CATEGORIA["desayuno"])
                else:
                    entry.configure(bg=color_para_nombre(valor))

        self._actualizar_compra()

    def _actualizar_compra(self):
        todos_ing = set()
        for valor in self.menu_actual.values():
            if valor:
                # Soportar nombres compuestos
                nombres = valor.split(" + ") if " + " in valor else [valor]
                for nombre in nombres:
                    for r in RECETAS:
                        if r.nombre == nombre:
                            todos_ing.update(r.ingredientes)
                            break
        faltan = sorted(todos_ing - self.ingredientes_seleccionados)
        self.txt_compra.delete("1.0", "end")
        self.txt_compra.insert("1.0", ", ".join(faltan) if faltan else "¡Tienes todo lo necesario!")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
