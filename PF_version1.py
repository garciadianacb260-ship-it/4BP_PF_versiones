# =========================================================
# NEKOCOFFE - SISTEMA TKINTER + FIREBASE
# =========================================================

# ---------------- 1. LIBRERÍAS ----------------
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import firebase_admin
from firebase_admin import credentials, firestore
from PIL import Image, ImageTk
import os
import shutil
from datetime import datetime

# ---------------- 2. CONEXIÓN ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "imagenes")
os.makedirs(IMAGES_DIR, exist_ok=True)

cred_path = os.path.join(BASE_DIR, "Clavebasededatos.json")

if not os.path.exists(cred_path):
    raise FileNotFoundError("No se encontró Clavebasededatos.json")

cred = credentials.Certificate(cred_path)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

ESPRESSO = "#3C2415"
CREMA = "#F5E6D3"
LATTE = "#D4A574"
BLANCO = "#FFFFFF"

FONT = "Helvetica"

usuario_actual = None

# =========================================================
# VENTANA PRINCIPAL
# =========================================================

root = tk.Tk()
root.title("Nekocoffe")
root.geometry("1200x750")
root.configure(bg=CREMA)

# =========================================================
# CONTENEDOR GENERAL
# =========================================================

main_container = tk.Frame(root, bg=CREMA)
main_container.pack(fill="both", expand=True)

# =========================================================
# HEADER
# =========================================================

header = tk.Frame(main_container, bg=CREMA, height=90)
header.pack(fill="x")
header.pack_propagate(False)

# ---------------- LOGO ----------------

logo_path = r"E:\Diana4B\logo.jpeg"

logo_frame = tk.Frame(header, bg=CREMA)
logo_frame.pack(side="left", padx=15)

if os.path.exists(logo_path):
    img = Image.open(logo_path)
    img = img.resize((70, 70))
    logo_img = ImageTk.PhotoImage(img)

    logo_label = tk.Label(
        logo_frame,
        image=logo_img,
        bg=CREMA
    )
    logo_label.pack()
else:
    canvas_logo = tk.Canvas(
        logo_frame,
        width=70,
        height=70,
        bg=CREMA,
        highlightthickness=0
    )
    canvas_logo.create_oval(
        5, 5, 65, 65,
        fill=ESPRESSO
    )
    canvas_logo.pack()

# ---------------- TITULO ----------------

title_frame = tk.Frame(header, bg=CREMA)
title_frame.pack(side="left", expand=True)

titulo = tk.Label(
    title_frame,
    text="Nekocoffe",
    font=(FONT, 18, "bold"),
    fg=ESPRESSO,
    bg=CREMA
)
titulo.pack()

subtitulo = tk.Label(
    title_frame,
    text="Donde cada sorbo ronronea",
    font=(FONT, 10, "italic"),
    fg=LATTE,
    bg=CREMA
)
subtitulo.pack()

# ---------------- MENÚ HAMBURGUESA ----------------

menu_visible = False

menu_lateral = tk.Frame(
    root,
    bg=ESPRESSO,
    width=250
)

def toggle_menu():
    global menu_visible

    if menu_visible:
        menu_lateral.place_forget()
        menu_visible = False
    else:
        menu_lateral.place(x=0, y=90, height=650)
        menu_visible = True

btn_menu = tk.Button(
    header,
    text="☰",
    font=(FONT, 20, "bold"),
    bg=CREMA,
    fg=ESPRESSO,
    bd=0,
    command=toggle_menu
)
btn_menu.pack(side="right", padx=20)

# Línea divisoria
linea = tk.Frame(main_container, bg=ESPRESSO, height=2)
linea.pack(fill="x")

# =========================================================
# CONTENIDO
# =========================================================

contenedor = tk.Frame(main_container, bg=CREMA)
contenedor.pack(fill="both", expand=True)

# =========================================================
# FOOTER
# =========================================================

footer = tk.Frame(main_container, bg=ESPRESSO, height=45)
footer.pack(fill="x")
footer.pack_propagate(False)

