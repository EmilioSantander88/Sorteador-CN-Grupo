import streamlit as st
import pandas as pd

# Configuración inicial de la página
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

    /* Contenedor principal */
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

    /* Colores de texto */
    h1, h2, h3, h4, h5, h6 {{
        color: white !important;
        text-shadow: 2px 2px 5px black !important;
    }}

    p, span, div {{
        color: white !important;
        text-shadow: 1px 1px 3px black;
    }}

    /* DataFrame: texto negro sobre fondo blanco */
    .stDataFrame table, .stDataFrame th, .stDataFrame td {{
        color: black !important;
        background-color: white !important;
    }}

    /* --- Sidebar Fix: botón hamburguesa --- */
    [data-testid="stSidebarToggleButton"] {{
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 99999 !important;
        background-color: rgba(0,0,0,0.6) !important;
        border-radius: 6px !important;
        color: white !important;
    }}

    /* --- Sidebar Fix --- */
    section[data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.95) !important;
        color: white !important;
        z-index: 9999 !important;
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    [data-testid="stSidebarUserContent"] {{
        position: relative;
        z-index: 10000;
    }}

    /* Uploader claro */
    .stFileUploader label, .stFileUploader div {{
        color: white !important;
    }}

    /* Premio en blanco y visible */
    .premio-visible {{
        font-size: 22px;
        font-weight: bold;
        color: #fff !important;
        text-shadow: 2px 2px 5px black;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# === Fondo e imagen del logo ===
image_url = "https://i.imgur.com/KkSUL4Z.jpg"
set_background(image_url)

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

# === Título principal ===
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


# === Lógica de carga ===
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
