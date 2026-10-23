# Resumen diario por correo

Script en Python que cada día envía por correo un resumen con el clima de Medellín, la TRM del dólar y una frase del día, en un correo con diseño HTML.

## Qué incluye el correo

- **Saludo automático** según la hora (buenos días, buenas tardes o buenas noches) y fecha en español.
- **Clima de Medellín:** temperatura actual, máxima, mínima, probabilidad de lluvia y descripción con ícono.
- **Pronóstico por tramos:** mañana, tarde y noche.
- **Consejos automáticos:** paraguas, calor o chaqueta, según el pronóstico.
- **TRM del dólar** con la diferencia frente al valor anterior (▲ sube, ▼ baja).
- **Frase del día** elegida al azar de una lista.
- **Envío a varios destinatarios**, cada uno con su nombre en el saludo.
- **Aviso de errores:** si el script falla, llega un correo con el detalle.

## Fuentes de datos

- Clima: [Open-Meteo](https://open-meteo.com/) (gratis, sin clave).
- TRM: datos abiertos de Colombia ([datos.gov.co](https://www.datos.gov.co/)).

## Requisitos

- Python 3
- La librería `requests`
- Una cuenta de Gmail con **verificación en dos pasos** y una **contraseña de aplicación**

## Instalación

1. Instala la dependencia:

   ```
   python -m pip install requests
   ```

2. Crea una contraseña de aplicación en `myaccount.google.com/apppasswords`.

3. Guarda tus datos como variables de entorno (nunca los escribas dentro del código):

   ```
   setx GMAIL_USER "tucorreo@gmail.com"
   setx GMAIL_APP_PASSWORD "clave_de_16_letras"
   ```

   Después **cierra y vuelve a abrir** VS Code o la terminal para que las lea.

## Uso

Ejecuta el script a mano:

```
python Clima.py
```

## Configuración

Todo se cambia al inicio de `Clima.py`:

- `DESTINATARIOS`: lista de correos que reciben el resumen.
- `EXCEPCIONES`: nombre que se usa en el saludo cuando no se puede deducir del correo o lleva tilde.
- `LATITUD` y `LONGITUD`: ubicación del clima (por defecto, Medellín).
- `frases`: lista de frases del día.
- Cortes de los consejos (lluvia, calor, frío) en la sección "Consejos según el clima".

## Programarlo cada día (Windows)

Con el Programador de tareas de Windows, desde PowerShell (cambia las rutas por las tuyas):

```
schtasks /Create /TN "ResumenDiario" /SC DAILY /ST 07:00 /TR "cmd /c cd /d C:\ruta\a\la\carpeta && C:\ruta\a\python.exe Clima.py"
```

Para probarla al momento:

```
schtasks /Run /TN "ResumenDiario"
```

El computador debe estar encendido a esa hora. Si estaba apagado, conviene activar en las propiedades de la tarea la opción de ejecutarla lo antes posible tras omitir un inicio programado. Deja la tarea en **un solo equipo** para que los destinatarios no reciban el correo duplicado.

## Seguridad

- La contraseña de aplicación **no** está en el código ni debe subirse a GitHub.
- El repositorio contiene correos de destinatarios, por eso debe mantenerse **privado**.

## Ideas para mejorar

- Clima por ciudad según cada destinatario.
- Sección de noticias de tecnología por RSS.
- Lista de tareas del día leída desde un archivo.