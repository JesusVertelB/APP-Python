from datetime import datetime
import os
import random
import re
import smtplib
import sys
import traceback
from email.message import EmailMessage

import requests


# --- Aviso por correo si el script falla ---
def avisar_error(tipo, valor, tb):
    detalle = "".join(traceback.format_exception(tipo, valor, tb))
    print(detalle)  # el error se sigue viendo en la terminal
    try:
        correo = os.environ["GMAIL_USER"]
        clave = os.environ["GMAIL_APP_PASSWORD"]
        aviso = EmailMessage()
        aviso["Subject"] = "⚠️ Falló tu resumen diario"
        aviso["From"] = correo
        aviso["To"] = correo
        aviso.set_content(
            f"El script Clima.py falló el {datetime.now():%d/%m/%Y a las %H:%M}.\n\n{detalle}"
        )
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(correo, clave)
            servidor.send_message(aviso)
    except Exception:
        pass  # si ni el aviso se puede enviar, no hacemos nada más


sys.excepthook = avisar_error


# --- Destinatarios ---
DESTINATARIOS = [
    "vertelbravojesus@gmail.com",
    "hurtadomariana180@gmail.com",
]

# Para correos donde el nombre no se pueda deducir o lleva tilde.
EXCEPCIONES = {
    "vertelbravojesus@gmail.com": "Jesús",
    "hurtadomariana180@gmail.com": "Mariana",
}


def nombre_desde_correo(direccion):
    usuario = direccion.split("@")[0]
    if not re.search(r"[._\-+]", usuario):
        return None  # no hay separador, no se puede deducir
    primera_parte = re.split(r"[._\-+0-9]", usuario)[0]
    return primera_parte.capitalize() or None


# --- Datos de acceso (vienen de las variables de entorno) ---
CORREO = os.environ["GMAIL_USER"]
CLAVE = os.environ["GMAIL_APP_PASSWORD"]

# --- Clima ---
LATITUD = 6.2442
LONGITUD = -75.5812

respuesta = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    params={
        "latitude": LATITUD,
        "longitude": LONGITUD,
        "current": "temperature_2m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
        "hourly": "temperature_2m,precipitation_probability",
        "timezone": "America/Bogota",
    },
)
datos = respuesta.json()

temp_actual = datos["current"]["temperature_2m"]
maxima = datos["daily"]["temperature_2m_max"][0]
minima = datos["daily"]["temperature_2m_min"][0]
lluvia = datos["daily"]["precipitation_probability_max"][0]
codigo = datos["daily"]["weather_code"][0]

CLIMAS = {
    0: ("Despejado", "☀️"),
    1: ("Mayormente despejado", "🌤️"),
    2: ("Parcialmente nublado", "⛅"),
    3: ("Nublado", "☁️"),
    45: ("Niebla", "🌫️"),
    48: ("Niebla", "🌫️"),
    51: ("Llovizna ligera", "🌦️"),
    53: ("Llovizna", "🌦️"),
    55: ("Llovizna intensa", "🌧️"),
    61: ("Lluvia ligera", "🌧️"),
    63: ("Lluvia moderada", "🌧️"),
    65: ("Lluvia fuerte", "🌧️"),
    80: ("Chubascos ligeros", "🌦️"),
    81: ("Chubascos", "🌧️"),
    82: ("Chubascos fuertes", "⛈️"),
    95: ("Tormenta eléctrica", "⛈️"),
    96: ("Tormenta con granizo", "⛈️"),
    99: ("Tormenta con granizo", "⛈️"),
}
descripcion, icono = CLIMAS.get(codigo, ("Clima variable", "🌡️"))

# --- Pronóstico por tramos del día ---
horas = datos["hourly"]


def resumen_tramo(inicio, fin):
    temps = [t for t in horas["temperature_2m"][inicio:fin] if t is not None]
    lluvias = [p for p in horas["precipitation_probability"][inicio:fin] if p is not None]
    temp_media = round(sum(temps) / len(temps), 1)
    lluvia_max = max(lluvias)
    return temp_media, lluvia_max


tramos = [
    ("Mañana", 6, 12, "🌅"),
    ("Tarde", 12, 18, "☀️"),
    ("Noche", 18, 24, "🌙"),
]

