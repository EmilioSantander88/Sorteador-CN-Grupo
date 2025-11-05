import streamlit as st
import pandas as pd

# Configuración inicial
st.set_page_config(layout="wide", page_title="Sorteador CN")

# === Función para estilos y fondo ===
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

    /* Contenedor */
    .main .block-container {{
        padding-top: 0rem !important;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 5rem;
    }}
    [data-testid="stAppViewBlockContainer"] {{
        padding-top: 0rem !important;
    }}
    header {{
        visibility: hidden;
        height: 0px;
    }}

    /* Textos */
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

    /* --- Sidebar Toggle visible --- */
    [data-testid="stSidebarToggleButton"] {{
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 99999 !important;
        background-color: rgba(0,0,0,0.7) !important;
        border: 1px solid white !important;
        border-radius: 6px !important;
        color: white !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    [data-testid="stSidebarToggleButton"]:hover {{
        background-color: rgba(255,255,255,0.8) !important;
        color: black !important;
    }}

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.95) !important;
        color: white !important;
        z-index: 9999 !important;
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}

    /* Botón Sortear Premio con brillo */
    div.stButton > button:first-child {{
        background: linear-gradient(90deg, #444, #777, #444);
        color: white !important;
        font-weight: bold;
        border: 2px solid #fff;
        border-radius: 10px;
        padding: 0.6em 1.5em;
        font-size: 1.1em;
        cursor: pointer;
        box-shadow: 0 0 10px rgba(255,255,255,0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    div.stButton > button:first-child::before {{
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.6), transparent);
        transition: all 0.6s;
    }}
    div.stButton > button:first-child:hover::before {{
        left: 100%;
    }}
    div.stButton > button:first-child:hover {{
        background: linear-gradient(90deg, #666, #999, #666);
        box-shadow: 0 0 20px rgba(255,255,255,0.5);
    }}

    /* Texto de premio visible */
    .premio-visible {{
        font-size: 22px;
        font-weight: bold;
        color: #fff !important;
        text-shadow: 2px 2px 5px black;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# === Fondo ===
image_url = "https://i.imgur.com/KkSUL4Z.jpg"
set_background(image_url)

# === Logo ===
logo_url = "https://i.imgur.com/wxJTNMK.png"
st.markdown(
    f"""
    <div style="text-align: center; margin-bottom: 50px;">
        <img src="{logo_url}" alt="Logo" style="width: 150px; margin: 20px auto;">
        <hr style="border: 1px solid #ccc;">
    </div>
    """,
    unsafe_allow_html=True,
)

# === Título ===
st.title("SORTEO Fiesta Fin de Año 🎁")

# === Sidebar ===
st.sidebar.header("Carga de Datos")
personas_file = st.sidebar.file_uploader("Sube el archivo de personas (CSV)", type=["csv"])
premios_file = st.sidebar.file_uploader("Sube el archivo de premios (CSV)", type=["csv"])

# === Estados ===
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


# === Lógica principal ===
if personas_file and premios_file:
    try:
        if st.session_state.personas is None:
            st.session_state.personas = pd.read_csv(personas_file)
        if st.session_state.premios is None:
            st.session_state.premios = pd.read_csv(premios_file)

        if st.session_state.premios_disponibles is None:
            st.session_state.premios_disponibles = st.session_state.premios["Nombre Premio"].tolist()

        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("El siguiente premio es")

            if st.session_state.premios_disponibles:
                premio_seleccionado = st.session_state.premios_disponibles[0]
                st.markdown(f"<div class='premio-visible'>{premio_seleccionado}</div>", unsafe_allow_html=True)
            else:
                st.warning("No hay premios disponibles.")

            if st.button("Sortear Premio"):
                if not st.session_state.personas.empty and st.session_state.premios_disponibles:
                    ganador = st.session_state.personas.sample(n=1)
                    ganador_id = ganador["ID"].values[0]
                    ganador_nombre = ganador["Nombre"].values[0]
                    st.session_state.ultimo_ganador = ganador_nombre
                    st.session_state.ultimo_premio = premio_seleccionado

                    st.session_state.resultados.append(
                        {"Ganador": ganador_nombre, "Premio": premio_seleccionado}
                    )

                    st.session_state.personas = st.session_state.personas[
                        st.session_state.personas["ID"] != ganador_id
                    ]

                    st.session_state.premios_disponibles.pop(0)

                    if not st.session_state.premios_disponibles:
                        st.balloons()
                        st.success(f"🎉 {ganador_nombre} ganó el premio: {premio_seleccionado}. ¡Sorteo finalizado!")
                    else:
                        st.success(f"🎉 {ganador_nombre} ganó el premio: {premio_seleccionado}")
                else:
                    st.warning("No hay más participantes o premios disponibles.")

            if st.session_state.resultados:
                st.subheader("Resultados del Sorteo")
                resultados_df = pd.DataFrame(st.session_state.resultados)
                st.dataframe(resultados_df, use_container_width=True)
                st.download_button(
                    label="Descargar Resultados",
                    data=resultados_df.to_csv(index=False),
                    file_name="resultados_sorteo.csv",
                    mime="text/csv",
                )

        with col2:
            st.markdown(
                """
                <div style="text-align: center; margin-top: 50px; color: white; text-shadow: 2px 2px 5px black;">
                    <h2 style="font-size: 50px;">EL GANADOR ES...</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.session_state.ultimo_ganador and st.session_state.ultimo_premio:
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-top: 20px; color: white; text-shadow: 2px 2px 5px black;">
                        <h1 style="font-size: 70px;">{st.session_state.ultimo_ganador}</h1>
                        <h2 style="font-size: 50px;">{st.session_state.ultimo_premio}</h2>
                        <h3 style="font-size: 50px; margin-top: 20px; color: #ddd4c2;">¡Muchas Felicidades!</h3>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div style="text-align: center; margin-top: 50px; color: gray;">
                        <h1 style="font-size: 40px;">Aún no hay ganadores</h1>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    except Exception as e:
        st.error(f"Error al cargar los archivos CSV. Revisa las columnas ('ID', 'Nombre', 'Nombre Premio'). Detalle: {e}")
        st.session_state.personas = None
        st.session_state.premios = None