footer_label = tk.Label(
    footer,
    text="Nekocoffe © 2026 | Siete vidas, un mismo hogar",
    bg=ESPRESSO,
    fg=CREMA,
    font=(FONT, 8)
)
footer_label.pack(pady=12)

# =========================================================
# LIMPIAR CONTENIDO
# =========================================================

def limpiar_contenido():
    for widget in contenedor.winfo_children():
        widget.destroy()

# =========================================================
# TABLA DE CLIENTES
# =========================================================

def tabla_clientes():

    frame_tabla = tk.Frame(contenedor, bg=CREMA)
    frame_tabla.pack(fill="both", expand=True, pady=20)

    tabla = ttk.Treeview(
        frame_tabla,
        columns=("Nombre","Email","Telefono",
                 "Ubicacion","Intereses","Fecha"),
        show="tree headings",
        height=10
    )

    tabla.heading("#0", text="Foto")
    tabla.column("#0", width=80)

    for col in ("Nombre","Email","Telefono",
                "Ubicacion","Intereses","Fecha"):

        tabla.heading(col, text=col)
        tabla.column(col, width=130, anchor="center")

    tabla.pack(fill="both", expand=True)

    try:
        usuarios = db.collection("usuarios").stream()

        for user in usuarios:
            data = user.to_dict()

            tabla.insert(
                "",
                "end",
                text="📷",
                values=(
                    data.get("nombre", ""),
                    data.get("email", ""),
                    data.get("telefono", ""),
                    data.get("direccion", ""),
                    data.get("intereses", ""),
                    data.get("fecha", "")
                )
            )

    except Exception as e:
        messagebox.showerror("Error", str(e))

# =========================================================
# REGISTRO
# =========================================================

def abrir_registro():

    limpiar_contenido()

    titulo = tk.Label(
        contenedor,
        text="Registro / Login",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 18, "bold")
    )
    titulo.pack(pady=20)

    form = tk.Frame(contenedor, bg=CREMA)
    form.pack()

    campos = {}

    labels = [
        "Nombre completo",
        "Correo electrónico",
        "Contraseña",
        "Confirmar contraseña",
        "Número de teléfono"
    ]

    for texto in labels:

        tk.Label(
            form,
            text=texto,
            bg=CREMA,
            fg=ESPRESSO,
            font=(FONT, 11, "bold")
        ).pack(anchor="w", pady=5)

        entry = tk.Entry(
            form,
            width=40,
            font=(FONT, 11),
            show="*" if "Contraseña" in texto else ""
        )
        entry.pack(pady=5)

        campos[texto] = entry

    # FOTO
    foto_path = tk.StringVar()

    def seleccionar_foto():
        archivo = filedialog.askopenfilename(
            filetypes=[("Imagen", "*.png *.jpg *.jpeg")]
        )

        if archivo:
            destino = os.path.join(
                IMAGES_DIR,
                os.path.basename(archivo)
            )

            shutil.copy(archivo, destino)

            foto_path.set(destino)

    tk.Button(
        form,
        text="Seleccionar foto",
        bg=LATTE,
        fg=BLANCO,
        command=seleccionar_foto
    ).pack(pady=10)

    # CHECKBOX
    aceptar = tk.BooleanVar()

    tk.Checkbutton(
        form,
        text="Acepto términos y aviso de privacidad",
        variable=aceptar,
        bg=CREMA,
        fg=ESPRESSO
    ).pack(pady=10)

    # GUARDAR
    def registrar():

        nombre = campos["Nombre completo"].get()
        email = campos["Correo electrónico"].get()
        password = campos["Contraseña"].get()
        confirm = campos["Confirmar contraseña"].get()
        telefono = campos["Número de teléfono"].get()

        if not nombre or not email or not password:
            messagebox.showerror(
                "Error",
                "Completa todos los campos obligatorios"
            )
            return

        if len(password) < 8:
            messagebox.showerror(
                "Error",
                "La contraseña debe tener mínimo 8 caracteres"
            )
            return

        if password != confirm:
            messagebox.showerror(
                "Error",
                "Las contraseñas no coinciden"
            )
            return

        if not aceptar.get():
            messagebox.showerror(
                "Error",
                "Debes aceptar términos"
            )
            return

        datos = {
            "nombre": nombre,
            "email": email,
            "telefono": telefono,
            "foto": foto_path.get(),
            "fecha": datetime.now().strftime("%d/%m/%Y")
        }

        db.collection("usuarios").add(datos)

        messagebox.showinfo(
            "Éxito",
            "Usuario registrado correctamente"
        )

        tabla_clientes()

    tk.Button(
        form,
        text="Registrarse",
        bg=ESPRESSO,
        fg=BLANCO,
        font=(FONT, 11, "bold"),
        command=registrar
    ).pack(pady=20)

# =========================================================
# MODIFICAR PERFIL
# =========================================================

def modificar_perfil():

    limpiar_contenido()

    tk.Label(
        contenedor,
        text="Modificación del Perfil",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 18, "bold")
    ).pack(pady=20)

    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack()

    campos = [
        "Fecha nacimiento",
        "Dirección",
        "Nueva contraseña"
    ]

    for campo in campos:

        tk.Label(
            frame,
            text=campo,
            bg=CREMA,
            fg=ESPRESSO
        ).pack(anchor="w")

        tk.Entry(
            frame,
            width=40
        ).pack(pady=5)

    # ALERGIAS
    tk.Label(
        frame,
        text="Alergias alimentarias",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 11, "bold")
    ).pack(pady=10)

    opciones = [
        "Gluten",
        "Lactosa",
        "Nueces",
        "Otro"
    ]

    for op in opciones:
        tk.Checkbutton(
            frame,
            text=op,
            bg=CREMA
        ).pack(anchor="w")

# =========================================================
# CONOCE
# =========================================================

def conoce():

    limpiar_contenido()

    texto = """
Bienvenido a Nekocoffe ☕

Una cafetería temática donde el amor
por el café y los gatos se unen.

Misión:
Crear un refugio cálido donde el café de especialidad y la compañía
felina se unen para sanar, conectar y dar segundas oportunidades.
Cada taza que servimos sostiene el bienestar de nuestros gatos rescatados
y regala a nuestros clientes un momento de calma que ronronea.

Visión:
Ser el cat-café referente en Latinoamérica por su impacto social y calidad,
demostrando que un negocio puede ser rentable, delicioso y compasivo. 
Queremos que cada ciudad tenga un Nekocoffe: un lugar donde las personas y 
los gatos se salvan mutuamente, un sorbo a la vez.

Valores:
1.Bienestar primero: La salud y felicidad de nuestros 7 michis está antes que todo
2.Calidez real: Atendemos como el abuelo: con café caliente y escucha honesta
3.Segundas oportunidades: Para gatos, para personas, para días malos
4.Transparencia: Cada peso del menú sostiene comida, vet y arena
5.Comunidad: No somos cafetería, somos refugio con puertas abiertas
"""

    tk.Label(
        contenedor,
        text=texto,
        justify="left",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 12)
    ).pack(padx=40, pady=40)

# =========================================================
# CONTACTO
# =========================================================

def contacto():

    limpiar_contenido()

    tk.Label(
        contenedor,
        text="Contacto",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 18, "bold")
    ).pack(pady=20)

    form = tk.Frame(contenedor, bg=CREMA)
    form.pack()

    campos = [
        "Nombre",
        "Correo",
        "Teléfono",
        "Asunto"
    ]

    for campo in campos:

        tk.Label(
            form,
            text=campo,
            bg=CREMA,
            fg=ESPRESSO
        ).pack(anchor="w")

        tk.Entry(form, width=40).pack(pady=5)

    tk.Label(
        form,
        text="Mensaje",
        bg=CREMA
    ).pack(anchor="w")

    tk.Text(
        form,
        width=50,
        height=5
    ).pack()

# =========================================================
# RESERVACIÓN
# =========================================================

def reservacion():

    limpiar_contenido()

    tk.Label(
        contenedor,
        text="Reservación de Mesa",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 18, "bold")
    ).pack(pady=20)

    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack()

    datos = [
        "Fecha",
        "Hora",
        "Zona",
        "Número de personas",
        "Nombre"
    ]

    for dato in datos:

        tk.Label(
            frame,
            text=dato,
            bg=CREMA
        ).pack(anchor="w")

        ttk.Entry(frame, width=40).pack(pady=5)

    aceptar = tk.BooleanVar()

    tk.Checkbutton(
        frame,
        text="Leí y acepto normas",
        variable=aceptar,
        bg=CREMA
    ).pack(pady=10)

# =========================================================
# 5. FILTRO DE MENÚ
# =========================================================

def filtro_menu():

    limpiar_contenido()

    tk.Label(
        contenedor,
        text="Filtro de Menú",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 18, "bold")
    ).pack(pady=20)

    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack(pady=20)

    # ---------------- TIPO ----------------

    tk.Label(
        frame,
        text="Tipo",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 11, "bold")
    ).pack(anchor="w")

    tipo = ttk.Combobox(
        frame,
        values=[
            "Bebida caliente",
            "Fría",
            "Postre"
        ],
        width=35
    )
    tipo.pack(pady=5)

    # ---------------- RESTRICCIONES ----------------

    tk.Label(
        frame,
        text="Restricciones",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 11, "bold")
    ).pack(anchor="w", pady=10)

    restricciones = [
        "Sin cafeína",
        "Sin lactosa",
        "Sin gluten",
        "Vegano"
    ]

    for r in restricciones:
        tk.Checkbutton(
            frame,
            text=r,
            bg=CREMA,
            fg=ESPRESSO
        ).pack(anchor="w")

    # ---------------- PRECIO ----------------

    tk.Label(
        frame,
        text="Rango de precio",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 11, "bold")
    ).pack(anchor="w", pady=10)

    precio = tk.Scale(
        frame,
        from_=50,
        to=200,
        orient="horizontal",
        bg=CREMA,
        fg=ESPRESSO,
        troughcolor=LATTE,
        length=300
    )
    precio.pack()

# =========================================================
# 7. PERFILES DE MICHIS
# =========================================================

def perfiles_michis():

    limpiar_contenido()

    tk.Label(
        contenedor,
        text="Perfiles de Michis",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 18, "bold")
    ).pack(pady=20)

    gatos = [
        ("Moka", "2 años", "Juguetón"),
        ("Luna", "1 año", "Cariñosa"),
        ("Simba", "3 años", "Dormilón")
    ]

    frame_cards = tk.Frame(contenedor, bg=CREMA)
    frame_cards.pack()

    for nombre, edad, personalidad in gatos:

        card = tk.Frame(
            frame_cards,
            bg=BLANCO,
            bd=1,
            relief="solid"
        )
        card.pack(
            side="left",
            padx=15,
            pady=10
        )

        tk.Label(
            card,
            text="🐱",
            font=(FONT, 40),
            bg=BLANCO
        ).pack(pady=10)

        tk.Label(
            card,
            text=nombre,
            font=(FONT, 13, "bold"),
            bg=BLANCO,
            fg=ESPRESSO
        ).pack()

        tk.Label(
            card,
            text=f"Edad: {edad}",
            bg=BLANCO
        ).pack()

        tk.Label(
            card,
            text=f"Personalidad: {personalidad}",
            bg=BLANCO
        ).pack()

        # BOTÓN ADOPCIÓN

        def adoptar(gato=nombre):

            ventana = tk.Toplevel(root)
            ventana.title(f"Adoptar a {gato}")
            ventana.geometry("400x350")
            ventana.configure(bg=CREMA)

            tk.Label(
                ventana,
                text=f"Me interesa adoptar a {gato}",
                bg=CREMA,
                fg=ESPRESSO,
                font=(FONT, 14, "bold")
            ).pack(pady=15)

            preguntas = [
                "¿Tienes otros gatos?",
                "Tipo de vivienda",
                "Teléfono"
            ]

            for p in preguntas:

                tk.Label(
                    ventana,
                    text=p,
                    bg=CREMA
                ).pack(anchor="w", padx=20)

                tk.Entry(
                    ventana,
                    width=35
                ).pack(pady=5)

            tk.Button(
                ventana,
                text="Enviar solicitud",
                bg=ESPRESSO,
                fg=BLANCO
            ).pack(pady=20)

        tk.Button(
            card,
            text=f"Adoptar a {nombre}",
            bg=LATTE,
            fg=BLANCO,
            command=adoptar
        ).pack(pady=10)