tramos_texto = ""
tramos_html = ""
for nombre_tramo, inicio, fin, emoji in tramos:
    temp_media, lluvia_max = resumen_tramo(inicio, fin)
    tramos_texto += f"{emoji} {nombre_tramo}: {temp_media} °C, lluvia {lluvia_max}%\n"
    tramos_html += f"""<td width="33%" style="text-align:center; padding:12px 4px; background-color:#f7f8fa; border-radius:8px;">
      <div style="font-size:12px; color:#7b8794;">{emoji} {nombre_tramo}</div>
      <div style="font-size:18px; font-weight:600; color:#1b2a41;">{temp_media}°C</div>
      <div style="font-size:12px; color:#7b8794;">💧 {lluvia_max}%</div>
    </td>"""

# --- Consejos según el clima ---
consejos = []
if lluvia >= 60:
    consejos.append("☔ Lleva paraguas, hay alta probabilidad de lluvia.")
if maxima >= 30:
    consejos.append("🥵 Hoy hará calor, mantente hidratado.")
if minima <= 15:
    consejos.append("🧥 La mañana estará fresca, lleva una chaqueta.")

# Versión texto simple: vacía si no hay consejos
if consejos:
    consejo_texto = "\n" + "\n".join(consejos) + "\n"
else:
    consejo_texto = ""

# Versión HTML: una cajita crema, vacía si no hay consejos
if consejos:
    consejo_html = (
        '<div style="background-color:#fdf6e7; border-radius:6px; padding:12px 16px; '
        'margin-top:16px; color:#1b2a41; font-size:14px; line-height:1.6;">'
        + "<br>".join(consejos)
        + "</div>"
    )
else:
    consejo_html = ""

# --- TRM ---
respuesta_trm = requests.get(
    "https://www.datos.gov.co/resource/32sa-8pi3.json",
    params={"$order": "vigenciadesde DESC", "$limit": 2},
)
datos_trm = respuesta_trm.json()
trm = float(datos_trm[0]["valor"])
trm_anterior = float(datos_trm[1]["valor"])
desde = datos_trm[0]["vigenciadesde"][:10]

cambio = trm - trm_anterior
if cambio > 0:
    flecha, color_cambio = "▲", "#c0392b"   # sube: rojo
elif cambio < 0:
    flecha, color_cambio = "▼", "#2e8b57"   # baja: verde
else:
    flecha, color_cambio = "=", "#7b8794"   # igual: gris
cambio_texto = f"{flecha} ${abs(cambio):,.2f} frente al valor anterior"

# --- Frase del día ---
frases = [
    "Un pequeño avance cada día suma más que un gran esfuerzo de vez en cuando.",
    "No tienes que ser perfecto para empezar, solo tienes que empezar.",
    "Los errores son la prueba de que estás intentando.",
    "Aprender a programar es resolver un problema a la vez.",
    "Lo que hoy cuesta trabajo, mañana será un hábito.",
    "La constancia le gana al talento cuando el talento no es constante.",
]
frase = random.choice(frases)

# --- Fecha en español ---
dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
hoy = datetime.now()
fecha_texto = f"{dias[hoy.weekday()].capitalize()}, {hoy.day} de {meses[hoy.month - 1]} de {hoy.year}"

# --- Saludo según la hora ---
if hoy.hour < 12:
    saludo = "Buenos días"
elif hoy.hour < 18:
    saludo = "Buenas tardes"
else:
    saludo = "Buenas noches"

# --- Versión en texto simple (respaldo) ---
texto = f"""{saludo}, Jesús.

CLIMA
{icono} {descripcion}
Temperatura actual: {temp_actual} °C
Máxima: {maxima} °C | Mínima: {minima} °C
Probabilidad de lluvia: {lluvia}%

{tramos_texto}{consejo_texto}
DÓLAR
TRM vigente desde {desde}: ${trm:,.2f} COP
{cambio_texto}

FRASE DEL DÍA
{frase}
"""

