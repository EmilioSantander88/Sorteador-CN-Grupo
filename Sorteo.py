import streamlit as st
import pandas as pd
import time

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
        font-size: 26px;
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

    /* Texto grande lado derecho */
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

    /* Cuenta regresiva (centrada y grande) */
    .countdown {{
        text-align: center;
        margin-top: 30px;
    }}
    .countdown h1 {{
        font-size: 120px;
        color: #f7e9b0;
        text-shadow: 3px 3px 8px black;
        margin: 0;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# === Fondo ===
set_background("https://i.imgur.com/dPJYAld.jpeg")

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
# ESTADOS (asegurar claves)
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
st.title("Sorteo Cocktail de Fin de Año")

# si no están los datos, mostrar upload
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
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error al leer los archivos: {e}")

else:
    # columnas ajustadas: izquierda más angosta, derecha más ancha
    col1, col2 = st.columns([0.8, 2.2])

    # Placeholder en la columna derecha para la cuenta y luego el ganador
    placeholder_der = col2.empty()

    with col1:
        st.subheader("El siguiente premio es:")
        if st.session_state.premios_disponibles:
            premio_actual = st.session_state.premios_disponibles[0]
            st.markdown(f"<div class='premio-visible'>{premio_actual}</div>", unsafe_allow_html=True)
        else:
            st.warning("No hay premios disponibles.")

        # el botón está DENTRO de col1 — así no ocupa todo el ancho de la página
        if st.button("Sortear Premio", use_container_width=True):
            # seguridad
            if st.session_state.personas is None or st.session_state.premios_disponibles is None:
                st.warning("Cargá primero los archivos.")
            elif st.session_state.personas.empty or not st.session_state.premios_disponibles:
                st.warning("Fin del sorteo")
            else:
                # animación: 3,2,1 en la columna derecha
                for i in [3, 2, 1]:
                    placeholder_der.markdown(
                        f"""
                        <div class="countdown">
                            <h1>{i}</h1>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    time.sleep(1)

                # pequeño destello final (puede verse rápido)
                placeholder_der.markdown(
                    """
                    <div style="text-align:center; margin-top:10px;">
                        <h1 style="font-size:80px; color:white; text-shadow:0 0 30px #fff;">¡Ya!</h1>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                time.sleep(0.3)

                # seleccionar ganador y actualizar estado ANTES de rerun
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

                # rerun para mostrar el ganador usando la plantilla normal de la derecha
                st.experimental_rerun()

        # resultados y descarga (siguen en la columna izquierda)
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

    # Columna derecha: aquí se muestra el ganador (si existe)
    with col2:
        if st.session_state.ultimo_ganador:
            st.markdown(
                f"""
                <div style="text-align:center; margin-top:30px;">
                    <h2 class="ganador-titulo">El ganador es...</h2>
                    <div class="ganador-nombre shine">{st.session_state.ultimo_ganador}</div>
                    <div class="ganador-premio">{st.session_state.ultimo_premio}</div>
                    <h3 style="font-size:40px; color:#f7e9b0;">¡Felicitaciones!</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # si no hay ganador todavía, mostramos el placeholder vacío (ya creado)
            placeholder_der.markdown(
                """
                <div style="text-align:center; margin-top:100px;">
                    <h2 style="color:gray;">Esperando el primer sorteo...</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )
