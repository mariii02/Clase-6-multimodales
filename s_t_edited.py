import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# Configuración de la aplicación
st.set_page_config(page_title="Traductor de Voz", layout="wide")

# Título y subtítulo
st.title("🌐 Traductor de Voz")
st.subheader("¡Habla y traduce en tiempo real!")

# Cargar y mostrar la imagen
image = Image.open('OIG7.jpg')
st.image(image, width=300)

# Sidebar para instrucciones
with st.sidebar:
    st.subheader("Instrucciones")
    st.write("1. Presiona el botón para iniciar el reconocimiento de voz.")
    st.write("2. Habla lo que deseas traducir.")
    st.write("3. Selecciona el idioma de entrada y salida.")
    st.write("4. Presiona 'Convertir' para obtener la traducción en audio.")

# Botón para iniciar reconocimiento de voz
st.write("🔊 Toca el botón para hablar y traducir:")
stt_button = Button(label="Escuchar  🎤", width=400, height=80)

# JavaScript para reconocimiento de voz
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

# Manejo del resultado del reconocimiento de voz
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# Si hay resultado, procesar la traducción
if result and "GET_TEXT" in result:
    spoken_text = result.get("GET_TEXT")
    st.write("Texto reconocido:", spoken_text)

    # Crear carpeta temporal si no existe
    os.makedirs("temp", exist_ok=True)

    st.title("🔊 Texto a Audio")
    translator = Translator()
    
    # Selección de idioma de entrada
    input_lang = st.selectbox("Selecciona el idioma de entrada:", 
                               ("Inglés", "Español", "Latín", "Coreano", "Gaélico escocés", "Japonés"))
    
    # Mapeo de idiomas
    lang_map = {
        "Inglés": "en",
        "Español": "es",
        "Latín": "la",
        "Coreano": "ko",
        "Gaélico escocés": "gd",
        "Japonés": "ja"
    }
    input_language = lang_map[input_lang]

    # Selección de idioma de salida
    output_lang = st.selectbox("Selecciona el idioma de salida:", 
                                ("Inglés", "Español", "Latín", "Coreano", "Gaélico escocés", "Japonés"))
    output_language = lang_map[output_lang]
    
    # Selección de acento
    english_accent = st.selectbox("Selecciona el acento:", 
                                   ("Defecto", "Español", "Reino Unido", "Estados Unidos", "Canadá", "Australia", "Irlanda", "Sudáfrica"))
    
    # Mapeo de acentos
    accent_map = {
        "Defecto": "com",
        "Español": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canadá": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za"
    }
    tld = accent_map[english_accent]
    
    # Función para convertir texto a voz
    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        my_file_name = text[:20] if text else "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    display_output_text = st.checkbox("Mostrar el texto de salida")

    if st.button("Convertir"):
        result, output_text = text_to_speech(input_language, output_language, spoken_text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("## 🎶 Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown("## ✍️ Texto de salida:")
            st.write(output_text)

    # Función para eliminar archivos temporales
    def remove_files(n):
        mp3_files = glob.glob("temp/*.mp3")
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted", f)

    remove_files(7)