# =========================================================
# 8. NORMAS DE CONVIVENCIA
# =========================================================

def normas():

    limpiar_contenido()

    tk.Label(
        contenedor,
        text="Normas de Convivencia",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 18, "bold")
    ).pack(pady=20)

    reglas = """
• No cargar a los gatos
• No usar flash
• Lavarse las manos antes y después
• Niños siempre acompañados
• No alimentar gatos sin permiso
"""

    tk.Label(
        contenedor,
        text=reglas,
        justify="left",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 12)
    ).pack(pady=15)

    aceptar = tk.BooleanVar()

    tk.Checkbutton(
        contenedor,
        text="He leído y acepto las normas",
        variable=aceptar,
        bg=CREMA,
        fg=ESPRESSO
    ).pack(pady=10)

    tk.Label(
        contenedor,
        text="¿Cuántos menores de 12 años?",
        bg=CREMA
    ).pack()

    tk.Spinbox(
        contenedor,
        from_=0,
        to=10,
        width=10
    ).pack()

# =========================================================
# 9. PEDIDO Y PAGO ONLINE
# =========================================================

def pedido_online():

    limpiar_contenido()

    tk.Label(
        contenedor,
        text="Pedido y Pago Online",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 18, "bold")
    ).pack(pady=20)

    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack()

    # PRODUCTOS

    tk.Label(
        frame,
        text="Producto",
        bg=CREMA,
        fg=ESPRESSO
    ).pack(anchor="w")

    productos = ttk.Combobox(
        frame,
        values=[
            "Latte Gatuno",
            "Moka Felino",
            "Cheesecake",
            "Cold Brew"
        ],
        width=35
    )
    productos.pack(pady=5)

    # CANTIDAD

    tk.Label(
        frame,
        text="Cantidad",
        bg=CREMA
    ).pack(anchor="w")

    tk.Spinbox(
        frame,
        from_=1,
        to=20,
        width=10
    ).pack(pady=5)

    # CONSUMO

    tk.Label(
        frame,
        text="Tipo de consumo",
        bg=CREMA
    ).pack(anchor="w")

    consumo = ttk.Combobox(
        frame,
        values=[
            "Aquí",
            "Para llevar"
        ],
        width=35
    )
    consumo.pack(pady=5)

    # MÉTODO PAGO

    tk.Label(
        frame,
        text="Método de pago",
        bg=CREMA
    ).pack(anchor="w")

    pago = ttk.Combobox(
        frame,
        values=[
            "Tarjeta",
            "Transferencia",
            "Efectivo en local"
        ],
        width=35
    )
    pago.pack(pady=5)

    # TARJETA

    tarjeta_frame = tk.Frame(frame, bg=CREMA)
    tarjeta_frame.pack()

    campos_tarjeta = [
        "Número tarjeta",
        "Vencimiento",
        "CVV",
        "Nombre titular"
    ]

    for c in campos_tarjeta:

        tk.Label(
            tarjeta_frame,
            text=c,
            bg=CREMA
        ).pack(anchor="w")

        tk.Entry(
            tarjeta_frame,
            width=35
        ).pack(pady=5)

    # PROPINA

    tk.Label(
        frame,
        text="Propina",
        bg=CREMA
    ).pack(anchor="w")

    ttk.Combobox(
        frame,
        values=[
            "0%",
            "10%",
            "15%",
            "Otro"
        ],
        width=35
    ).pack(pady=5)

    # FACTURA

    factura = tk.BooleanVar()

    tk.Checkbutton(
        frame,
        text="Solicitar factura",
        variable=factura,
        bg=CREMA
    ).pack(pady=10)

    factura_frame = tk.Frame(frame, bg=CREMA)
    factura_frame.pack()

    datos_factura = [
        "RFC",
        "Razón social",
        "CFDI",
        "Email"
    ]

    for dato in datos_factura:

        tk.Label(
            factura_frame,
            text=dato,
            bg=CREMA
        ).pack(anchor="w")

        tk.Entry(
            factura_frame,
            width=35
        ).pack(pady=5)

    # BOTÓN

    def pagar():

        messagebox.showinfo(
            "Pago",
            "Pago procesado correctamente"
        )

    tk.Button(
        frame,
        text="Pagar ahora",
        bg=ESPRESSO,
        fg=BLANCO,
        font=(FONT, 11, "bold"),
        command=pagar
    ).pack(pady=20)

# =========================================================
# 10. PROGRAMA MICHILOVERS
# =========================================================

def michilovers():

    limpiar_contenido()

    tk.Label(
        contenedor,
        text="Programa MichiLovers",
        bg=CREMA,
        fg=ESPRESSO,
        font=(FONT, 18, "bold")
    ).pack(pady=20)

    puntos = 250

    card = tk.Frame(
        contenedor,
        bg=BLANCO,
        bd=1,
        relief="solid"
    )
    card.pack(pady=20, padx=20)

    tk.Label(
        card,
        text=f"Puntos disponibles: {puntos}",
        bg=BLANCO,
        fg=ESPRESSO,
        font=(FONT, 16, "bold")
    ).pack(padx=40, pady=20)

    tk.Label(
        card,
        text="1 punto = $10 gastados",
        bg=BLANCO,
        fg=LATTE,
        font=(FONT, 10)
    ).pack()

    tk.Label(
        card,
        text="Los puntos vencen en 6 meses",
        bg=BLANCO,
        fg=LATTE,
        font=(FONT, 10)
    ).pack(pady=5)

    # RECOMPENSAS

    tk.Label(
        card,
        text="Selecciona recompensa",
        bg=BLANCO,
        fg=ESPRESSO
    ).pack(pady=10)

    recompensa = ttk.Combobox(
        card,
        values=[
            "Café gratis",
            "Sticker",
            "Donación"
        ],
        width=30
    )
    recompensa.pack()

    # CONFIRMACIÓN

    def canjear():

        confirmar = messagebox.askyesno(
            "Confirmar",
            "¿Usar 100 puntos?"
        )

        if confirmar:
            messagebox.showinfo(
                "Éxito",
                "Recompensa canjeada"
            )

    tk.Button(
        card,
        text="Canjear recompensa",
        bg=LATTE,
        fg=BLANCO,
        command=canjear
    ).pack(pady=20)

# =========================================================
# ACTUALIZAR MENÚ LATERAL
# =========================================================

for widget in menu_lateral.winfo_children():
    widget.destroy()

paginas = [
    ("1 Registro/Login", abrir_registro),
    ("2 Modificación del perfil", modificar_perfil),
    ("3 Conoce Nekocoffe", conoce),
    ("4 Contacto", contacto),
    ("5 Filtro de menú", filtro_menu),
    ("6 Reservación de mesa", reservacion),
    ("7 Perfiles de Michis", perfiles_michis),
    ("8 Normas de convivencia", normas),
    ("9 Pedido y pago online", pedido_online),
    ("10 Programa MichiLovers", michilovers)
]

for texto, comando in paginas:

    tk.Button(
        menu_lateral,
        text=texto,
        bg=ESPRESSO,
        fg=BLANCO,
        activebackground=LATTE,
        activeforeground=BLANCO,
        font=(FONT, 11, "bold"),
        bd=0,
        anchor="w",
        padx=20,
        command=comando
    ).pack(fill="x", pady=2, ipady=12)

# =========================================================
# PANTALLA INICIAL
# =========================================================

conoce()

# =========================================================
# EJECUTAR
# =========================================================

root.mainloop()