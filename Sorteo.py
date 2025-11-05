import streamlit as st
import pandas as pd

# Configuración inicial de la página
st.set_page_config(layout="wide", page_title="Sorteador de Premios Manual 🎁")

# Función para establecer el fondo y estilos generales (incluyendo la eliminación del margen superior)
def set_background(image_url):
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DIN&display=swap');

    .stApp {{
        background-image: url("{image_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed; /* Mantiene el fondo fijo al hacer scroll */
        font-family: 'DIN', sans-serif;
    }}

    /* Eliminación agresiva del margen y padding superior */
    .main .block-container {{
        /* Asegura que el contenido empiece inmediatamente */
        padding-top: 0rem !important;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 5rem;
    }}
    
    /* Elimina el padding del contenedor principal de la aplicación */
    [data-testid="stAppViewBlockContainer"] {{
        padding-top: 0rem !important;
    }}
    
    /* Oculta la cabecera predeterminada de Streamlit (donde a veces reside el espacio) */
    header {{
        visibility: hidden;
        height: 0px;
    }}

    /* Estilo general del texto */
    html, body, [class*="css"] {{
        font-family: 'DIN', sans-serif;
    }}

    /* Personalización del título */
    .stTitle {{
        color: white;
        text-shadow: 2px 2px 5px black;
        text-align: center;
        margin-top: 1rem; /* Pequeño margen superior para que no se pegue al borde */
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# URL de la imagen de fondo (directo desde Imgur)
image_url = "https://i.imgur.com/KkSUL4Z.jpg"  # Enlace directo a la imagen
set_background(image_url)

# Agregar el logo de la empresa centrado entre líneas
logo_url = "https://i.imgur.com/wxJTNMK.png"  # URL directa de la imagen PNG
st.markdown(
    f"""
    <div style="text-align: center; margin-bottom: 50px;">
        <img src="{logo_url}" alt="Logo" style="width: 150px; margin: 20px auto;">
        <hr style="border: 1px solid #ccc;">
    </div>
    """,
    unsafe_allow_html=True,
)

# Contenido de la aplicación
st.title("SORTEO Fiesta Fin de Año 🎁")

# Subida de archivos
st.sidebar.header("Carga de Datos")
personas_file = st.sidebar.file_uploader("Sube el archivo de personas (CSV)", type=["csv"])
premios_file = st.sidebar.file_uploader("Sube el archivo de premios (CSV)", type=["csv"])

# Estado inicial para las tablas
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
    st.session_state.premios_disponibles = None  # Lista de premios no sorteados

# Cargar los datos subidos si no están cargados aún
if personas_file and premios_file:
    if st.session_state.personas is None:
        st.session_state.personas = pd.read_csv(personas_file)
    if st.session_state.premios is None:
        st.session_state.premios = pd.read_csv(premios_file)

    # Crear una copia de los premios disponibles para el sorteo
    if st.session_state.premios_disponibles is None:
        st.session_state.premios_disponibles = st.session_state.premios["Nombre Premio"].tolist()

    # Dividir la pantalla en dos columnas
    col1, col2 = st.columns([1, 2])  # Ajustar proporción: izquierda más estrecha, derecha más grande

    # Contenido en la columna izquierda: el sorteador
    with col1:
        st.subheader("El siguiente premio es")

        # Mostrar el siguiente premio de forma secuencial
        if st.session_state.premios_disponibles:
            premio_seleccionado = st.session_state.premios_disponibles[0]
            st.write(premio_seleccionado)
        else:
            st.warning("No hay premios disponibles.")

        # Botón para realizar el sorteo
        if st.button("Sortear Premio"):
            if not st.session_state.personas.empty and st.session_state.premios_disponibles:
                # Sorteo: Elegir un ganador aleatorio
                ganador = st.session_state.personas.sample(n=1)
                ganador_id = ganador["ID"].values[0]
                ganador_nombre = ganador["Nombre"].values[0]

                # Guardar el último ganador y premio para mostrar
                st.session_state.ultimo_ganador = ganador_nombre
                st.session_state.ultimo_premio = premio_seleccionado

                # Registrar el resultado
                st.session_state.resultados.append(
                    {"Ganador": ganador_nombre, "Premio": premio_seleccionado}
                )

                # Eliminar al ganador
                st.session_state.personas = st.session_state.personas[st.session_state.personas["ID"] != ganador_id]

                # Eliminar el premio seleccionado de la lista de premios disponibles
                st.session_state.premios_disponibles.pop(0)

                # Verificar si quedan premios
                if not st.session_state.premios_disponibles:
                    st.warning("No hay más premios disponibles.")
                else:
                    st.success(f"🎉 {ganador_nombre} ganó el premio: {premio_seleccionado}")

            else:
                st.warning("No hay más participantes o premios disponibles.")

        # Mostrar la tabla de resultados
        if st.session_state.resultados:
            st.subheader("Resultados del Sorteo")
            resultados_df = pd.DataFrame(st.session_state.resultados)
            st.dataframe(resultados_df)

            # Botón para descargar los resultados
            st.download_button(
                label="Descargar Resultados",
                data=resultados_df.to_csv(index=False),
                file_name="resultados_sorteo.csv",
                mime="text/csv",
            )

# Contenido en la columna derecha: mostrar al ganador y el premio
    with col2:
        st.markdown(
            f"""
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