# --- Versión HTML elegante ---
html = f"""\
<html>
<body style="margin:0; padding:0; background-color:#f1f3f6;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f1f3f6; padding:24px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px; width:100%; background-color:#ffffff; border-radius:12px; overflow:hidden; font-family:Segoe UI, Helvetica, Arial, sans-serif;">

        <!-- Encabezado -->
        <tr><td style="background-color:#1b2a41; padding:32px 36px;">
          <div style="color:#c9a45c; font-size:12px; letter-spacing:3px; text-transform:uppercase;">Tu resumen del día</div>
          <div style="color:#ffffff; font-size:26px; font-weight:600; margin-top:8px;">{saludo}, Jesús</div>
          <div style="color:#a9b4c4; font-size:14px; margin-top:6px;">{fecha_texto}</div>
        </td></tr>

        <!-- Clima -->
        <tr><td style="padding:32px 36px 8px 36px;">
          <div style="color:#c9a45c; font-size:12px; letter-spacing:2px; text-transform:uppercase; font-weight:600;">Clima · Medellín</div>
          <div style="color:#1b2a41; font-size:44px; font-weight:300; margin:10px 0 4px 0;">{temp_actual}°C</div>
          <div style="color:#1b2a41; font-size:16px; margin-bottom:6px;">{icono} {descripcion}</div>
          <table cellpadding="0" cellspacing="0" style="margin-top:12px;">
            <tr>
              <td style="padding-right:28px;">
                <div style="color:#7b8794; font-size:12px;">Máxima</div>
                <div style="color:#1b2a41; font-size:18px; font-weight:600;">{maxima}°C</div>
              </td>
              <td style="padding-right:28px;">
                <div style="color:#7b8794; font-size:12px;">Mínima</div>
                <div style="color:#1b2a41; font-size:18px; font-weight:600;">{minima}°C</div>
              </td>
              <td>
                <div style="color:#7b8794; font-size:12px;">Lluvia</div>
                <div style="color:#1b2a41; font-size:18px; font-weight:600;">{lluvia}%</div>
              </td>
            </tr>
          </table>
          <table width="100%" cellpadding="0" cellspacing="6" style="margin-top:16px;">
            <tr>{tramos_html}</tr>
          </table>
          {consejo_html}
        </td></tr>

        <tr><td style="padding:24px 36px 0 36px;"><div style="border-top:1px solid #e4e7ec;"></div></td></tr>

        <!-- Dólar -->
        <tr><td style="padding:24px 36px 8px 36px;">
          <div style="color:#c9a45c; font-size:12px; letter-spacing:2px; text-transform:uppercase; font-weight:600;">Dólar · TRM</div>
          <div style="color:#1b2a41; font-size:32px; font-weight:300; margin:10px 0 4px 0;">${trm:,.2f} <span style="font-size:14px; color:#7b8794;">COP</span></div>
          <div style="color:{color_cambio}; font-size:14px; font-weight:600; margin-top:6px;">{cambio_texto}</div>
        </td></tr>

        <tr><td style="padding:24px 36px 0 36px;"><div style="border-top:1px solid #e4e7ec;"></div></td></tr>

        <!-- Frase -->
        <tr><td style="padding:24px 36px 36px 36px;">
          <div style="background-color:#f7f4ed; border-left:4px solid #c9a45c; padding:18px 22px; border-radius:4px;">
            <div style="color:#1b2a41; font-size:16px; font-style:italic; line-height:1.6;">"{frase}"</div>
          </div>
        </td></tr>

        <!-- Pie -->
        <tr><td style="background-color:#f1f3f6; padding:16px 36px; text-align:center;">
          <div style="color:#98a2b3; font-size:11px;">Generado automáticamente por Python</div>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""

# --- Armar y enviar un correo por persona ---
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
    servidor.login(CORREO, CLAVE)

    for direccion in DESTINATARIOS:
        nombre = EXCEPCIONES.get(direccion, nombre_desde_correo(direccion))

        if nombre:
            texto_final = texto.replace("Jesús", nombre)
            html_final = html.replace("Jesús", nombre)
        else:
            texto_final = texto.replace(", Jesús", "")
            html_final = html.replace(", Jesús", "")

        mensaje = EmailMessage()
        mensaje["Subject"] = f"Tu resumen del día · {hoy.day} de {meses[hoy.month - 1]}"
        mensaje["From"] = CORREO
        mensaje["To"] = direccion
        mensaje.set_content(texto_final)
        mensaje.add_alternative(html_final, subtype="html")
        servidor.send_message(mensaje)
        print(f"Enviado a {nombre or 'sin nombre'} ({direccion})")