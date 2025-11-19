import streamlit as st
import pandas as pd
import time

# ==========================
# CONFIGURACIÓN INICIAL
# ==========================
st.set_page_config(layout="wide", page_title="Sorteador CN")

# === Opciones de fondos ===
FONDOS = {
    "Azul Marino (Default)": "GRADIENT",  # Fondo CSS
    "Cocktail Fin de Año": "https://raw.githubusercontent.com/EmilioSantander88/Sorteador-CN-Grupo/main/Fondo%20Sorteo%20Grande.png"
}

# === Fondo y estilo ===
def set_background(image_url):
    if image_url == "GRADIENT":
        css_background = """
        background: linear-gradient(135deg, #0a1a33 0%, #0f2547 50%, #091528 100%) !important;
        """
    else:
        css_background = f"""
        background-image: url("{image_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        """

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DIN&display=swap');

    .stApp {{
        {css_background}
        font-family: 'DIN', sans-serif;
    }}

    header {{visibility: hidden; height: 0px;}}

    h1, h2, h3, h4, h5, h6 {{
        color: white !important;
        text-shadow: 2px 2px 5px black !important;
    }}

    p, span, div {{
        color: white !important;
        text-shadow: 1px 1px 3px black;
    }}

    /* DataFrame */
    .stDataFrame table, .stDataFrame th, .stDataFrame td {{
        color: black !important;
        background-color: white !important;
    }}

    /* Botones principales */
    button[kind="primary"], div.stButton > button {{
        background-color: rgba(0,0,0,0.7) !important;
        color: #f7e9b0 !important;
        border: 2px solid #f7e9b0 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        transition: all 0.3s ease-in-out;
    }}

    button[kind="primary"]:hover, div.stButton > button:hover {{
        background-color: #f7e9b0 !important;
        color: black !important;
        transform: scale(1.03);
    }}

    /* Botón de descarga */
    div[data-testid="stDownloadButton"] > button {{
        background-color: rgba(0,0,0,0.6) !important;
        color: white !important;
        border: 1px solid #ccc !important;
    }}

    /* Premio */
    .premio-visible {{
        font-size: 26px;
        font-weight: bold;
        color: #fff !important;
        text-shadow: 2px 2px 5px black;
    }}

    /* Línea divisoria */
    .custom-line {{
        border-top: 1px solid #ccc;
        width: 100%;
        margin: 40px 0 40px 0;
    }}

    /* Texto ganador */
    .ganador-nombre {{
        font-size: 100px;
        font-weight: bold;
        color: #fff;
        text-shadow: 3px 3px 8px black;
    }}
    .ganador-premio {{
        font-size: 60px;
        font-weight: bold;
        color: #f7e9b0;
        text-shadow: 2px 2px 5px black;
    }}
    .ganador-titulo {{
        font-size: 45px;
        margin-bottom: 20px;
        color: white;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ======================================
# SELECTOR DE FONDO SOLO EN LA PANTALLA INICIAL
# ======================================

mostrar_selector = (
    st.session_state.get("personas") is None or 
    st.session_state.get("premios") is None
)

if mostrar_selector:
    fondo_seleccionado = st.selectbox(
        "Elegí la temática del fondo",
        list(FONDOS.keys())
    )
else:
    # Por coherencia: si ya está cargado, usar el último seleccionado,
    # y si no existe, usar el default.
    fondo_seleccionado = st.session_state.get("fondo_actual", "Azul Marino (Default)")

# Guardar selección
st.session_state["fondo_actual"] = fondo_seleccionado

# Aplicar fondo
set_background(FONDOS[fondo_seleccionado])

# === Logo (CN-GRUPO) ===
logo_url = "https://i.imgur.com/wxJTNMK.png"
st.markdown(
    f"""
    <div style="text-align: left; margin-bottom: 15px;"> 
        <img src="{logo_url}" alt="Logo" style="width: 150px; margin: 20px 0 0 0; display: block;">
    </div>
    """,
    unsafe_allow_html=True,
)

# === Línea Divisoria ===
st.markdown('<div class="custom-line"></div>', unsafe_allow_html=True)

# ==========================
# ESTADOS
# ==========================
for key in ["personas", "premios", "resultados", "ultimo_ganador", "ultimo_premio", "premios_disponibles"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "resultados" else None

# ==========================
# INTERFAZ PRINCIPAL
# ==========================
st.title("Sorteo CN Grupo")

if st.session_state.personas is None or st.session_state.premios is None:
    st.markdown("<h3 style='text-align:center;'>Cargá los archivos Excel y CSV para comenzar</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        personas_file = st.file_uploader("📋 Archivo de Personas (Excel o CSV)", type=["csv", "xlsx", "xls"], key="personas_uploader")
    with col2:
        premios_file = st.file_uploader("🎁 Archivo de Premios (CSV)", type=["csv"], key="premios_uploader")

    if personas_file and premios_file:
        try:
            # Carga personas
            if personas_file.name.endswith((".xls", ".xlsx")):
                personas_df = pd.read_excel(personas_file, sheet_name=0)
            else:
                personas_df = pd.read_csv(personas_file)

            if "Nombre y Apellido" not in personas_df.columns or "N° DNI (Sin puntos, espacios ni comas)" not in personas_df.columns:
                st.error("El archivo de personas debe contener las columnas 'Nombre y Apellido' y 'N° DNI (Sin puntos, espacios ni comas)'.")
            else:
                personas_df = personas_df.dropna(subset=["Nombre y Apellido"])

                if 'ID' in personas_df.columns:
                    personas_df = personas_df.drop(columns=['ID'])
                if 'Nombre' in personas_df.columns:
                    personas_df = personas_df.drop(columns=['Nombre'])

                personas_df = personas_df.drop_duplicates(
                    subset=["N° DNI (Sin puntos, espacios ni comas)"], keep="first"
                ).reset_index(drop=True)

                personas_df = personas_df.rename(columns={
                    "Nombre y Apellido": "Nombre",
                    "N° DNI (Sin puntos, espacios ni comas)": "ID"
                })

                premios_df = pd.read_csv(premios_file)

                st.session_state.personas = personas_df
                st.session_state.premios = premios_df
                st.session_state.premios_disponibles = premios_df["Nombre Premio"].tolist()

                st.success(f"Archivos cargados correctamente. Se registraron {len(personas_df)} personas únicas.")
                st.rerun()

        except Exception as e:
            st.error(f"Error al leer los archivos: {e}")

else:
    col1, col2 = st.columns([0.8, 2.2])

    with col1:
        st.subheader("El siguiente premio es:")
        if st.session_state.premios_disponibles:
            premio_actual = st.session_state.premios_disponibles[0]
            st.markdown(f"<div class='premio-visible'>{premio_actual}</div>", unsafe_allow_html=True)
        else:
            st.warning("No hay premios disponibles.")

        if st.button("Sortear Premio", use_container_width=True):
            if (
                st.session_state.personas is not None
                and not st.session_state.personas.empty
                and st.session_state.premios_disponibles
            ):
                st.session_state.ultimo_ganador = None
                st.session_state.ultimo_premio = None

                placeholder_derecha = col2.empty()

                for i in [3, 2, 1]:
                    placeholder_derecha.markdown(
                        f"""
                        <div style="text-align:center; margin-top:50px;">
                            <h1 style="font-size:120px; color:#f7e9b0; text-shadow:3px 3px 8px black;">{i}</h1>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    time.sleep(1)

                placeholder_derecha.empty()

                ganador = st.session_state.personas.sample(n=1)
                ganador_id = ganador["ID"].values[0]
                ganador_nombre = ganador["Nombre"].values[0]

                premio = st.session_state.premios_disponibles[0]

                st.session_state.ultimo_ganador = ganador_nombre
                st.session_state.ultimo_premio = premio

                st.session_state.resultados.append({"Ganador": ganador_nombre, "Premio": premio})

                st.session_state.personas = st.session_state.personas[
                    st.session_state.personas["ID"] != ganador_id
                ]
                st.session_state.premios_disponibles.pop(0)

                if not st.session_state.premios_disponibles:
                    st.balloons()
                    st.success("¡Sorteo completado!")

                st.rerun()
            else:
                st.warning("Fin del sorteo o no hay participantes disponibles.")

        if st.session_state.resultados:
            st.subheader("Resultados del sorteo")
            resultados_df = pd.DataFrame(st.session_state.resultados)
            st.dataframe(resultados_df, use_container_width=True)
            st.download_button(
                label="Descargar Resultados",
                data=resultados_df.to_csv(index=False),
                file_name="resultados_sorteo.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with col2:
        if st.session_state.ultimo_ganador:
            st.markdown(
                f"""
                <div style="text-align:center; margin-top:30px;">
                    <h2 class="ganador-titulo">El ganador es...</h2>
                    <div class="ganador-nombre">{st.session_state.ultimo_ganador}</div>
                    <div class="ganador-premio">{st.session_state.ultimo_premio}</div>
                    <h3 style="font-size:40px; color:#f7e9b0;">¡Felicitaciones!</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="text-align:center; margin-top:100px;">
                    <h2 style="color:gray;">Esperando el primer sorteo...</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )
