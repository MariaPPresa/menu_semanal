import streamlit as st
import random
from recetas import RECETAS, INGREDIENTES, COLORES_CATEGORIA, DESAYUNOS, FRUTAS, Receta
from logica import generar_menu, temporada_actual, color_para_nombre, recetas_disponibles, nombre_con_segundo, DIAS, MOMENTOS

st.set_page_config(page_title="Menu Semanal", page_icon="🥗", layout="wide")

if "menu" not in st.session_state:
    st.session_state.menu = {}

# Categorias de ingredientes para mostrar ordenados
CATS_INGREDIENTES = {
    "Carnes": [i for i in INGREDIENTES if any(x in i for x in ["pollo","pavo","ternera","cerdo","lomo","jamon","lacon","tocino","chorizo","morcilla","picadillo","picada","salchicha","chistorra","butifarra","chuleta","cordero","costill"])],
    "Pescados": [i for i in INGREDIENTES if any(x in i for x in ["salmon","atun","dorada","lubina","bacalao","gambas","sepia","mejillones","zamburina","sardina","gula"])],
    "Cereales/Legumbres": [i for i in INGREDIENTES if any(x in i for x in ["pasta","arroz","fideua","lenteja","garbanzo","fabe","guisante"])],
    "Verduras": [i for i in INGREDIENTES if any(x in i for x in ["tomate","lechuga","cebolla","ajo","pimiento","zanahoria","pepinillo","patata","calabac","espinaca","frejol","champi","berenje","calabaza","maiz","aguacate","boniato","seta","puerro","esparrago"])],
    "Otros": [i for i in INGREDIENTES if any(x in i for x in ["huevo","queso","mozza","leche","nata","curry","pan","limon","aceituna","vino","sal gorda","salsa","tomate frito","caldo","harina","levadura","nugget","croqueta","rollito"])],
    "Frutas": [i for i in INGREDIENTES if any(x in i for x in ["manzana","platano","naranja","fresa","kiwi","melocoton","frutos","uva","cereal","tostada"])],
}

# --- Layout: menu a la izquierda, compra a la derecha ---
st.title(f"🥗 Menu Semanal - {temporada_actual().capitalize()}")

# --- Generar ---
if st.button("🍽 Generar Menu", type="primary"):
    excl = set()
    for dia in DIAS:
        for momento in MOMENTOS:
            if st.session_state.get(f"excl_{dia}_{momento}", False):
                excl.add((dia, momento))
    st.session_state.menu = generar_menu(st.session_state.get("nevera", set()), excl, {})

col_menu, col_compra = st.columns([4, 1])

with col_menu:
    # Leyenda
    leg = " ".join(f"<span style='background-color:{c};padding:3px 8px;border-radius:4px;font-size:12px;color:#000'>{k}</span>" for k,c in COLORES_CATEGORIA.items())
    st.markdown(leg, unsafe_allow_html=True)
    st.markdown("")

    # Cabecera
    header = st.columns([1]+[2]*7)
    header[0].write("")
    for j,dia in enumerate(DIAS):
        header[j+1].markdown(f"**{dia}**")

    # Filas con X para excluir y boton regenerar
    for momento in MOMENTOS:
        row = st.columns([1]+[2]*7)
        row[0].markdown(f"**{momento}**")
        for j,dia in enumerate(DIAS):
            with row[j+1]:
                excl_key = f"excl_{dia}_{momento}"
                excluded = st.checkbox("✖", key=excl_key, label_visibility="collapsed")
                clave = (dia, momento)
                menu = st.session_state.menu
                if excluded:
                    st.markdown("<div style='background:#D5D8DC;padding:10px;border-radius:6px;text-align:center;min-height:55px;font-size:13px;color:#000'>-</div>", unsafe_allow_html=True)
                elif clave in menu and menu[clave]:
                    valor = menu[clave]
                    color = color_para_nombre(valor) if momento != "Desayuno" else COLORES_CATEGORIA.get("desayuno","#D7BDE2")
                    st.markdown(f"<div style='background:{color};padding:10px;border-radius:6px;text-align:center;font-size:13px;color:#000;min-height:55px'>{valor}</div>", unsafe_allow_html=True)
                    # Boton regenerar celda
                    if st.button("🔄", key=f"regen_{dia}_{momento}"):
                        temporada = temporada_actual()
                        if momento == "Desayuno":
                            if dia == "Sábado":
                                nuevo = "Desayuno libre 🎉"
                            else:
                                nuevo = f"{random.choice(DESAYUNOS)} + {random.choice(FRUTAS)}"
                        else:
                            hora = "comida" if momento == "Comida" else "cena"
                            pool = recetas_disponibles(hora, temporada, st.session_state.get("nevera", set()))
                            if pool:
                                r = random.choice(pool)
                                if r.tipo == "acompanamiento":
                                    segs = recetas_disponibles(hora, temporada, st.session_state.get("nevera", set()), "segundo")
                                    nuevo = nombre_con_segundo(r, random.choice(segs)) if segs else r.nombre
                                else:
                                    nuevo = r.nombre
                            else:
                                nuevo = "-"
                        st.session_state.menu[clave] = nuevo
                        st.rerun()
                else:
                    st.markdown("<div style='background:#ECF0F1;padding:10px;border-radius:6px;text-align:center;min-height:55px;font-size:13px;color:#000'></div>", unsafe_allow_html=True)

with col_compra:
    st.subheader("🛒 Compra")
    if st.session_state.menu:
        todos_ing = set()
        for valor in st.session_state.menu.values():
            if valor:
                nombres = valor.split(" + ") if " + " in valor else [valor]
                for nombre in nombres:
                    for r in RECETAS:
                        if r.nombre == nombre:
                            todos_ing.update(r.ingredientes)
                            break
        nevera = st.session_state.get("nevera", set())
        faltan = sorted(todos_ing - nevera)
        if faltan:
            for ing in faltan:
                st.write(f"- {ing}")
        else:
            st.success("Todo listo!")
    else:
        st.caption("Genera un menu primero")

# --- Nevera: ingredientes por categoria con checkboxes ---
st.markdown("---")
st.subheader("🧊 Nevera / Congelador")
st.caption("Marca los ingredientes que tienes")

nevera = st.session_state.get("nevera", set())
nueva_nevera = set()

for cat, ings in CATS_INGREDIENTES.items():
    if not ings:
        continue
    st.markdown(f"**{cat}**")
    cols = st.columns(5)
    for i, ing in enumerate(ings):
        with cols[i % 5]:
            if st.checkbox(ing, value=ing in nevera, key=f"nev_{ing}"):
                nueva_nevera.add(ing)

st.session_state.nevera = nueva_nevera
