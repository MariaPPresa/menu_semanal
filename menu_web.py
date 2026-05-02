import streamlit as st
import random
from recetas import RECETAS, INGREDIENTES, COLORES_CATEGORIA, DESAYUNOS, FRUTAS, Receta
from logica import generar_menu, temporada_actual, color_para_nombre, recetas_disponibles, nombre_con_segundo, fruta_semana, DIAS, MOMENTOS

st.set_page_config(page_title="Menu Semanal", page_icon="🥗", layout="wide")

if "menu" not in st.session_state:
    st.session_state.menu = {}

# --- Layout: menu a la izquierda, compra a la derecha ---
st.title(f"🥗 Menu Semanal - {temporada_actual().capitalize()}")

# --- Generar ---
if "fruta" not in st.session_state:
    st.session_state.fruta = fruta_semana()
st.markdown(f"**\U0001f34e Fruta de la semana: {st.session_state.fruta}**")

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
                                nuevo = random.choice(DESAYUNOS)
                        else:
                            hora = "comida" if momento == "Comida" else "cena"
                            nevera = st.session_state.get("nevera", set())
                            pool = [r for r in recetas_disponibles(hora, temporada, nevera) if r.tipo != "segundo"]
                            if pool:
                                r = random.choice(pool)
                                if r.tipo == "acompanamiento":
                                    segs = recetas_disponibles(hora, temporada, nevera, "segundo")
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
        st.caption("Tacha lo que ya tengas")
        tachados = st.session_state.get("tachados", set())
        for ing in sorted(todos_ing):
            if st.checkbox(ing, value=ing in tachados, key=f"compra_{ing}"):
                tachados.add(ing)
            else:
                tachados.discard(ing)
        st.session_state.tachados = tachados
        st.session_state.nevera = tachados
        pendientes = sorted(todos_ing - tachados)
        if not pendientes:
            st.success("Todo listo!")
            st.caption(f"{len(pendientes)} ingredientes pendientes")
            lista_txt = chr(10).join(pendientes)
            st.code(lista_txt, language=None)
            st.caption(f"{pendientes} ingredientes pendientes")
    else:
        st.caption("Genera un menu primero")
