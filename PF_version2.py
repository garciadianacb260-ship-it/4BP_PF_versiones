import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import firebase_admin
from firebase_admin import credentials, firestore
from PIL import Image, ImageTk
import os
import shutil
from datetime import datetime

# ---------------- 1. CONFIGURACIÓN NEKOCOFFE ----------------
ESPRESSO = "#3C2415"
CREMA = "#F5E6D3"
LATTE = "#D4A574"
BLANCO = "#FFFFFF"
FONT = "Helvetica"

usuario_actual = None
ruta_imagen = ""
doc_actual = None
imagen_actual = ""
imagenes_guardadas = []
sesion_iniciada = False

entrada_id = entrada_nombre = entrada_campo3 = entrada_campo4 = entrada_campo5 = None
imagen_preview = None
tabla_perfil = tabla_reserva = tabla_pedido = tabla_usuarios = tabla_contacto = None

# ---------------- 2. CONEXIÓN FIREBASE ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "imagenes")
os.makedirs(IMAGES_DIR, exist_ok=True)

cred_path = os.path.join(BASE_DIR, "Clavebasededatos.json")
if not os.path.exists(cred_path):
    raise FileNotFoundError("No se encontró Clavebasededatos.json en la carpeta del proyecto")

cred = credentials.Certificate(cred_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------- 3. VENTANA PRINCIPAL ----------------
root = tk.Tk()
root.title("Nekocoffe")
root.geometry("1200x750")
root.configure(bg=CREMA)

main_container = tk.Frame(root, bg=CREMA)
main_container.pack(fill="both", expand=True)

# ---------------- 4. HEADER ----------------
header = tk.Frame(main_container, bg=CREMA, height=90)
header.pack(fill="x")
header.pack_propagate(False)

logo_path = r"E:\Diana4B\logo.jpeg"
logo_frame = tk.Frame(header, bg=CREMA)
logo_frame.pack(side="left", padx=20)

try:
    logo_img = Image.open(logo_path).resize((70, 70))
    logo_tk = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(logo_frame, image=logo_tk, bg=CREMA)
    logo_label.image = logo_tk
    logo_label.pack()
except:
    canvas = tk.Canvas(logo_frame, width=70, height=70, bg=CREMA, highlightthickness=0)
    canvas.create_oval(5, 5, 65, 65, fill=ESPRESSO)
    canvas.pack()

titulo_frame = tk.Frame(header, bg=CREMA)
titulo_frame.pack(side="left", expand=True)
tk.Label(titulo_frame, text="Nekocoffe", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack()
tk.Label(titulo_frame, text="Donde cada sorbo ronronea", bg=CREMA, fg=LATTE, font=(FONT, 10, "italic")).pack()

def toggle_menu():
    if menu_lateral.winfo_viewable():
        menu_lateral.place_forget()
    else:
        menu_lateral.place(x=0, y=90, height=650)
        menu_lateral.lift()

tk.Button(header, text="☰", bg=CREMA, fg=ESPRESSO, font=(FONT, 20, "bold"), bd=0, command=toggle_menu).pack(side="right", padx=20)
tk.Frame(main_container, bg=ESPRESSO, height=2).pack(fill="x")

# ---------------- 5. MENÚ LATERAL ----------------
menu_lateral = tk.Frame(main_container, bg=ESPRESSO, width=250)

# ---------------- 6. CONTENEDOR - DEFINIDO ANTES DE USARLO ----------------
contenedor = tk.Frame(main_container, bg=CREMA)
contenedor.pack(fill="both", expand=True, padx=20, pady=10)

def limpiar_contenido():
    for widget in contenedor.winfo_children():
        widget.destroy()

def crear_tabla_con_scroll(parent, columnas):
    frame_tabla = tk.Frame(parent, bg=BLANCO)
    frame_tabla.pack(fill="both", expand=True, pady=10)
    scroll_y = tk.Scrollbar(frame_tabla)
    scroll_y.pack(side="right", fill="y")
    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="tree headings", yscrollcommand=scroll_y.set, height=8)
    tabla.heading("#0", text="Foto")
    tabla.column("#0", width=80, anchor="center")
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=120, anchor="center")
    tabla.pack(fill="both", expand=True)
    scroll_y.config(command=tabla.yview)
    return tabla, frame_tabla

def hacer_scrollable(funcion_original):
    def wrapper():
        limpiar_contenido()
        canvas = tk.Canvas(contenedor, bg=CREMA, highlightthickness=0)
        scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=CREMA)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Guardar referencia original y usar scroll_frame temporalmente
        contenedor_original = contenedor
        globals()['contenedor'] = scroll_frame
        funcion_original()
        globals()['contenedor'] = contenedor_original

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    return wrapper

# ---------------- 7. FUNCIONES CRUD NEKOCOFFE ----------------
def seleccionar_imagen():
    global ruta_imagen
    ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp")])
    if ruta:
        ruta_imagen = ruta
        img = Image.open(ruta).resize((80, 80))
        img_tk = ImageTk.PhotoImage(img)
        imagen_preview.config(image=img_tk, text="")
        imagen_preview.image = img_tk

def guardar_registro(coleccion):
    global ruta_imagen
    mat = entrada_id.get().strip()
    nom = entrada_nombre.get().strip()
    esp = entrada_campo3.get().strip()
    prom_txt = entrada_campo4.get().strip()
    horas_txt = entrada_campo5.get().strip()
    if not all([mat, nom, esp, prom_txt, horas_txt, ruta_imagen]):
        messagebox.showwarning("Atención", "Faltan datos y foto obligatoria.")
        return
    try:
        nombre_img = f"{mat}_{os.path.basename(ruta_imagen)}"
        ruta_destino = os.path.join(IMAGES_DIR, nombre_img)
        shutil.copy(ruta_imagen, ruta_destino)
        datos = {"id": mat, "nombre": nom, "campo3": esp, "campo4": prom_txt, "campo5": horas_txt, "imagen": ruta_destino}
        db.collection(coleccion).add(datos)
        messagebox.showinfo("Éxito", "Registro guardado")
        limpiar_campos()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def limpiar_campos():
    global ruta_imagen, doc_actual, imagen_actual
    for e in [entrada_id, entrada_nombre, entrada_campo4, entrada_campo5]:
        e.delete(0, tk.END)
    entrada_campo3.delete(0, tk.END)
    imagen_preview.config(image="", text="Sin foto")
    ruta_imagen = ""
    doc_actual = None
    imagen_actual = ""

def mostrar_datos(coleccion):
    global imagenes_guardadas
    tabla = tabla_perfil if coleccion == "perfiles" else tabla_reserva if coleccion == "reservas" else tabla_pedido
    for item in tabla.get_children():
        tabla.delete(item)
    imagenes_guardadas.clear()
    docs = list(db.collection(coleccion).stream())
    if not docs:
        messagebox.showinfo("Info", "No hay registros")
        return
    for doc in docs:
        d = doc.to_dict()
        img_tk = None
        try:
            img = Image.open(d["imagen"]).resize((65, 65))
            img_tk = ImageTk.PhotoImage(img)
            imagenes_guardadas.append(img_tk)
        except: pass
        tabla.insert("", "end", text="", image=img_tk if img_tk else "",
                    values=(d.get("id", ""), d.get("nombre", ""), d.get("campo3", ""), d.get("campo4", ""), d.get("campo5", "")))

def borrar_registro(coleccion, entrada_borrar):
    clave = entrada_borrar.get().strip()
    if not clave: return
    if not messagebox.askyesno("Confirmar", "¿Segura de borrar este registro?"): return
    for doc in db.collection(coleccion).stream():
        d = doc.to_dict()
        if d["id"] == clave or d["nombre"].lower() == clave.lower():
            db.collection(coleccion).document(doc.id).delete()
            messagebox.showinfo("OK", "Registro eliminado")
            return
    messagebox.showerror("Error", "No encontrado")

def buscar_modificar(coleccion):
    global doc_actual, imagen_actual
    clave = entrada_id.get().strip()
    if not clave:
        messagebox.showwarning("Atención", "Escribe el ID en el primer campo")
        return
    for doc in db.collection(coleccion).stream():
        d = doc.to_dict()
        if d["id"] == clave or d["nombre"].lower() == clave.lower():
            doc_actual = doc.id
            imagen_actual = d.get("imagen", "")
            entrada_id.delete(0, tk.END)
            entrada_id.insert(0, d["id"])
            entrada_nombre.delete(0, tk.END)
            entrada_nombre.insert(0, d["nombre"])
            entrada_campo3.delete(0, tk.END)
            entrada_campo3.insert(0, d["campo3"])
            entrada_campo4.delete(0, tk.END)
            entrada_campo4.insert(0, d["campo4"])
            entrada_campo5.delete(0, tk.END)
            entrada_campo5.insert(0, d["campo5"])
            messagebox.showinfo("OK", "Registro cargado para modificar")
            return
    messagebox.showerror("Error", "No encontrado")

def actualizar_registro(coleccion):
    global doc_actual, imagen_actual, ruta_imagen
    if not doc_actual:
        messagebox.showwarning("Atención", "Primero busca un registro")
        return
    mat = entrada_id.get().strip()
    nom = entrada_nombre.get().strip()
    esp = entrada_campo3.get().strip()
    prom = entrada_campo4.get().strip()
    horas = entrada_campo5.get().strip()
    if not all([mat, nom, esp, prom, horas]):
        messagebox.showwarning("Atención", "Faltan datos")
        return
    ruta_final = imagen_actual
    if ruta_imagen:
        nombre_img = f"{mat}_{os.path.basename(ruta_imagen)}"
        ruta_final = os.path.join(IMAGES_DIR, nombre_img)
        shutil.copy(ruta_imagen, ruta_final)
    db.collection(coleccion).document(doc_actual).update({
        "id": mat, "nombre": nom, "campo3": esp, "campo4": prom, "campo5": horas, "imagen": ruta_final
    })
    messagebox.showinfo("Éxito", "Registro modificado")
    limpiar_campos()

# ---------------- 8. LOGIN ----------------
def login():
    global sesion_iniciada
    limpiar_contenido()
    tk.Label(contenedor, text="Iniciar Sesión", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=30)
    form = tk.Frame(contenedor, bg=CREMA)
    form.pack()

    tk.Label(form, text="Usuario:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(anchor="w", pady=10)
    entry_user = tk.Entry(form, width=30, font=(FONT, 12))
    entry_user.pack(pady=5)

    tk.Label(form, text="Contraseña:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(anchor="w", pady=10)
    entry_pass = tk.Entry(form, width=30, font=(FONT, 12), show="*")
    entry_pass.pack(pady=5)

    def validar_login():
        global sesion_iniciada
        if entry_user.get() == "Michelle" and entry_pass.get() == "110425":
            sesion_iniciada = True
            messagebox.showinfo("Bienvenida", "Acceso correcto")
            cargar_menu_completo()
            conoce()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    tk.Button(form, text="Entrar", bg=ESPRESSO, fg=BLANCO, font=(FONT, 12, "bold"),
              width=15, command=validar_login).pack(pady=30)

# ---------------- 9. PÁGINA 3: CONOCE NEKOCOFFE ----------------
def conoce():
    limpiar_contenido()
    canvas = tk.Canvas(contenedor, bg=CREMA, highlightthickness=0)
    scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=CREMA)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    tk.Label(scroll_frame, text="Conoce Nekocoffe", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)

    tk.Label(scroll_frame, text="Misión", bg=CREMA, fg=LATTE, font=(FONT, 14, "bold")).pack(pady=(15,5))
    mision = "Crear un espacio único donde el amor por el café artesanal se combine con la protección animal. Buscamos que cada cliente disfrute una experiencia sensorial mientras ayuda a nuestros michis rescatados a encontrar un hogar."
    tk.Label(scroll_frame, text=mision, bg=CREMA, fg=ESPRESSO, font=(FONT, 11), wraplength=800, justify="center").pack(padx=40)

    tk.Label(scroll_frame, text="Visión", bg=CREMA, fg=LATTE, font=(FONT, 14, "bold")).pack(pady=(20,5))
    vision = "Ser la cafetería de gatos referente en México, reconocida por nuestro impacto social y la calidad de nuestros productos. Queremos expandir el modelo a más ciudades para que más michis encuentren su familia."
    tk.Label(scroll_frame, text=vision, bg=CREMA, fg=ESPRESSO, font=(FONT, 11), wraplength=800, justify="center").pack(padx=40)

    tk.Label(scroll_frame, text="Valores", bg=CREMA, fg=LATTE, font=(FONT, 14, "bold")).pack(pady=(20,5))
    valores = """• Amor y respeto animal: Cada michi es familia
- Calidad artesanal: Café de especialidad en cada taza
- Compromiso social: 10% de ganancias va a refugios
- Sustentabilidad: Empaques compostables y café de comercio justo
- Comunidad: Creamos lazos entre humanos y gatos"""
    tk.Label(scroll_frame, text=valores, bg=CREMA, fg=ESPRESSO, font=(FONT, 11), justify="left").pack(padx=40)

    tk.Label(scroll_frame, text="\nHorarios", bg=CREMA, fg=LATTE, font=(FONT, 14, "bold")).pack(pady=(20,5))
    tk.Label(scroll_frame, text="Lunes a Domingo: 8:00 AM - 9:00 PM\nTodos nuestros gatos están vacunados y esterilizados",
             bg=CREMA, fg=ESPRESSO, font=(FONT, 11), justify="center").pack()

    frame = tk.Frame(scroll_frame, bg=CREMA)
    frame.pack(pady=20)
    tk.Label(frame, text="¿Quieres adoptar?", bg=CREMA, fg=ESPRESSO, font=(FONT, 14, "bold")).pack(pady=10)
    tk.Label(frame, text="Déjanos tu correo:", bg=CREMA, fg=ESPRESSO).pack()
    entry_lead = tk.Entry(frame, width=40)
    entry_lead.pack(pady=5)
    def enviar_lead():
        if entry_lead.get():
            messagebox.showinfo("Gracias", "Te contactaremos pronto para el proceso de adopción")
            entry_lead.delete(0, tk.END)
    tk.Button(frame, text="Enviar", bg=LATTE, fg=BLANCO, command=enviar_lead).pack(pady=5)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

# ---------------- 10. PÁGINA 1: REGISTRO ----------------
def abrir_registro():
    global ruta_imagen, imagen_preview, tabla_usuarios
    ruta_imagen = ""
    tk.Label(contenedor, text="Registro de Usuarios", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    form = tk.Frame(contenedor, bg=CREMA)
    form.pack()
    campos = {}
    labels = ["Nombre completo", "Correo electrónico", "Contraseña", "Confirmar contraseña", "Número de teléfono"]
    for texto in labels:
        tk.Label(form, text=texto, bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(anchor="w", pady=5)
        entry = tk.Entry(form, width=40, font=(FONT, 11), show="*" if "Contraseña" in texto else "")
        entry.pack(pady=5)
        campos[texto] = entry
    imagen_preview = tk.Label(form, bg=CREMA, text="Sin foto")
    imagen_preview.pack(pady=5)
    def seleccionar_foto_usuario():
        global ruta_imagen
        ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        if ruta:
            ruta_imagen = ruta
            img = Image.open(ruta).resize((80, 80))
            img_tk = ImageTk.PhotoImage(img)
            imagen_preview.config(image=img_tk, text="")
            imagen_preview.image = img_tk
    tk.Button(form, text="Seleccionar foto", bg=LATTE, fg=BLANCO, command=seleccionar_foto_usuario).pack(pady=10)
    aceptar = tk.BooleanVar()
    tk.Checkbutton(form, text="Acepto términos y aviso de privacidad", variable=aceptar, bg=CREMA, fg=ESPRESSO).pack(pady=10)
    def registrar():
        global ruta_imagen
        nombre = campos["Nombre completo"].get()
        email = campos["Correo electrónico"].get()
        password = campos["Contraseña"].get()
        confirm = campos["Confirmar contraseña"].get()
        telefono = campos["Número de teléfono"].get()
        if not all([nombre, email, password, telefono, ruta_imagen]):
            messagebox.showerror("Error", "Completa todos los campos y selecciona foto")
            return
        if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            messagebox.showerror("Error", "Contraseña: mín 8 caracteres, 1 mayúscula, 1 número")
            return
        if password!= confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        if not aceptar.get():
            messagebox.showerror("Error", "Debes aceptar términos")
            return
        try:
            nombre_img = f"{email}_{os.path.basename(ruta_imagen)}"
            ruta_destino = os.path.join(IMAGES_DIR, nombre_img)
            shutil.copy(ruta_imagen, ruta_destino)
            datos = {"nombre": nombre, "email": email, "telefono": telefono, "foto": ruta_destino, "fecha": datetime.now().strftime("%d/%m/%Y")}
            db.collection("usuarios").add(datos)
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")
            for e in campos.values(): e.delete(0, tk.END)
            imagen_preview.config(image="", text="Sin foto")
            ruta_imagen = ""
        except Exception as e:
            messagebox.showerror("Error", str(e))
    tk.Button(form, text="Registrarse", bg=ESPRESSO, fg=BLANCO, font=(FONT, 11, "bold"), command=registrar).pack(pady=20)
    def mostrar_tabla_usuarios():
        global imagenes_guardadas
        imagenes_guardadas.clear()
        for item in tabla_usuarios.get_children(): tabla_usuarios.delete(item)
        docs = db.collection("usuarios").stream()
        for doc in docs:
            d = doc.to_dict()
            img_tk = None
            try:
                img = Image.open(d["foto"]).resize((65, 65))
                img_tk = ImageTk.PhotoImage(img)
                imagenes_guardadas.append(img_tk)
            except: pass
            tabla_usuarios.insert("", "end", text="", image=img_tk if img_tk else "",
                values=(d.get("nombre", ""), d.get("email", ""), d.get("telefono", ""), d.get("fecha", "")))
    tk.Button(contenedor, text="Mostrar tabla", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), command=mostrar_tabla_usuarios).pack(pady=10)
    tabla_usuarios, _ = crear_tabla_con_scroll(contenedor, ("Nombre", "Email", "Telefono", "Fecha"))

# ---------------- 11. PÁGINA 2: MODIFICACIÓN PERFIL ----------------
def modificar_perfil():
    global ruta_imagen, doc_actual, imagen_actual, imagen_preview, tabla_perfil
    global entrada_id, entrada_nombre, entrada_campo3, entrada_campo4, entrada_campo5
    ruta_imagen = ""
    doc_actual = None
    tk.Label(contenedor, text="Modificación del Perfil", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack()
    tk.Label(frame, text="Email (ID)", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_id = tk.Entry(frame, width=40)
    entrada_id.pack(pady=5)
    tk.Label(frame, text="Nombre completo", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_nombre = tk.Entry(frame, width=40)
    entrada_nombre.pack(pady=5)
    tk.Label(frame, text="Dirección", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_campo3 = tk.Entry(frame, width=40)
    entrada_campo3.pack(pady=5)
    tk.Label(frame, text="Fecha nacimiento DD/MM/YYYY", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_campo4 = tk.Entry(frame, width=40)
    entrada_campo4.pack(pady=5)
    tk.Label(frame, text="Alergias", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_campo5 = tk.Entry(frame, width=40)
    entrada_campo5.pack(pady=5)
    imagen_preview = tk.Label(frame, bg=CREMA, text="Sin foto")
    imagen_preview.pack(pady=5)
    tk.Button(frame, text="Seleccionar nueva foto", bg=LATTE, fg=BLANCO, command=seleccionar_imagen).pack(pady=5)
    frame_btns = tk.Frame(contenedor, bg=CREMA)
    frame_btns.pack(pady=10)
    tk.Button(frame_btns, text="Guardar", bg=ESPRESSO, fg=BLANCO, command=lambda: guardar_registro("perfiles")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Buscar para modificar", bg=LATTE, fg=BLANCO, command=lambda: buscar_modificar("perfiles")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Actualizar", bg=ESPRESSO, fg=BLANCO, command=lambda: actualizar_registro("perfiles")).pack(side="left", padx=5)
    frame_borrar = tk.Frame(contenedor, bg=CREMA)
    frame_borrar.pack(pady=5)
    tk.Label(frame_borrar, text="Email a borrar:", bg=CREMA).pack(side="left")
    entrada_borrar = tk.Entry(frame_borrar, width=30)
    entrada_borrar.pack(side="left", padx=5)
    tk.Button(frame_borrar, text="Borrar", bg="red", fg=BLANCO, command=lambda: borrar_registro("perfiles", entrada_borrar)).pack(side="left")
    tk.Button(contenedor, text="Mostrar tabla", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), command=lambda: mostrar_datos("perfiles")).pack(pady=10)
    tabla_perfil, _ = crear_tabla_con_scroll(contenedor, ("Email", "Nombre", "Dirección", "Fecha Nac", "Alergias"))

# ---------------- 12. PÁGINA 4: CONTACTO ----------------
def contacto():
    global tabla_contacto, imagen_preview, ruta_imagen
    ruta_imagen = ""
    tk.Label(contenedor, text="Contacto", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    form = tk.Frame(contenedor, bg=CREMA)
    form.pack()
    tk.Label(form, text="Nombre", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entry_nombre = tk.Entry(form, width=40)
    entry_nombre.pack(pady=5)
    tk.Label(form, text="Correo", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entry_correo = tk.Entry(form, width=40)
    entry_correo.pack(pady=5)
    tk.Label(form, text="Teléfono", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entry_tel = tk.Entry(form, width=40)
    entry_tel.pack(pady=5)
    tk.Label(form, text="Asunto: Reserva/Adopción/Queja/Otro", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entry_asunto = tk.Entry(form, width=40)
    entry_asunto.pack(pady=5)
    tk.Label(form, text="Mensaje", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entry_msg = tk.Text(form, width=40, height=4)
    entry_msg.pack(pady=5)
    imagen_preview = tk.Label(form, bg=CREMA, text="Sin foto")
    imagen_preview.pack(pady=5)
    def enviar_contacto():
        global ruta_imagen
        if not all([entry_nombre.get(), entry_correo.get(), entry_asunto.get(), ruta_imagen]):
            messagebox.showerror("Error", "Nombre, correo, asunto y foto son obligatorios")
            return
        try:
            nombre_img = f"contacto_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(ruta_imagen)}"
            ruta_destino = os.path.join(IMAGES_DIR, nombre_img)
            shutil.copy(ruta_imagen, ruta_destino)
            datos = {"nombre": entry_nombre.get(), "correo": entry_correo.get(), "telefono": entry_tel.get(),
                    "asunto": entry_asunto.get(), "mensaje": entry_msg.get("1.0", "end"), "foto": ruta_destino}
            db.collection("contactos").add(datos)
            messagebox.showinfo("Éxito", "Mensaje enviado")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    tk.Button(form, text="Seleccionar foto", bg=LATTE, fg=BLANCO, command=seleccionar_imagen).pack(pady=5)
    tk.Button(form, text="Enviar", bg=ESPRESSO, fg=BLANCO, command=enviar_contacto).pack(pady=10)
    def mostrar_tabla_contacto():
        global imagenes_guardadas
        imagenes_guardadas.clear()
        for item in tabla_contacto.get_children(): tabla_contacto.delete(item)
        docs = db.collection("contactos").stream()
        for doc in docs:
            d = doc.to_dict()
            img_tk = None
            try:
                img = Image.open(d["foto"]).resize((65, 65))
                img_tk = ImageTk.PhotoImage(img)
                imagenes_guardadas.append(img_tk)
            except: pass
            tabla_contacto.insert("", "end", text="", image=img_tk if img_tk else "",
                values=(d.get("nombre", ""), d.get("correo", ""), d.get("telefono", ""), d.get("asunto", ""), d.get("mensaje", "")[:30]))
    tk.Button(contenedor, text="Mostrar tabla", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), command=mostrar_tabla_contacto).pack(pady=10)
    tabla_contacto, _ = crear_tabla_con_scroll(contenedor, ("Nombre", "Correo", "Teléfono", "Asunto", "Mensaje"))

# ---------------- 13. PÁGINA 5: FILTRO DE MENÚ ----------------
def filtro_menu():
    tk.Label(contenedor, text="Filtro de Menú", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack(pady=20)
    tk.Label(frame, text="Tipo de bebida:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(anchor="w", pady=10)
    tipo = tk.StringVar(value="Todas")
    for t in ["Todas", "Bebida caliente", "Bebida fría", "Postre"]:
        tk.Radiobutton(frame, text=t, variable=tipo, value=t, bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    tk.Label(frame, text="\nRestricciones:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(anchor="w", pady=10)
    sin_cafeina = tk.BooleanVar()
    sin_lactosa = tk.BooleanVar()
    sin_gluten = tk.BooleanVar()
    vegano = tk.BooleanVar()
    tk.Checkbutton(frame, text="Sin cafeína", variable=sin_cafeina, bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    tk.Checkbutton(frame, text="Sin lactosa", variable=sin_lactosa, bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    tk.Checkbutton(frame, text="Sin gluten", variable=sin_gluten, bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    tk.Checkbutton(frame, text="Vegano", variable=vegano, bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    tk.Label(frame, text="\nRango de precio:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(anchor="w", pady=10)
    tk.Scale(frame, from_=50, to=200, orient="horizontal", bg=CREMA, fg=ESPRESSO, highlightthickness=0).pack()
    tk.Button(frame, text="Aplicar Filtros", bg=ESPRESSO, fg=BLANCO, font=(FONT, 11, "bold")).pack(pady=20)

# ---------------- 14. PÁGINA 6: RESERVACIÓN ----------------
def reservacion():
    global ruta_imagen, doc_actual, imagen_actual, imagen_preview, tabla_reserva
    global entrada_id, entrada_nombre, entrada_campo3, entrada_campo4, entrada_campo5
    ruta_imagen = ""
    doc_actual = None
    tk.Label(contenedor, text="Reservación de Mesa", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack()
    tk.Label(frame, text="ID Reserva", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_id = tk.Entry(frame, width=40)
    entrada_id.pack(pady=5)
    tk.Label(frame, text="Nombre", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_nombre = tk.Entry(frame, width=40)
    entrada_nombre.pack(pady=5)
    tk.Label(frame, text="Fecha DD/MM/YYYY", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_campo3 = tk.Entry(frame, width=40)
    entrada_campo3.pack(pady=5)
    tk.Label(frame, text="Hora HH:MM", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_campo4 = tk.Entry(frame, width=40)
    entrada_campo4.pack(pady=5)
    tk.Label(frame, text="Zona: General/Con gatos", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_campo5 = tk.Entry(frame, width=40)
    entrada_campo5.pack(pady=5)
    imagen_preview = tk.Label(frame, bg=CREMA, text="Sin foto")
    imagen_preview.pack(pady=5)
    tk.Button(frame, text="Seleccionar foto", bg=LATTE, fg=BLANCO, command=seleccionar_imagen).pack(pady=5)
    frame_btns = tk.Frame(contenedor, bg=CREMA)
    frame_btns.pack(pady=10)
    tk.Button(frame_btns, text="Guardar", bg=ESPRESSO, fg=BLANCO, command=lambda: guardar_registro("reservas")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Buscar", bg=LATTE, fg=BLANCO, command=lambda: buscar_modificar("reservas")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Actualizar", bg=ESPRESSO, fg=BLANCO, command=lambda: actualizar_registro("reservas")).pack(side="left", padx=5)
    tk.Button(contenedor, text="Mostrar tabla", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), command=lambda: mostrar_datos("reservas")).pack(pady=10)
    tabla_reserva, _ = crear_tabla_con_scroll(contenedor, ("ID", "Nombre", "Fecha", "Hora", "Zona"))

# ---------------- 15. PÁGINA 7: PERFILES MICHIS ----------------
def perfiles_michis():
    tk.Label(contenedor, text="Perfiles de Michis", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack(pady=20)
    michis = [
        {"nombre": "Moka", "edad": "2 años", "personalidad": "Juguetón y cariñoso"},
        {"nombre": "Latte", "edad": "1 año", "personalidad": "Tranquilo y dormilón"},
        {"nombre": "Espresso", "edad": "3 años", "personalidad": "Independiente"}
    ]
    for michi in michis:
        card = tk.Frame(frame, bg=BLANCO, bd=2, relief="ridge")
        card.pack(pady=10, padx=20, fill="x")
        tk.Label(card, text=michi["nombre"], bg=BLANCO, fg=ESPRESSO, font=(FONT, 14, "bold")).pack(pady=5)
        tk.Label(card, text=f"Edad: {michi['edad']}", bg=BLANCO, fg=ESPRESSO).pack()
        tk.Label(card, text=michi["personalidad"], bg=BLANCO, fg=LATTE).pack(pady=5)
        tk.Button(card, text=f"Me interesa adoptar a {michi['nombre']}", bg=LATTE, fg=BLANCO).pack(pady=5)

# ---------------- 16. PÁGINA 8: NORMAS ----------------
def normas():
    tk.Label(contenedor, text="Normas de Convivencia", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    frame = tk.Frame(contenedor, bg=BLANCO, bd=2, relief="ridge")
    frame.pack(pady=20, padx=50, fill="both", expand=True)
    normas_texto = """1. No levantar ni perseguir a los gatos. Ellos se acercarán si quieren.
2. Lávate las manos antes y después de interactuar con los michis.
3. No darles comida humana. Solo el personal puede alimentarlos.
4. Los niños menores de 12 años deben estar supervisados en todo momento.
5. Si un gato está durmiendo, no lo despiertes.
6. No usar flash al tomar fotos.
7. Mantén un volumen de voz moderado para no estresarlos.
8. El tiempo máximo en zona de gatos es de 90 minutos."""
    tk.Label(frame, text=normas_texto, bg=BLANCO, fg=ESPRESSO, font=(FONT, 11), justify="left").pack(pady=20, padx=20)
    check = tk.BooleanVar()
    tk.Checkbutton(contenedor, text="He leído y acepto las normas de convivencia", variable=check, bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=20)

# ---------------- 17. PÁGINA 9: PEDIDO ONLINE ----------------
def pedido_online():
    global ruta_imagen, doc_actual, imagen_actual, imagen_preview, tabla_pedido
    global entrada_id, entrada_nombre, entrada_campo3, entrada_campo4, entrada_campo5
    ruta_imagen = ""
    doc_actual = None
    tk.Label(contenedor, text="Pedido y Pago Online", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack()
    tk.Label(frame, text="ID Cliente", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_id = tk.Entry(frame, width=40)
    entrada_id.pack(pady=5)
    tk.Label(frame, text="Nombre", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_nombre = tk.Entry(frame, width=40)
    entrada_nombre.pack(pady=5)
    tk.Label(frame, text="Productos", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_campo3 = tk.Entry(frame, width=40)
    entrada_campo3.pack(pady=5)
    tk.Label(frame, text="Cantidad", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_campo4 = tk.Entry(frame, width=40)
    entrada_campo4.pack(pady=5)
    tk.Label(frame, text="Método Pago: Tarjeta/Transferencia/Efectivo", bg=CREMA, fg=ESPRESSO).pack(anchor="w")
    entrada_campo5 = tk.Entry(frame, width=40)
    entrada_campo5.pack(pady=5)
    imagen_preview = tk.Label(frame, bg=CREMA, text="Sin foto")
    imagen_preview.pack(pady=5)
    tk.Button(frame, text="Seleccionar foto", bg=LATTE, fg=BLANCO, command=seleccionar_imagen).pack(pady=5)
    frame_btns = tk.Frame(contenedor, bg=CREMA)
    frame_btns.pack(pady=10)
    tk.Button(frame_btns, text="Guardar", bg=ESPRESSO, fg=BLANCO, command=lambda: guardar_registro("pedidos")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Buscar", bg=LATTE, fg=BLANCO, command=lambda: buscar_modificar("pedidos")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Actualizar", bg=ESPRESSO, fg=BLANCO, command=lambda: actualizar_registro("pedidos")).pack(side="left", padx=5)
    tk.Button(contenedor, text="Mostrar tabla", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), command=lambda: mostrar_datos("pedidos")).pack(pady=10)
    tabla_pedido, _ = crear_tabla_con_scroll(contenedor, ("ID", "Nombre", "Productos", "Cantidad", "Pago"))

# ---------------- 18. PÁGINA 10: MICHILOVERS ----------------
def michilovers():
    tk.Label(contenedor, text="Programa MichiLovers", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    frame = tk.Frame(contenedor, bg=BLANCO, bd=2, relief="ridge")
    frame.pack(pady=20, padx=50, fill="x")
    texto = """1 punto = $10 gastados\nPuntos vencen en 6 meses\n\nRecompensas:\n100 puntos = Café gratis\n200 puntos = Postre gratis\n500 puntos = Desayuno para 2\n1000 puntos = Kit MichiLover"""
    tk.Label(frame, text=texto, bg=BLANCO, fg=ESPRESSO, font=(FONT, 12), justify="left").pack(pady=20, padx=20)
    tk.Label(contenedor, text="Ingresa tu email para consultar puntos:", bg=CREMA, fg=ESPRESSO).pack(pady=10)
    entry_email = tk.Entry(contenedor, width=40)
    entry_email.pack()
    tk.Button(contenedor, text="Consultar", bg=LATTE, fg=BLANCO).pack(pady=10)

# ---------------- 19. CARGAR MENÚ SEGÚN SESIÓN ----------------
def cargar_menu_inicial():
    for widget in menu_lateral.winfo_children():
        widget.destroy()
    tk.Button(menu_lateral, text="Login", bg=ESPRESSO, fg=BLANCO,
              font=(FONT, 11), bd=0, anchor="w", padx=15,
              command=lambda: [login(), menu_lateral.place_forget()]).pack(fill="x", pady=2, padx=10)
    tk.Button(menu_lateral, text="Conoce Nekocoffe", bg=ESPRESSO, fg=BLANCO,
              font=(FONT, 11), bd=0, anchor="w", padx=15,
              command=lambda: [conoce(), menu_lateral.place_forget()]).pack(fill="x", pady=2, padx=10)

def cargar_menu_completo():
    for widget in menu_lateral.winfo_children():
        widget.destroy()
    botones = [
        ("1. Registro/Login", abrir_registro),
        ("2. Modificación del perfil", modificar_perfil),
        ("3. Conoce Nekocoffe", conoce),
        ("4. Contacto", contacto),
        ("5. Filtro de menú", filtro_menu),
        ("6. Reservación de mesa", reservacion),
        ("7. Perfiles de Michis", perfiles_michis),
        ("8. Normas de convivencia", normas),
        ("9. Pedido y pago online", pedido_online),
        ("10. Programa MichiLovers", michilovers)
    ]
    for texto, comando in botones:
        tk.Button(menu_lateral, text=texto, bg=ESPRESSO, fg=BLANCO,
                  font=(FONT, 11), bd=0, anchor="w", padx=15,
                  command=lambda c=comando: [c(), menu_lateral.place_forget()]).pack(fill="x", pady=2, padx=10)

# ---------------- 20. APLICAR SCROLL A PÁGINAS ----------------
abrir_registro = hacer_scrollable(abrir_registro)
modificar_perfil = hacer_scrollable(modificar_perfil)
contacto = hacer_scrollable(contacto)
filtro_menu = hacer_scrollable(filtro_menu)
reservacion = hacer_scrollable(reservacion)
perfiles_michis = hacer_scrollable(perfiles_michis)
normas = hacer_scrollable(normas)
pedido_online = hacer_scrollable(pedido_online)
michilovers = hacer_scrollable(michilovers)

# ---------------- 21. FOOTER ----------------
footer = tk.Frame(main_container, bg=ESPRESSO, height=45)
footer.pack(side="bottom", fill="x")
footer.pack_propagate(False)
tk.Label(footer, text="Nekocoffe © 2026 | Siete vidas, un mismo hogar",
         bg=ESPRESSO, fg=CREMA, font=(FONT, 8)).pack(expand=True)

# ---------------- 22. INICIO ----------------
cargar_menu_inicial()
conoce()
root.mainloop()