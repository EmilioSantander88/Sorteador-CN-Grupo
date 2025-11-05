import streamlit as st
import pandas as pd

# ==========================
# CONFIGURACIÓN INICIAL
# ==========================
st.set_page_config(layout="wide", page_title="Sorteador CN")

# === Fondo y estilo ===
def set_background(image_url):
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DIN&display=swap');

    .stApp {{
        background-image: url("{image_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
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
        border: 2px solid #f7e9b0 !important;
        transform: scale(1.03);
    }}

    /* Botón de descarga */
    div[data-testid="stDownloadButton"] > button {{
        background-color: rgba(0,0,0,0.6) !important;
        color: white !important;
        border: 1px solid #ccc !important;
    }}

    /* Subtítulos de carga */
    div[data-testid="stFileUploader"] {{
        background-color: rgba(0, 0, 0, 0.6);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }}

    /* Premio */
    .premio-visible {{
        font-size: 24px;
        font-weight: bold;
        color: #fff !important;
        text-shadow: 2px 2px 5px black;
    }}

    /* Línea decorativa bajo el logo */
    .custom-line {{
        border-top: 1px solid #ccc;
        width: 100%;
        margin: 10px 0 40px 0;
    }}

    /* Efecto de brillo */
    @keyframes shine {{
        0% {{ text-shadow: 0 0 10px #fff, 0 0 20px #ffd700, 0 0 30px #ff8c00; }}
        50% {{ text-shadow: 0 0 20px #fff, 0 0 40px #ffd700, 0 0 60px #ff8c00; }}
        100% {{ text-shadow: 0 0 10px #fff, 0 0 20px #ffd700, 0 0 30px #ff8c00; }}
    }}
    .shine {{
        animation: shine 1.5s infinite alternate;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# === Fondo ===
set_background("https://i.imgur.com/KkSUL4Z.jpg")

# === Logo ===
logo_url = "https://i.imgur.com/wxJTNMK.png"
st.markdown(
    f"""
    <div style="text-align: center; margin-bottom: 10px;">
        <img src="{logo_url}" alt="Logo" style="width: 150px; margin: 20px auto;">
        <div class="custom-line"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================
# ESTADOS
# ==========================
if "personas" not in st.session_state:
    st.session_state.personas = None
if "premios" not in st.session_state:
    st.session_state.premios = None
if "resultados" not in st.session_state:
    st.session_state.resultados = []
if "ultimo_ganador" not in st.session_state:
    st.session_state.ultimo_ganador = None
if "ultimo_premio" not in st.session_state:
    st.session_state.ultimo_premio = None
if "premios_disponibles" not in st.session_state:
    st.session_state.premios_disponibles = None

# ==========================
# INTERFAZ PRINCIPAL
# ==========================
st.title("🎁 Sorteo Fiesta Fin de Año CN")

if st.session_state.personas is None or st.session_state.premios is None:
    st.markdown("<h3 style='text-align:center;'>Cargá los archivos CSV para comenzar</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        personas_file = st.file_uploader("📋 Archivo de Personas (CSV)", type=["csv"], key="personas_uploader")
    with col2:
        premios_file = st.file_uploader("🎁 Archivo de Premios (CSV)", type=["csv"], key="premios_uploader")

    if personas_file and premios_file:
        try:
            st.session_state.personas = pd.read_csv(personas_file)
            st.session_state.premios = pd.read_csv(premios_file)
            st.session_state.premios_disponibles = st.session_state.premios["Nombre Premio"].tolist()
            st.success("Archivos cargados correctamente. ¡Listo para comenzar el sorteo!")
            st.rerun()
        except Exception as e:
            st.error(f"Error al leer los archivos: {e}")

else:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("El siguiente premio es:")
        if st.session_state.premios_disponibles:
            premio_actual = st.session_state.premios_disponibles[0]
            st.markdown(f"<div class='premio-visible'>{premio_actual}</div>", unsafe_allow_html=True)
        else:
            st.warning("No hay premios disponibles.")

        if st.button("Sortear Premio", use_container_width=True):
            if not st.session_state.personas.empty and st.session_state.premios_disponibles:
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
                    st.success("🎉 ¡Sorteo completado!")
                st.rerun()
            else:
                st.warning("No hay más participantes o premios.")

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
                <div style="text-align:center; margin-top:50px;">
                    <h2>EL GANADOR ES...</h2>
                    <h1 class="shine" style="font-size:80px;">{st.session_state.ultimo_ganador}</h1>
                    <h2 style="font-size:50px;">{st.session_state.ultimo_premio}</h2>
                    <h3 style="font-size:40px; color:#f7e9b0;">¡FELICITACIONES! 🎉</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="text-align:center; margin-top:80px;">
                    <h2 style="color:gray;">Esperando el primer sorteo...</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )
