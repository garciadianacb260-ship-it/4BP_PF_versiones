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
imagenes_michis_catalogo = []
imagenes_menu = []
imagenes_michilovers = []
sesion_iniciada = False
carrito_global = []

USUARIO_LOGIN = "Michelle"
PASS_LOGIN = "110425"
ULTIMA_MODIFICACION = "15/05/2026 10:30"
INTENTOS_LOGIN = 0

entrada_id = entrada_nombre = entrada_campo3 = entrada_campo4 = entrada_campo5 = None
imagen_preview = None
tabla_perfil = tabla_reserva = tabla_pedido = tabla_usuarios = tabla_contacto = tabla_menu = None

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
menu_lateral = tk.Frame(main_container, bg=ESPRESSO, width=270)

# ---------------- 6. CONTENEDOR ----------------
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
    
    style = ttk.Style()
    style.configure("Treeview", rowheight=80)
    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="tree headings", yscrollcommand=scroll_y.set, height=6)
    tabla.heading("#0", text="Foto")
    tabla.column("#0", width=110, anchor="center", minwidth=110)
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=130, anchor="center")
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
        canvas_window = canvas.create_window((600, 0), window=scroll_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        contenedor_original = contenedor
        globals()['contenedor'] = scroll_frame
        funcion_original()
        globals()['contenedor'] = contenedor_original

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)
    return wrapper

def validar_email(event, entry):
    email = entry.get()
    if "@" in email and "." in email:
        entry.config(bg="#CCFFCC")
    else:
        entry.config(bg="#FFCCCC") if email else entry.config(bg=BLANCO)

def crear_boton_menu(parent, texto, comando):
    btn = tk.Button(parent, text=texto, bg=ESPRESSO, fg=BLANCO, font=(FONT, 11), 
                    bd=0, anchor="w", padx=20, pady=8, command=comando, cursor="hand2")
    def on_enter(e): btn.config(bg=LATTE)
    def on_leave(e): btn.config(bg=ESPRESSO)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    btn.pack(fill="x", pady=2)
    return btn

def ir_a_pedido_con_carrito():
    if not carrito_global:
        messagebox.showwarning("Carrito vacío", "Agrega productos primero")
        return
    pedido()

# ---------------- 7. FUNCIONES CRUD - TABLA PEDIDOS ARREGLADA ----------------
def seleccionar_imagen():
    global ruta_imagen
    ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp")])
    if ruta:
        ruta_imagen = ruta
        img = Image.open(ruta).resize((100, 100))
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
        if coleccion == "usuarios":
            datos["fecha"] = datetime.now().strftime("%d/%m/%Y")
            datos["puntos"] = 0
        if coleccion == "perfiles":
            datos["fecha_registro"] = datetime.now().strftime("%d/%m/%Y")
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
    tabla = tabla_perfil if coleccion == "perfiles" else tabla_reserva if coleccion == "reservas" else tabla_pedido if coleccion == "pedidos" else tabla_contacto if coleccion == "contactos" else tabla_usuarios
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
            img = Image.open(d.get("imagen", "")).resize((75, 75))
            img_tk = ImageTk.PhotoImage(img)
            imagenes_guardadas.append(img_tk)
        except: pass
        
        if coleccion == "pedidos":
            productos_str = ", ".join([f"{p['nombre']} x{p['cantidad']}" for p in d.get('productos', [])]) if d.get('productos') else d.get("nombre", "")
            tabla.insert("", "end", text="", image=img_tk if img_tk else "",
                        values=(d.get("id", ""), d.get("nombre", ""), d.get("campo3", ""), productos_str[:30], d.get("campo5", "")))
        elif coleccion == "contactos":
            tabla.insert("", "end", text="", image=img_tk if img_tk else "",
                        values=(d.get("nombre", ""), d.get("correo", ""), d.get("telefono", ""), d.get("asunto", ""), d.get("mensaje", "")[:30]))
        elif coleccion == "usuarios":
            tabla.insert("", "end", text="", image=img_tk if img_tk else "",
                        values=(d.get("nombre", ""), d.get("email", ""), d.get("telefono", ""), d.get("fecha", ""), d.get("puntos", 0)))
        else:
            tabla.insert("", "end", text="", image=img_tk if img_tk else "",
                        values=(d.get("id", ""), d.get("nombre", ""), d.get("campo3", ""), d.get("campo4", ""), d.get("campo5", "")))

def borrar_registro(coleccion, entrada_borrar):
    clave = entrada_borrar.get().strip()
    if not clave:
        messagebox.showwarning("Atención", "Escribe el ID a borrar")
        return
    if not messagebox.askyesno("Confirmar", f"¿Segura de borrar '{clave}'?"): 
        return
    
    encontrado = False
    for doc in db.collection(coleccion).stream():
        d = doc.to_dict()
        if (d.get("id") == clave or d.get("email") == clave or d.get("nombre", "").lower() == clave.lower() or doc.id == clave):
            db.collection(coleccion).document(doc.id).delete()
            messagebox.showinfo("OK", "Registro eliminado")
            entrada_borrar.delete(0, tk.END)
            encontrado = True
            break
    if not encontrado:
        messagebox.showerror("Error", f"No se encontró '{clave}'")

def buscar_modificar(coleccion):
    global doc_actual, imagen_actual
    clave = entrada_id.get().strip()
    if not clave:
        messagebox.showwarning("Atención", "Escribe el ID en el primer campo")
        return
    for doc in db.collection(coleccion).stream():
        d = doc.to_dict()
        if d["id"] == clave or d.get("nombre", "").lower() == clave.lower() or d.get("email") == clave:
            doc_actual = doc.id
            imagen_actual = d.get("imagen", "")
            entrada_id.delete(0, tk.END)
            entrada_id.insert(0, d.get("id", d.get("email", "")))
            entrada_nombre.delete(0, tk.END)
            entrada_nombre.insert(0, d["nombre"])
            entrada_campo3.delete(0, tk.END)
            entrada_campo3.insert(0, d["campo3"])
            entrada_campo4.delete(0, tk.END)
            entrada_campo4.insert(0, d["campo4"])
            entrada_campo5.delete(0, tk.END)
            entrada_campo5.insert(0, d["campo5"])
            try:
                img = Image.open(d["imagen"]).resize((100, 100))
                img_tk = ImageTk.PhotoImage(img)
                imagen_preview.config(image=img_tk, text="")
                imagen_preview.image = img_tk
            except: pass
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

# ---------------- 8. CONOCE NEKOCOFFE ----------------
@hacer_scrollable
def conoce():
    michis_count = len(list(db.collection("perfiles").stream()))

    tk.Label(contenedor, text="Bienvenido a Nekocoffe", bg=CREMA, fg=ESPRESSO, font=(FONT, 20, "bold")).pack(pady=20)
    tk.Label(contenedor, text=f"15 michis han encontrado hogar ❤️ | {michis_count} disponibles ahora",
             bg=CREMA, fg=LATTE, font=(FONT, 11, "italic")).pack(pady=5)

    tk.Label(contenedor, text="Misión", bg=CREMA, fg=LATTE, font=(FONT, 14, "bold")).pack(pady=(15,5))
    mision = "Crear un espacio único donde el amor por el café artesanal se combine con la protección animal. Buscamos que cada cliente disfrute una experiencia sensorial mientras ayuda a nuestros michis rescatados a encontrar un hogar."
    tk.Label(contenedor, text=mision, bg=CREMA, fg=ESPRESSO, font=(FONT, 11), wraplength=800, justify="center").pack(padx=40)

    tk.Label(contenedor, text="Visión", bg=CREMA, fg=LATTE, font=(FONT, 14, "bold")).pack(pady=(20,5))
    vision = "Ser la cafetería de gatos referente en México, reconocida por nuestro impacto social y la calidad de nuestros productos."
    tk.Label(contenedor, text=vision, bg=CREMA, fg=ESPRESSO, font=(FONT, 11), wraplength=800, justify="center").pack(padx=40)

    tk.Label(contenedor, text="Valores", bg=CREMA, fg=LATTE, font=(FONT, 14, "bold")).pack(pady=(20,5))
    valores = """• Amor y respeto animal: Cada michi es familia
- Calidad artesanal: Café de especialidad en cada taza
- Compromiso social: 10% de ganancias va a refugios
- Sustentabilidad: Empaques compostables"""
    tk.Label(contenedor, text=valores, bg=CREMA, fg=ESPRESSO, font=(FONT, 11), justify="center").pack(padx=40)

    tk.Label(contenedor, text="\nHorarios", bg=CREMA, fg=LATTE, font=(FONT, 14, "bold")).pack(pady=(20,5))
    tk.Label(contenedor, text="Lunes a Domingo: 8:00 AM - 9:00 PM\nTodos nuestros gatos están vacunados y esterilizados",
             bg=CREMA, fg=ESPRESSO, font=(FONT, 11), justify="center").pack()

# ---------------- 9. LOGIN ----------------
def login():
    global sesion_iniciada, INTENTOS_LOGIN
    limpiar_contenido()
    
    frame_centro = tk.Frame(contenedor, bg=CREMA)
    frame_centro.pack(expand=True)
    tk.Label(frame_centro, text="Iniciar Sesión Admin", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=30)
    form = tk.Frame(frame_centro, bg=CREMA)
    form.pack()

    tk.Label(form, text="Usuario:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(pady=10)
    entry_user = tk.Entry(form, width=30, font=(FONT, 12), justify="center")
    entry_user.pack(pady=5)

    tk.Label(form, text="Contraseña:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(pady=10)
    entry_pass = tk.Entry(form, width=30, font=(FONT, 12), show="*", justify="center")
    entry_pass.pack(pady=5)

    recordar = tk.BooleanVar()
    tk.Checkbutton(form, text="Recordar usuario", variable=recordar, bg=CREMA, fg=ESPRESSO).pack(pady=5)

    label_intentos = tk.Label(form, text=f"Intentos: {INTENTOS_LOGIN}/3", bg=CREMA, fg=LATTE, font=(FONT, 9))
    label_intentos.pack(pady=5)

    def validar_login(event=None):
        global sesion_iniciada, INTENTOS_LOGIN
        if INTENTOS_LOGIN >= 3:
            messagebox.showerror("Bloqueado", "Demasiados intentos fallidos")
            return
        if entry_user.get() == USUARIO_LOGIN and entry_pass.get() == PASS_LOGIN:
            sesion_iniciada = True
            INTENTOS_LOGIN = 0
            if recordar.get():
                with open("recordar.txt", "w") as f: f.write(entry_user.get())
            messagebox.showinfo("Bienvenida", "Acceso correcto")
            cargar_menu_completo()
            conoce()
        else:
            INTENTOS_LOGIN += 1
            label_intentos.config(text=f"Intentos: {INTENTOS_LOGIN}/3")
            messagebox.showerror("Error", f"Usuario o contraseña incorrectos. Te quedan {3-INTENTOS_LOGIN} intentos")

    entry_pass.bind('<Return>', validar_login)
    tk.Button(form, text="Entrar", bg=ESPRESSO, fg=BLANCO, font=(FONT, 12, "bold"),
              width=15, command=validar_login).pack(pady=30)

# ---------------- 10. REGISTRO USUARIOS ----------------
@hacer_scrollable
def abrir_registro():
    global ruta_imagen, imagen_preview, tabla_usuarios, doc_actual
    global entrada_id, entrada_nombre, entrada_campo3, entrada_campo4, entrada_campo5
    ruta_imagen = ""
    doc_actual = None

    tk.Label(contenedor, text="Registro de Usuarios - MichiLovers", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    form = tk.Frame(contenedor, bg=CREMA)
    form.pack()

    tk.Label(form, text="Email (será tu ID)", bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=5)
    entrada_id = tk.Entry(form, width=40, font=(FONT, 11), justify="center")
    entrada_id.bind('<KeyRelease>', lambda e: validar_email(e, entrada_id))
    entrada_id.pack(pady=5)

    tk.Label(form, text="Nombre completo", bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=5)
    entrada_nombre = tk.Entry(form, width=40, font=(FONT, 11), justify="center")
    entrada_nombre.pack(pady=5)

    tk.Label(form, text="Contraseña", bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=5)
    entrada_campo3 = tk.Entry(form, width=40, font=(FONT, 11), show="*", justify="center")
    entrada_campo3.pack(pady=5)

    tk.Label(form, text="Confirmar contraseña", bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=5)
    entrada_campo4 = tk.Entry(form, width=40, font=(FONT, 11), show="*", justify="center")
    entrada_campo4.pack(pady=5)

    tk.Label(form, text="Número de teléfono", bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=5)
    entrada_campo5 = tk.Entry(form, width=40, font=(FONT, 11), justify="center")
    entrada_campo5.pack(pady=5)

    imagen_preview = tk.Label(form, bg=CREMA, text="Sin foto")
    imagen_preview.pack(pady=5)

    def seleccionar_foto_usuario():
        global ruta_imagen
        ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        if ruta:
            ruta_imagen = ruta
            img = Image.open(ruta).resize((100, 100))
            img_tk = ImageTk.PhotoImage(img)
            imagen_preview.config(image=img_tk, text="")
            imagen_preview.image = img_tk

    tk.Button(form, text="Seleccionar foto", bg=LATTE, fg=BLANCO, command=seleccionar_foto_usuario).pack(pady=10)

    frame_puntos = tk.Frame(form, bg=CREMA)
    frame_puntos.pack(pady=10)
    tk.Label(frame_puntos, text="Al registrarte obtienes: 50 puntos MichiLover Bronce", bg=CREMA, fg=LATTE, font=(FONT, 10, "italic")).pack()
    canvas_barra = tk.Canvas(frame_puntos, width=300, height=20, bg=BLANCO, highlightthickness=1)
    canvas_barra.pack(pady=5)
    canvas_barra.create_rectangle(0, 0, 50, 20, fill=LATTE, outline="")
    tk.Label(frame_puntos, text="50/1000 puntos", bg=CREMA, fg=ESPRESSO).pack()

    def registrar_usuario():
        global ruta_imagen
        email = entrada_id.get().strip()
        nombre = entrada_nombre.get().strip()
        password = entrada_campo3.get().strip()
        confirm = entrada_campo4.get().strip()
        telefono = entrada_campo5.get().strip()

        if not all([email, nombre, password, telefono, ruta_imagen]):
            messagebox.showerror("Error", "Completa todos los campos y selecciona foto")
            return
        if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            messagebox.showerror("Error", "Contraseña: mín 8 caracteres, 1 mayúscula, 1 número")
            return
        if password!= confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return

        try:
            nombre_img = f"{email}_{os.path.basename(ruta_imagen)}"
            ruta_destino = os.path.join(IMAGES_DIR, nombre_img)
            shutil.copy(ruta_imagen, ruta_destino)
            datos = {
                "id": email, "nombre": nombre, "email": email, "telefono": telefono,
                "imagen": ruta_destino, "campo3": password, "campo4": telefono, "campo5": "Usuario",
                "fecha": datetime.now().strftime("%d/%m/%Y"), "puntos": 50
            }
            db.collection("usuarios").add(datos)
            messagebox.showinfo("Éxito", "Usuario registrado. ¡Ya eres MichiLover Bronce con 50 puntos!")
            limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    frame_btns = tk.Frame(contenedor, bg=CREMA)
    frame_btns.pack(pady=10)
    tk.Button(frame_btns, text="Registrar", bg=ESPRESSO, fg=BLANCO, command=registrar_usuario).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Buscar", bg=LATTE, fg=BLANCO, command=lambda: buscar_modificar("usuarios")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Actualizar", bg=ESPRESSO, fg=BLANCO, command=lambda: actualizar_registro("usuarios")).pack(side="left", padx=5)

    frame_borrar = tk.Frame(contenedor, bg=CREMA)
    frame_borrar.pack(pady=5)
    tk.Label(frame_borrar, text="Email a borrar:", bg=CREMA).pack(side="left")
    entrada_borrar = tk.Entry(frame_borrar, width=25, justify="center")
    entrada_borrar.pack(side="left", padx=5)
    tk.Button(frame_borrar, text="Borrar", bg="red", fg=BLANCO, command=lambda: borrar_registro("usuarios", entrada_borrar)).pack(side="left")

    def mostrar_tabla_usuarios():
        global imagenes_guardadas
        imagenes_guardadas.clear()
        for item in tabla_usuarios.get_children(): tabla_usuarios.delete(item)
        docs = db.collection("usuarios").stream()
        for doc in docs:
            d = doc.to_dict()
            img_tk = None
            try:
                img = Image.open(d.get("imagen", "")).resize((75, 75))
                img_tk = ImageTk.PhotoImage(img)
                imagenes_guardadas.append(img_tk)
            except: pass
            tabla_usuarios.insert("", "end", text="", image=img_tk if img_tk else "",
                values=(d.get("nombre", ""), d.get("email", ""), d.get("telefono", ""), d.get("fecha", ""), d.get("puntos", 0)))

    tk.Button(contenedor, text="Mostrar tabla", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), command=mostrar_tabla_usuarios).pack(pady=10)
    tabla_usuarios, _ = crear_tabla_con_scroll(contenedor, ("Nombre", "Email", "Telefono", "Fecha", "Puntos"))

# ---------------- 11. MODIFICAR CREDENCIALES ----------------
@hacer_scrollable
def modificar_perfil():
    global USUARIO_LOGIN, PASS_LOGIN, ULTIMA_MODIFICACION
    tk.Label(contenedor, text="Modificar Credenciales de Acceso", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    tk.Label(contenedor, text=f"Última modificación: {ULTIMA_MODIFICACION}", bg=CREMA, fg=LATTE, font=(FONT, 10, "italic")).pack(pady=5)
    form = tk.Frame(contenedor, bg=CREMA)
    form.pack(pady=20)

    tk.Label(form, text="Usuario actual:", bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=5)
    tk.Label(form, text=USUARIO_LOGIN, bg=BLANCO, fg=ESPRESSO, width=30, font=(FONT, 11)).pack(pady=5)

    tk.Label(form, text="Nuevo usuario:", bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=(15,5))
    entry_user = tk.Entry(form, width=30, font=(FONT, 11), justify="center")
    entry_user.insert(0, USUARIO_LOGIN)
    entry_user.pack(pady=5)

    tk.Label(form, text="Nueva contraseña:", bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=(15,5))
    entry_pass = tk.Entry(form, width=30, font=(FONT, 11), show="*", justify="center")
    entry_pass.pack(pady=5)

    label_fuerza = tk.Label(form, text="Fuerza: ", bg=CREMA, fg=ESPRESSO, font=(FONT, 9))
    label_fuerza.pack()

    def verificar_fuerza(event):
        pwd = entry_pass.get()
        if len(pwd) < 6: fuerza, color = "Débil", "red"
        elif len(pwd) < 10: fuerza, color = "Media", "orange"
        else: fuerza, color = "Fuerte", "green"
        label_fuerza.config(text=f"Fuerza: {fuerza}", fg=color)

    entry_pass.bind('<KeyRelease>', verificar_fuerza)

    tk.Label(form, text="Confirmar contraseña:", bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=(15,5))
    entry_confirm = tk.Entry(form, width=30, font=(FONT, 11), show="*", justify="center")
    entry_confirm.pack(pady=5)

    def actualizar_credenciales():
        global USUARIO_LOGIN, PASS_LOGIN, ULTIMA_MODIFICACION
        nuevo_user = entry_user.get().strip()
        nuevo_pass = entry_pass.get().strip()
        confirm = entry_confirm.get().strip()
        if not nuevo_user or not nuevo_pass:
            messagebox.showerror("Error", "Usuario y contraseña no pueden estar vacíos")
            return
        if nuevo_pass!= confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        if len(nuevo_pass) < 6:
            messagebox.showerror("Error", "La contraseña debe tener mínimo 6 caracteres")
            return
        USUARIO_LOGIN = nuevo_user
        PASS_LOGIN = nuevo_pass
        ULTIMA_MODIFICACION = datetime.now().strftime("%d/%m/%Y %H:%M")
        messagebox.showinfo("Éxito", f"Credenciales actualizadas\nUsuario: {USUARIO_LOGIN}")

    tk.Button(form, text="Actualizar Credenciales", bg=ESPRESSO, fg=BLANCO, font=(FONT, 11, "bold"),
              command=actualizar_credenciales).pack(pady=30)

# ---------------- 12. CONTACTO ----------------
@hacer_scrollable
def contacto():
    global tabla_contacto, imagen_preview, ruta_imagen, doc_actual
    global entrada_id, entrada_nombre, entrada_campo3, entrada_campo4, entrada_campo5
    ruta_imagen = ""
    doc_actual = None

    tk.Label(contenedor, text="Contacto", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    tk.Label(contenedor, text="Tiempo respuesta promedio: 24h", bg=CREMA, fg=LATTE, font=(FONT, 10, "italic")).pack(pady=5)
    form = tk.Frame(contenedor, bg=CREMA)
    form.pack()

    tk.Label(form, text="Correo (para buscar)", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_id = tk.Entry(form, width=40, justify="center")
    entrada_id.bind('<KeyRelease>', lambda e: validar_email(e, entrada_id))
    entrada_id.pack(pady=5)

    tk.Label(form, text="Nombre", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_nombre = tk.Entry(form, width=40, justify="center")
    entrada_nombre.pack(pady=5)

    tk.Label(form, text="Teléfono", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo3 = tk.Entry(form, width=40, justify="center")
    entrada_campo3.pack(pady=5)

    tk.Label(form, text="Asunto:", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    asunto_var = tk.StringVar(value="Otro")
    combo_asunto = ttk.Combobox(form, textvariable=asunto_var, values=["Reserva", "Adopción", "Queja", "Sugerencia", "Otro"],
                                 width=37, state="readonly")
    combo_asunto.pack(pady=5)
    entrada_campo4 = combo_asunto

    tk.Label(form, text="Mensaje", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo5 = tk.Entry(form, width=40, justify="center")
    entrada_campo5.pack(pady=5)

    imagen_preview = tk.Label(form, bg=CREMA, text="Sin foto")
    imagen_preview.pack(pady=5)
    tk.Button(form, text="Seleccionar foto", bg=LATTE, fg=BLANCO, command=seleccionar_imagen).pack(pady=5)

    def guardar_contacto():
        global ruta_imagen
        correo = entrada_id.get().strip()
        nom = entrada_nombre.get().strip()
        tel = entrada_campo3.get().strip()
        asunto = entrada_campo4.get().strip()
        msg = entrada_campo5.get().strip()

        if not all([correo, nom, asunto, ruta_imagen]):
            messagebox.showerror("Error", "Correo, nombre, asunto y foto son obligatorios")
            return
        try:
            nombre_img = f"contacto_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(ruta_imagen)}"
            ruta_destino = os.path.join(IMAGES_DIR, nombre_img)
            shutil.copy(ruta_imagen, ruta_destino)
            datos = {
                "id": correo, "nombre": nom, "correo": correo, "telefono": tel,
                "asunto": asunto, "mensaje": msg, "imagen": ruta_destino,
                "campo3": tel, "campo4": asunto, "campo5": msg[:30]
            }
            db.collection("contactos").add(datos)
            messagebox.showinfo("Éxito", "Mensaje enviado. Te responderemos en 24h")
            limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    frame_btns = tk.Frame(contenedor, bg=CREMA)
    frame_btns.pack(pady=10)
    tk.Button(frame_btns, text="Enviar", bg=ESPRESSO, fg=BLANCO, command=guardar_contacto).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Buscar", bg=LATTE, fg=BLANCO, command=lambda: buscar_modificar("contactos")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Actualizar", bg=ESPRESSO, fg=BLANCO, command=lambda: actualizar_registro("contactos")).pack(side="left", padx=5)

    frame_borrar = tk.Frame(contenedor, bg=CREMA)
    frame_borrar.pack(pady=5)
    tk.Label(frame_borrar, text="Correo a borrar:", bg=CREMA).pack(side="left")
    entrada_borrar = tk.Entry(frame_borrar, width=25, justify="center")
    entrada_borrar.pack(side="left", padx=5)
    tk.Button(frame_borrar, text="Borrar", bg="red", fg=BLANCO, command=lambda: borrar_registro("contactos", entrada_borrar)).pack(side="left")

    tk.Button(contenedor, text="Mostrar tabla", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), command=lambda: mostrar_datos("contactos")).pack(pady=10)
    tabla_contacto, _ = crear_tabla_con_scroll(contenedor, ("Nombre", "Correo", "Teléfono", "Asunto", "Mensaje"))

# ---------------- 13. MENÚ & PEDIDOS ----------------
@hacer_scrollable
def filtro_menu():
    global carrito_global, imagenes_menu
    imagenes_menu = []

    PRODUCTOS_FIJOS = [
        {"nombre": "Café Nekocoffe", "precio": 55, "tipo": "Bebida caliente",
         "descripcion": "Café de especialidad con granos mexicanos", "imagen": r"E:\Diana4B\cafe.png"},
        {"nombre": "Malteada Gatuna", "precio": 75, "tipo": "Bebida fría",
         "descripcion": "Malteada cremosa de vainilla con topping", "imagen": r"E:\Diana4B\malteada.jpg"},
        {"nombre": "Carlota de Limón", "precio": 65, "tipo": "Postre",
         "descripcion": "Postre frío tradicional con galletas", "imagen": r"E:\Diana4B\carlota.jpg"},
        {"nombre": "Mousse de Zarzamora", "precio": 70, "tipo": "Postre",
         "descripcion": "Mousse artesanal con frutos rojos", "imagen": r"E:\Diana4B\mousse_de_zarzamora.jpg"}
    ]

    tk.Label(contenedor, text="Menú Nekocoffe | Haz tu pedido online",
             bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=(0,5))
    tk.Label(contenedor, text="☕ Productos artesanales | 🚚 Entrega a domicilio",
             bg=CREMA, fg=LATTE, font=(FONT, 10, "italic")).pack(pady=(0,10))
    tk.Frame(contenedor, bg=LATTE, height=2).pack(fill="x", pady=(0,15))

    frame_filtros = tk.Frame(contenedor, bg=CREMA)
    frame_filtros.pack(pady=10, fill="x", padx=20)

    tk.Label(frame_filtros, text="Filtrar:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(side="left", padx=5)

    tipo = tk.StringVar(value="Todos")
    for t in ["Todos", "Bebida caliente", "Bebida fría", "Postre"]:
        tk.Radiobutton(frame_filtros, text=t, variable=tipo, value=t, bg=CREMA, fg=ESPRESSO).pack(side="left", padx=5)

    label_resultados = tk.Label(contenedor, text="", bg=CREMA, fg=LATTE, font=(FONT, 11, "italic"))
    label_resultados.pack(pady=5)

    frame_menu = tk.Frame(contenedor, bg=CREMA)
    frame_menu.pack(pady=10, fill="both", expand=True)

    frame_carrito = tk.Frame(contenedor, bg=LATTE, bd=2, relief="ridge")
    frame_carrito.pack(fill="x", pady=10, padx=20)

    tk.Label(frame_carrito, text="🛒 Tu Pedido", bg=LATTE, fg=ESPRESSO, font=(FONT, 14, "bold")).pack(pady=5)
    label_carrito = tk.Label(frame_carrito, text="Carrito vacío", bg=LATTE, fg=ESPRESSO, font=(FONT, 10))
    label_carrito.pack(pady=5)
    label_total = tk.Label(frame_carrito, text="Total: $0", bg=LATTE, fg=ESPRESSO, font=(FONT, 12, "bold"))
    label_total.pack(pady=5)

    def actualizar_carrito():
        if not carrito_global:
            label_carrito.config(text="Carrito vacío")
            label_total.config(text="Total: $0")
        else:
            items = ", ".join([f"{c['nombre']} x{c['cantidad']}" for c in carrito_global])
            total_precio = sum(c['precio'] * c['cantidad'] for c in carrito_global)
            label_carrito.config(text=items)
            label_total.config(text=f"Total: ${total_precio:.0f} | Ganarás {int(total_precio//10)} puntos")

    def agregar_carrito(producto):
        for item in carrito_global:
            if item['nombre'] == producto['nombre']:
                item['cantidad'] += 1
                actualizar_carrito()
                return
        carrito_global.append({"nombre": producto['nombre'], "precio": producto['precio'], "cantidad": 1})
        actualizar_carrito()
        messagebox.showinfo("Agregado", f"{producto['nombre']} agregado al carrito")

    def mostrar_menu():
        for widget in frame_menu.winfo_children():
            widget.destroy()
        imagenes_menu.clear()

        contador = 0
        row = 0
        col = 0

        for p in PRODUCTOS_FIJOS:
            if tipo.get()!= "Todos" and p['tipo']!= tipo.get(): continue

            card = tk.Frame(frame_menu, bg=BLANCO, bd=2, relief="ridge")
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            frame_menu.grid_columnconfigure(col, weight=1)

            try:
                img = Image.open(p["imagen"]).resize((180, 180))
                img_tk = ImageTk.PhotoImage(img)
                imagenes_menu.append(img_tk)
                tk.Label(card, image=img_tk, bg=BLANCO).pack(pady=10)
            except:
                tk.Label(card, text="📷\nImagen no\ndisponible", bg=BLANCO, fg=ESPRESSO,
                        font=(FONT, 12), width=15, height=8).pack(pady=10)

            tk.Label(card, text=p["nombre"], bg=BLANCO, fg=ESPRESSO, font=(FONT, 13, "bold")).pack()
            tk.Label(card, text=p["tipo"], bg=BLANCO, fg=LATTE, font=(FONT, 9, "italic")).pack()
            tk.Label(card, text=p["descripcion"], bg=BLANCO, fg=ESPRESSO, font=(FONT, 9), wraplength=180, justify="center").pack(pady=5)
            tk.Label(card, text=f"${p['precio']:.0f}", bg=BLANCO, fg=ESPRESSO, font=(FONT, 16, "bold")).pack(pady=5)
            tk.Button(card, text="Agregar al carrito 🛒", bg=LATTE, fg=BLANCO,
                     font=(FONT, 10, "bold"), command=lambda prod=p: agregar_carrito(prod)).pack(pady=10)

            contador += 1
            col += 1
            if col > 1:
                col = 0
                row += 1

        label_resultados.config(text=f"Mostrando {contador} productos")

    tk.Button(frame_filtros, text="Aplicar", bg=ESPRESSO, fg=BLANCO, font=(FONT, 10, "bold"), command=mostrar_menu).pack(side="left", padx=10)
    mostrar_menu()
    actualizar_carrito()

    tk.Button(frame_carrito, text="Ir a Pagar / Finalizar Pedido 💳", bg=ESPRESSO, fg=BLANCO,
              font=(FONT, 11, "bold"), command=ir_a_pedido_con_carrito).pack(pady=10)

# ---------------- 14. RESERVACIÓN ----------------
@hacer_scrollable
def reservacion():
    global tabla_reserva, imagen_preview, ruta_imagen, doc_actual
    global entrada_id, entrada_nombre, entrada_campo3, entrada_campo4, entrada_campo5
    ruta_imagen = ""
    doc_actual = None

    total_mesas = 10
    mesas_ocupadas = len([d for d in db.collection("reservas").stream() if d.to_dict().get("campo5") == "Confirmada"])

    tk.Label(contenedor, text=f"Reservación de Mesas | Disponibles hoy: {total_mesas-mesas_ocupadas}/{total_mesas}",
             bg=CREMA, fg=ESPRESSO, font=(FONT, 16, "bold")).pack(pady=(0,10))
    tk.Frame(contenedor, bg=LATTE, height=1).pack(fill="x", pady=(0,15))

    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack()

    tk.Label(frame, text="ID Cliente", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_id = tk.Entry(frame, width=40, justify="center")
    entrada_id.pack(pady=5)

    tk.Label(frame, text="Nombre", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_nombre = tk.Entry(frame, width=40, justify="center")
    entrada_nombre.pack(pady=5)

    tk.Label(frame, text="Fecha (DD/MM/YYYY)", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo3 = tk.Entry(frame, width=40, justify="center")
    entrada_campo3.pack(pady=5)

    tk.Label(frame, text="Hora (HH:MM)", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo4 = tk.Entry(frame, width=40, justify="center")
    entrada_campo4.pack(pady=5)

    tk.Label(frame, text="Tipo: Con gatos / Sin gatos", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo5 = tk.Entry(frame, width=40, justify="center")
    entrada_campo5.pack(pady=5)

    label_validacion = tk.Label(frame, text="", bg=CREMA, fg=LATTE, font=(FONT, 9, "italic"))
    label_validacion.pack(pady=2)

    def validar_horario(event):
        tipo = entrada_campo5.get().lower()
        hora = entrada_campo4.get()
        if "con gatos" in tipo and hora:
            try:
                h = int(hora.split(":")[0])
                if h < 8 or h >= 20:
                    label_validacion.config(text="Zona con gatos solo 8:00-20:00", fg="red")
                    entrada_campo4.config(bg="#FFCCCC")
                else:
                    label_validacion.config(text="Horario válido", fg="green")
                    entrada_campo4.config(bg="#CCFFCC")
            except:
                label_validacion.config(text="Formato hora: HH:MM", fg="orange")
        else:
            label_validacion.config(text="")
            entrada_campo4.config(bg=BLANCO)

    entrada_campo4.bind('<KeyRelease>', validar_horario)
    entrada_campo5.bind('<KeyRelease>', validar_horario)

    imagen_preview = tk.Label(frame, bg=CREMA, text="Sin foto")
    imagen_preview.pack(pady=5)
    tk.Button(frame, text="Seleccionar foto", bg=LATTE, fg=BLANCO, command=seleccionar_imagen).pack(pady=5)

    frame_btns = tk.Frame(contenedor, bg=CREMA)
    frame_btns.pack(pady=10)
    tk.Button(frame_btns, text="Guardar", bg=ESPRESSO, fg=BLANCO, command=lambda: guardar_registro("reservas")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Buscar", bg=LATTE, fg=BLANCO, command=lambda: buscar_modificar("reservas")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Actualizar", bg=ESPRESSO, fg=BLANCO, command=lambda: actualizar_registro("reservas")).pack(side="left", padx=5)

    frame_borrar = tk.Frame(contenedor, bg=CREMA)
    frame_borrar.pack(pady=5)
    tk.Label(frame_borrar, text="ID a borrar:", bg=CREMA).pack(side="left")
    entrada_borrar = tk.Entry(frame_borrar, width=20, justify="center")
    entrada_borrar.pack(side="left", padx=5)
    tk.Button(frame_borrar, text="Borrar", bg="red", fg=BLANCO, command=lambda: borrar_registro("reservas", entrada_borrar)).pack(side="left")

    tk.Button(contenedor, text="Mostrar tabla", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), command=lambda: mostrar_datos("reservas")).pack(pady=10)
    tabla_reserva, _ = crear_tabla_con_scroll(contenedor, ("ID", "Nombre", "Fecha", "Hora", "Tipo"))

# ---------------- 15. MICHIS ADOPCIÓN - ARREGLADO PARA QUE APAREZCAN LOS NUEVOS ----------------
@hacer_scrollable
def perfiles_michis():
    global ruta_imagen, doc_actual, imagen_actual, imagen_preview, tabla_perfil, imagenes_michis_catalogo
    global entrada_id, entrada_nombre, entrada_campo3, entrada_campo4, entrada_campo5
    ruta_imagen = ""
    doc_actual = None
    imagenes_michis_catalogo = []

    MICHIS_ADOPCION = [
        {"ruta": r"E:\Diana4B\gato1.jpg", "nombre": "Manchitas", "edad": "2 años",
         "personalidad": "Tranquilo y dormilón", "descripcion": "Gato blanco con manchas negras. Le encanta tomar sol."},
        {"ruta": r"E:\Diana4B\gato2.jpg", "nombre": "Sol", "edad": "1 año",
         "personalidad": "Juguetón y cariñoso", "descripcion": "Gato amarillo. Súper sociable con humanos."},
        {"ruta": r"E:\Diana4B\gato3.jpg", "nombre": "Luna", "edad": "3 años",
         "personalidad": "Elegante e independiente", "descripcion": "Gata siamés. Perfecta para departamento."}
    ]

    total_michis = len(list(db.collection("perfiles").stream()))
    disponibles = len([d for d in db.collection("perfiles").stream() if d.to_dict().get("campo5") == "Disponible"])

    tk.Label(contenedor, text=f"Michis en Adopción | Disponibles: {disponibles}/{total_michis} | ¡Dales un hogar!",
             bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=(0,10))
    tk.Frame(contenedor, bg=LATTE, height=1).pack(fill="x", pady=(0,15))

    frame_catalogo = tk.Frame(contenedor, bg=CREMA)
    frame_catalogo.pack(pady=10, fill="x")

    # ARREGLADO: Ahora carga de Firebase + los 3 fijos
    docs_firebase = list(db.collection("perfiles").stream())

    # Mostrar primero los 3 fijos
    for idx, michi in enumerate(MICHIS_ADOPCION):
        frame_card = tk.Frame(frame_catalogo, bg=BLANCO, bd=2, relief="ridge")
        frame_card.pack(side="left", padx=15, pady=10, expand=True, fill="both")

        try:
            img = Image.open(michi["ruta"]).resize((180, 180))
            img_tk = ImageTk.PhotoImage(img)
            imagenes_michis_catalogo.append(img_tk)
            tk.Label(frame_card, image=img_tk, bg=BLANCO).pack(pady=10)
        except:
            tk.Label(frame_card, text="Foto no disponible", bg=BLANCO, fg=ESPRESSO, width=20, height=10).pack(pady=10)

        tk.Label(frame_card, text=michi["nombre"], bg=BLANCO, fg=ESPRESSO, font=(FONT, 14, "bold")).pack()
        tk.Label(frame_card, text=f"Edad: {michi['edad']}", bg=BLANCO, fg=ESPRESSO, font=(FONT, 10)).pack()
        tk.Label(frame_card, text=michi["personalidad"], bg=BLANCO, fg=LATTE, font=(FONT, 9, "italic")).pack(pady=2)
        tk.Label(frame_card, text=michi["descripcion"], bg=BLANCO, fg=ESPRESSO, font=(FONT, 9), wraplength=200, justify="center").pack(pady=5, padx=10)

        def cargar_michi(m=michi):
            entrada_id.delete(0, tk.END)
            entrada_id.insert(0, m["nombre"].lower())
            entrada_nombre.delete(0, tk.END)
            entrada_nombre.insert(0, m["nombre"])
            entrada_campo3.delete(0, tk.END)
            entrada_campo3.insert(0, m["edad"])
            entrada_campo4.delete(0, tk.END)
            entrada_campo4.insert(0, m["personalidad"])
            entrada_campo5.delete(0, tk.END)
            entrada_campo5.insert(0, "Disponible")
            global ruta_imagen
            ruta_imagen = m["ruta"]
            try:
                img = Image.open(m["ruta"]).resize((100, 100))
                img_tk = ImageTk.PhotoImage(img)
                imagen_preview.config(image=img_tk, text="")
                imagen_preview.image = img_tk
            except: pass
            messagebox.showinfo("Michi seleccionado", f"Cargaste a {m['nombre']} para registrar")

        tk.Button(frame_card, text="Seleccionar para Adoptar ❤️", bg=LATTE, fg=BLANCO,
                  font=(FONT, 10, "bold"), command=cargar_michi).pack(pady=10)

    # ARREGLADO: Mostrar también los de Firebase que no son los 3 fijos
    for doc in docs_firebase:
        d = doc.to_dict()
        if d.get("nombre") not in [m["nombre"] for m in MICHIS_ADOPCION]:
            frame_card = tk.Frame(frame_catalogo, bg="#E6F7FF", bd=2, relief="ridge")
            frame_card.pack(side="left", padx=15, pady=10, expand=True, fill="both")

            try:
                img = Image.open(d.get("imagen", "")).resize((180, 180))
                img_tk = ImageTk.PhotoImage(img)
                imagenes_michis_catalogo.append(img_tk)
                tk.Label(frame_card, image=img_tk, bg="#E6F7FF").pack(pady=10)
            except:
                tk.Label(frame_card, text="Foto no disponible", bg="#E6F7FF", fg=ESPRESSO, width=20, height=10).pack(pady=10)

            tk.Label(frame_card, text=d.get("nombre", ""), bg="#E6F7FF", fg=ESPRESSO, font=(FONT, 14, "bold")).pack()
            tk.Label(frame_card, text=f"Edad: {d.get('campo3', '')}", bg="#E6F7FF", fg=ESPRESSO, font=(FONT, 10)).pack()
            tk.Label(frame_card, text=d.get("campo4", ""), bg="#E6F7FF", fg=LATTE, font=(FONT, 9, "italic")).pack(pady=2)
            tk.Label(frame_card, text=f"Estado: {d.get('campo5', '')}", bg="#E6F7FF", fg=ESPRESSO, font=(FONT, 9)).pack(pady=5, padx=10)
            tk.Label(frame_card, text="✨ Nuevo michi", bg="#E6F7FF", fg="green", font=(FONT, 9, "bold")).pack()

    tk.Frame(contenedor, bg=LATTE, height=1).pack(fill="x", pady=15)

    tk.Label(contenedor, text="Registro de Michis - Se crea perfil automático", bg=CREMA, fg=ESPRESSO, font=(FONT, 14, "bold")).pack(pady=10)

    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack()

    tk.Label(frame, text="ID Michi", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_id = tk.Entry(frame, width=40, justify="center")
    entrada_id.pack(pady=5)
    tk.Label(frame, text="Nombre", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_nombre = tk.Entry(frame, width=40, justify="center")
    entrada_nombre.pack(pady=5)
    tk.Label(frame, text="Edad", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo3 = tk.Entry(frame, width=40, justify="center")
    entrada_campo3.pack(pady=5)
    tk.Label(frame, text="Personalidad", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo4 = tk.Entry(frame, width=40, justify="center")
    entrada_campo4.pack(pady=5)
    tk.Label(frame, text="Estado: Disponible/Adoptado", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo5 = tk.Entry(frame, width=40, justify="center")
    entrada_campo5.pack(pady=5)

    label_dias = tk.Label(frame, text="", bg=CREMA, fg=LATTE, font=(FONT, 9, "italic"))
    label_dias.pack(pady=2)

    def actualizar_color_estado(event):
        estado = entrada_campo5.get().lower()
        if "disponible" in estado:
            entrada_campo5.config(bg="#CCFFCC")
            label_dias.config(text="Listo para encontrar hogar ❤️")
        elif "adoptado" in estado:
            entrada_campo5.config(bg="#FFCCCC")
            label_dias.config(text="¡Ya tiene familia! 🏠")
        else:
            entrada_campo5.config(bg=BLANCO)

    entrada_campo5.bind('<KeyRelease>', actualizar_color_estado)

    imagen_preview = tk.Label(frame, bg=CREMA, text="Sin foto")
    imagen_preview.pack(pady=5)
    tk.Button(frame, text="Seleccionar otra foto", bg=LATTE, fg=BLANCO, command=seleccionar_imagen).pack(pady=5)

    frame_btns = tk.Frame(contenedor, bg=CREMA)
    frame_btns.pack(pady=10)

    def guardar_con_perfil():
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
            datos = {"id": mat, "nombre": nom, "campo3": esp, "campo4": prom_txt, "campo5": horas_txt,
                    "imagen": ruta_destino, "fecha_registro": datetime.now().strftime("%d/%m/%Y")}
            db.collection("perfiles").add(datos)
            messagebox.showinfo("Éxito", f"¡{nom} registrado! Ya aparece arriba con su perfil 🐱")
            limpiar_campos()
            perfiles_michis()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(frame_btns, text="Guardar Michi", bg=ESPRESSO, fg=BLANCO, command=guardar_con_perfil).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Buscar", bg=LATTE, fg=BLANCO, command=lambda: buscar_modificar("perfiles")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Actualizar", bg=ESPRESSO, fg=BLANCO, command=lambda: actualizar_registro("perfiles")).pack(side="left", padx=5)

    def marcar_adoptado():
        if not doc_actual:
            messagebox.showwarning("Atención", "Primero busca un michi")
            return
        db.collection("perfiles").document(doc_actual).update({"campo5": "Adoptado"})
        messagebox.showinfo("Éxito", "¡Michi marcado como adoptado! ❤️")
        limpiar_campos()
        perfiles_michis()

    tk.Button(frame_btns, text="Marcar Adoptado ❤️", bg=LATTE, fg=BLANCO, command=marcar_adoptado).pack(side="left", padx=5)

    frame_borrar = tk.Frame(contenedor, bg=CREMA)
    frame_borrar.pack(pady=5)
    tk.Label(frame_borrar, text="ID a borrar:", bg=CREMA).pack(side="left")
    entrada_borrar = tk.Entry(frame_borrar, width=20, justify="center")
    entrada_borrar.pack(side="left", padx=5)
    tk.Button(frame_borrar, text="Borrar", bg="red", fg=BLANCO, command=lambda: borrar_registro("perfiles", entrada_borrar)).pack(side="left")

    tk.Button(contenedor, text="Mostrar tabla", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), command=lambda: mostrar_datos("perfiles")).pack(pady=10)
    tabla_perfil, _ = crear_tabla_con_scroll(contenedor, ("ID", "Nombre", "Edad", "Personalidad", "Estado"))

    tk.Frame(contenedor, bg=LATTE, height=1).pack(fill="x", pady=(20,5))
    tk.Label(contenedor, text=f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}", bg=CREMA, fg=ESPRESSO, font=(FONT, 8)).pack()

# ---------------- 16. NORMAS CON CONTRATO + CONSULTA ----------------
@hacer_scrollable
def normas():
    usuarios_aceptaron = len(list(db.collection("usuarios").stream()))
    aceptaciones = len(list(db.collection("aceptacion_normas").stream()))

    tk.Label(contenedor, text="Normas del Café Nekocoffe", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    tk.Label(contenedor, text=f"{usuarios_aceptaron} usuarios registrados | {aceptaciones} contratos de aceptación firmados",
             bg=CREMA, fg=LATTE, font=(FONT, 10, "italic")).pack(pady=5)
    tk.Frame(contenedor, bg=LATTE, height=2).pack(fill="x", pady=(0,20))

    normas_generales = """1. Respeto absoluto: No levantar, perseguir ni asustar a los gatos bajo ninguna circunstancia.
2. Higiene obligatoria: Lavarse las manos con gel antibacterial antes y después de interactuar con los michis.
3. Alimentación controlada: Prohibido dar comida externa a los gatos. Solo el personal puede alimentarlos.
4. Fotografías: No usar flash. Las fotos deben tomarse sin perturbar el descanso de los gatos.
5. Volumen: Mantener un tono de voz moderado. Los gritos estresan a los felinos.
6. Espacios de descanso: Respetar las zonas marcadas como "Zona de Siesta" - no molestar gatos dormidos.
7. Niños: Menores de 8 años deben estar acompañados por un adulto en todo momento.
8. Mobiliario: Cualquier daño al mobiliario será responsabilidad del cliente.
9. Prohibido fumar: Establecimiento 100% libre de humo.
10. Tiempo límite: En horas pico, la estancia máxima es de 2 horas por mesa."""

    frame_normas1 = tk.Frame(contenedor, bg=BLANCO, bd=2, relief="ridge")
    frame_normas1.pack(pady=10, padx=40, fill="x")
    tk.Label(frame_normas1, text=normas_generales, bg=BLANCO, fg=ESPRESSO, font=(FONT, 10),
             justify="left", padx=20, pady=15).pack()

    normas_adopcion = """11. Compromiso de por vida: Adoptar es una responsabilidad de 15-20 años.
12. Visita domiciliaria: El equipo de Nekocoffe realizará una visita previa para verificar el hogar.
13. Esterilización: Todos nuestros michis están esterilizados. No se entregan sin este procedimiento.
14. Vacunación: Se entrega cartilla de vacunación al día. El adoptante debe continuar el esquema.
15. Seguimiento: Aceptas recibir visitas de seguimiento los primeros 6 meses.
16. Devolución: Si no puedes cuidarlo, debe regresar a Nekocoffe. Prohibido regalarlo o venderlo.
17. Cuota de recuperación: $500 MXN que cubre vacunas, desparasitación y esterilización."""

    frame_normas2 = tk.Frame(contenedor, bg=BLANCO, bd=2, relief="ridge")
    frame_normas2.pack(pady=10, padx=40, fill="x")
    tk.Label(frame_normas2, text=normas_adopcion, bg=BLANCO, fg=ESPRESSO, font=(FONT, 10),
             justify="left", padx=20, pady=15).pack()

    normas_pedidos = """18. Consumo mínimo: $50 MXN por persona en horario de 12:00-18:00.
19. Tiempo de espera: Los alimentos pueden tardar 15-20 minutos. Son preparados al momento.
20. Alergias: Informar al personal sobre alergias alimentarias antes de ordenar.
21. Mascotas externas: No se permite el ingreso de otras mascotas por seguridad de nuestros gatos.
22. Reservaciones: Cancelar con mínimo 2 horas de anticipación o se cobrará 50% del consumo estimado.
23. Propinas: No son obligatorias pero el 100% va al fondo de rescate animal."""

    frame_normas3 = tk.Frame(contenedor, bg=BLANCO, bd=2, relief="ridge")
    frame_normas3.pack(pady=10, padx=40, fill="x")
    tk.Label(frame_normas3, text=normas_pedidos, bg=BLANCO, fg=ESPRESSO, font=(FONT, 10),
             justify="left", padx=20, pady=15).pack()

    sanciones = """• Primera falta leve: Advertencia verbal
- Segunda falta: Se pedirá abandonar el establecimiento
- Maltrato animal: Expulsión inmediata + reporte a autoridades
- Daño a mobiliario: Cobro del 100% del valor de reposición

Nekocoffe se reserva el derecho de admisión."""

    frame_sanciones = tk.Frame(contenedor, bg="#FFE6E6", bd=2, relief="ridge")
    frame_sanciones.pack(pady=10, padx=40, fill="x")
    tk.Label(frame_sanciones, text=sanciones, bg="#FFE6E6", fg=ESPRESSO, font=(FONT, 10),
             justify="left", padx=20, pady=15).pack()

    tk.Frame(contenedor, bg=LATTE, height=2).pack(fill="x", pady=20)

    tk.Label(contenedor, text="📄 CONTRATO DE ACEPTACIÓN", bg=CREMA, fg=ESPRESSO, font=(FONT, 16, "bold")).pack(pady=10)

    frame_contrato = tk.Frame(contenedor, bg=BLANCO, bd=3, relief="ridge")
    frame_contrato.pack(pady=10, padx=40, fill="x")

    tk.Label(frame_contrato, text="Para continuar, ingresa tus datos y acepta las normas:",
             bg=BLANCO, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=10)

    tk.Label(frame_contrato, text="Nombre completo *:", bg=BLANCO, fg=ESPRESSO).pack(pady=5)
    entry_nombre_contrato = tk.Entry(frame_contrato, width=40, font=(FONT, 11), justify="center")
    entry_nombre_contrato.pack(pady=5)

    tk.Label(frame_contrato, text="Email *:", bg=BLANCO, fg=ESPRESSO).pack(pady=5)
    entry_email_contrato = tk.Entry(frame_contrato, width=40, font=(FONT, 11), justify="center")
    entry_email_contrato.pack(pady=5)

    tk.Label(frame_contrato, text="Teléfono *:", bg=BLANCO, fg=ESPRESSO).pack(pady=5)
    entry_tel_contrato = tk.Entry(frame_contrato, width=40, font=(FONT, 11), justify="center")
    entry_tel_contrato.pack(pady=5)

    acepto = tk.BooleanVar()
    btn_acepto = tk.Button(frame_contrato, text="Generar Contrato de Aceptación",
                           bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), state="disabled")

    def habilitar_boton():
        btn_acepto.config(state="normal" if acepto.get() else "disabled")

    tk.Checkbutton(frame_contrato, text="He leído y acepto TODAS las normas de Nekocoffe",
                   variable=acepto, bg=BLANCO, fg=ESPRESSO, font=(FONT, 10), command=habilitar_boton).pack(pady=15)
    btn_acepto.pack(pady=15)

    def generar_contrato():
        nombre = entry_nombre_contrato.get().strip()
        email = entry_email_contrato.get().strip()
        telefono = entry_tel_contrato.get().strip()

        if not all([nombre, email, telefono]):
            messagebox.showerror("Error", "Ingresa nombre, email y teléfono para generar el contrato")
            return

        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Email inválido")
            return

        try:
            folio = f"NEKO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            datos_contrato = {
                "folio": folio,
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "fecha_aceptacion": fecha,
                "tipo_documento": "Contrato de Aceptación de Normas",
                "version_normas": "v1.0-2026",
                "estado": "Vigente"
            }
            db.collection("aceptacion_normas").add(datos_contrato)

            contrato_texto = f"""
╔══════════════════════════════════════════════════════════╗
║          CONTRATO DE ACEPTACIÓN DE NORMAS                ║
║                    NEKOCOFFE                             ║
╚══════════════════════════════════════════════════════════╝

FOLIO: {folio}
FECHA: {fecha}

Yo, {nombre}, con email {email} y teléfono {telefono}, declaro que:

1. He leído y comprendido TODAS las normas de Nekocoffe.
2. Me comprometo a respetar el bienestar de los gatos rescatados.
3. Acepto las sanciones en caso de incumplimiento.
4. Autorizo el uso de mis datos conforme al Aviso de Privacidad.
5. Entiendo que este documento tiene validez de contrato digital.

Este contrato queda registrado en la base de datos de Nekocoffe
y puede ser consultado por las autoridades competentes.

___________________________
Firma Digital: {nombre}
Folio de Verificación: {folio}
Tel: {telefono}

Nekocoffe - Donde cada sorbo ronronea
© 2026 Todos los derechos reservados
"""

            ventana_contrato = tk.Toplevel(root)
            ventana_contrato.title(f"Contrato {folio}")
            ventana_contrato.geometry("700x600")
            ventana_contrato.configure(bg=BLANCO)

            tk.Label(ventana_contrato, text="CONTRATO GENERADO EXITOSAMENTE ✅",
                    bg=BLANCO, fg="green", font=(FONT, 14, "bold")).pack(pady=10)

            text_widget = tk.Text(ventana_contrato, wrap="word", font=("Courier", 9), bg="#F5F5F5")
            text_widget.insert("1.0", contrato_texto)
            text_widget.config(state="disabled")
            text_widget.pack(padx=20, pady=10, fill="both", expand=True)

            tk.Button(ventana_contrato, text="Cerrar", bg=ESPRESSO, fg=BLANCO,
                     command=ventana_contrato.destroy).pack(pady=10)

            messagebox.showinfo("Éxito", f"Contrato generado con folio: {folio}\n\nGuarda este folio para consultas futuras.")

            entry_nombre_contrato.delete(0, tk.END)
            entry_email_contrato.delete(0, tk.END)
            entry_tel_contrato.delete(0, tk.END)
            acepto.set(False)
            btn_acepto.config(state="disabled")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el contrato: {e}")

    btn_acepto.config(command=generar_contrato)

    tk.Frame(contenedor, bg=LATTE, height=2).pack(fill="x", pady=30)
    tk.Label(contenedor, text="🔍 CONSULTAR CONTRATO EXISTENTE", bg=CREMA, fg=ESPRESSO, font=(FONT, 16, "bold")).pack(pady=10)

    frame_consulta = tk.Frame(contenedor, bg=BLANCO, bd=3, relief="ridge")
    frame_consulta.pack(pady=10, padx=40, fill="x")

    tk.Label(frame_consulta, text="Ingresa tu Folio o Email para consultar tu contrato:",
             bg=BLANCO, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=10)

    tk.Label(frame_consulta, text="Folio o Email:", bg=BLANCO, fg=ESPRESSO).pack(pady=5)
    entry_buscar_contrato = tk.Entry(frame_consulta, width=40, font=(FONT, 11), justify="center")
    entry_buscar_contrato.pack(pady=5)

    def consultar_contrato():
        dato = entry_buscar_contrato.get().strip()
        if not dato:
            messagebox.showwarning("Atención", "Ingresa tu folio o email")
            return

        encontrado = False
        for doc in db.collection("aceptacion_normas").stream():
            d = doc.to_dict()
            if d.get("folio") == dato or d.get("email") == dato:
                contrato_texto = f"""
╔══════════════════════════════════════════════════════════╗
║          CONTRATO DE ACEPTACIÓN DE NORMAS                ║
║                    NEKOCOFFE                             ║
╚══════════════════════════════════════════════════════════╝

FOLIO: {d.get('folio')}
FECHA: {d.get('fecha_aceptacion')}
ESTADO: {d.get('estado')}

Titular: {d.get('nombre')}
Email: {d.get('email')}
Teléfono: {d.get('telefono')}

Este documento certifica que el titular aceptó las normas
de Nekocoffe en la fecha indicada y se encuentra vigente.

Versión de normas: {d.get('version_normas')}

___________________________
Firma Digital: {d.get('nombre')}
Folio de Verificación: {d.get('folio')}

Nekocoffe - Donde cada sorbo ronronea
"""
                ventana_consulta = tk.Toplevel(root)
                ventana_consulta.title(f"Contrato {d.get('folio')}")
                ventana_consulta.geometry("700x600")
                ventana_consulta.configure(bg=BLANCO)

                tk.Label(ventana_consulta, text="CONTRATO ENCONTRADO ✅",
                        bg=BLANCO, fg="green", font=(FONT, 14, "bold")).pack(pady=10)

                text_widget = tk.Text(ventana_consulta, wrap="word", font=("Courier", 9), bg="#F5F5F5")
                text_widget.insert("1.0", contrato_texto)
                text_widget.config(state="disabled")
                text_widget.pack(padx=20, pady=10, fill="both", expand=True)

                tk.Button(ventana_consulta, text="Cerrar", bg=ESPRESSO, fg=BLANCO,
                         command=ventana_consulta.destroy).pack(pady=10)

                encontrado = True
                break

        if not encontrado:
            messagebox.showerror("No encontrado", "No existe un contrato con ese folio o email")

    tk.Button(frame_consulta, text="Buscar Contrato 🔍", bg=ESPRESSO, fg=BLANCO,
              font=(FONT, 11, "bold"), command=consultar_contrato).pack(pady=15)

# ---------------- 17. PEDIDO ONLINE - TABLA ARREGLADA CON TELÉFONO ----------------
@hacer_scrollable
def pedido():
    global tabla_pedido, imagen_preview, ruta_imagen, doc_actual, carrito_global
    global entrada_id, entrada_nombre, entrada_campo3, entrada_campo4, entrada_campo5
    ruta_imagen = ""
    doc_actual = None

    total_gastado = 1450

    tk.Label(contenedor, text="Pedido Online - Finalizar Compra", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    tk.Label(contenedor, text=f"Total histórico gastado: ${total_gastado} | Con $30 más ganas 3 puntos extra",
             bg=CREMA, fg=LATTE, font=(FONT, 10, "italic")).pack(pady=5)

    if carrito_global:
        frame_carrito_info = tk.Frame(contenedor, bg=LATTE, bd=2, relief="ridge")
        frame_carrito_info.pack(fill="x", pady=10, padx=20)
        tk.Label(frame_carrito_info, text="🛒 Productos en tu carrito:", bg=LATTE, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(pady=5)
        for item in carrito_global:
            tk.Label(frame_carrito_info, text=f"• {item['nombre']} x{item['cantidad']} - ${item['precio']*item['cantidad']:.0f}",
                    bg=LATTE, fg=ESPRESSO, font=(FONT, 10)).pack()
        total_carrito = sum(c['precio'] * c['cantidad'] for c in carrito_global)
        tk.Label(frame_carrito_info, text=f"TOTAL: ${total_carrito:.0f}", bg=LATTE, fg=ESPRESSO, font=(FONT, 14, "bold")).pack(pady=10)
        tk.Frame(contenedor, bg=LATTE, height=2).pack(fill="x", pady=10)

    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack()

    tk.Label(frame, text="Email del Cliente *", bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=5)
    entrada_id = tk.Entry(frame, width=40, justify="center")
    entrada_id.pack(pady=5)

    tk.Label(frame, text="Nombre Completo *", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_nombre = tk.Entry(frame, width=40, justify="center")
    entrada_nombre.pack(pady=5)

    tk.Label(frame, text="Teléfono *", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo3 = tk.Entry(frame, width=40, justify="center")
    entrada_campo3.pack(pady=5)

    tk.Label(frame, text="Dirección de Entrega *", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo4 = tk.Entry(frame, width=60, justify="center")
    entrada_campo4.pack(pady=5)

    tk.Label(frame, text="Método de Pago", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    metodo_var = tk.StringVar(value="Efectivo")
    entrada_campo5 = ttk.Combobox(frame, textvariable=metodo_var,
                                   values=["Efectivo", "Tarjeta", "Transferencia"],
                                   width=37, state="readonly")
    entrada_campo5.pack(pady=5)

    label_total_final = tk.Label(frame, text="", bg=CREMA, fg=LATTE, font=(FONT, 12, "bold"))
    label_total_final.pack(pady=10)

    if carrito_global:
        total_carrito = sum(c['precio'] * c['cantidad'] for c in carrito_global)
        productos_str = ", ".join([f"{c['nombre']} x{c['cantidad']}" for c in carrito_global])
        label_total_final.config(text=f"Total a pagar: ${total_carrito:.0f}\nProductos: {productos_str}")

    imagen_preview = tk.Label(frame, bg=CREMA, text="Sin foto de comprobante")
    imagen_preview.pack(pady=5)
    tk.Button(frame, text="Subir Comprobante (opcional)", bg=LATTE, fg=BLANCO, command=seleccionar_imagen).pack(pady=5)

    def confirmar_pedido_final():
        global carrito_global, ruta_imagen
        email = entrada_id.get().strip()
        nombre = entrada_nombre.get().strip()
        telefono = entrada_campo3.get().strip()
        direccion = entrada_campo4.get().strip()
        metodo = entrada_campo5.get().strip()

        if not all([email, nombre, telefono, direccion]):
            messagebox.showerror("Error", "Completa todos los campos obligatorios (*)")
            return

        if not carrito_global:
            messagebox.showwarning("Carrito vacío", "No hay productos en el carrito. Ve a 'Menú & Pedidos' primero.")
            return

        try:
            total = sum(c['precio'] * c['cantidad'] for c in carrito_global)
            puntos = int(total // 10)

            ruta_final = ""
            if ruta_imagen:
                nombre_img = f"comprobante_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(ruta_imagen)}"
                ruta_final = os.path.join(IMAGES_DIR, nombre_img)
                shutil.copy(ruta_imagen, ruta_final)

            datos_pedido = {
                "id": email,
                "nombre": nombre,
                "campo3": telefono,
                "campo4": direccion,
                "campo5": metodo,
                "productos": carrito_global,
                "total": total,
                "puntos": puntos,
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "estado": "Pendiente",
                "imagen": ruta_final
            }
            db.collection("pedidos").add(datos_pedido)

            for doc in db.collection("usuarios").stream():
                if doc.to_dict().get("email") == email:
                    puntos_actuales = doc.to_dict().get("puntos", 0)
                    db.collection("usuarios").document(doc.id).update({"puntos": puntos_actuales + puntos})
                    break

            messagebox.showinfo("Pedido Confirmado ✅",
                f"¡Gracias {nombre}!\n\nTotal: ${total:.0f}\nGanaste {puntos} puntos MichiLover\nMétodo: {metodo}\n\nTe contactaremos al {telefono}")

            carrito_global.clear()
            limpiar_campos()
            pedido()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo procesar el pedido: {e}")

    frame_btns = tk.Frame(contenedor, bg=CREMA)
    frame_btns.pack(pady=20)
    tk.Button(frame_btns, text="Confirmar Pedido y Pagar 💳", bg=ESPRESSO, fg=BLANCO,
              font=(FONT, 12, "bold"), command=confirmar_pedido_final).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Vaciar Carrito", bg="red", fg=BLANCO,
              command=lambda: [carrito_global.clear(), pedido()]).pack(side="left", padx=5)

    tk.Button(contenedor, text="Ver Mis Pedidos", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"),
              command=lambda: mostrar_datos("pedidos")).pack(pady=10)
    # ARREGLADO: Ahora la tabla muestra Email, Nombre, Teléfono, Productos, Método
    tabla_pedido, _ = crear_tabla_con_scroll(contenedor, ("Email", "Nombre", "Teléfono", "Productos", "Método"))

# ---------------- 18. MICHILOVERS - CON FOTOS EN HISTORIAL ----------------
@hacer_scrollable
def michilovers():
    global imagenes_michilovers
    imagenes_michilovers.clear()
    
    tk.Label(contenedor, text="Programa MichiLovers - Fidelización", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)

    frame_busqueda = tk.Frame(contenedor, bg=CREMA)
    frame_busqueda.pack(pady=10)

    tk.Label(frame_busqueda, text="Ingresa tu Email:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(pady=5)
    entry_email = tk.Entry(frame_busqueda, width=40, font=(FONT, 11), justify="center")
    entry_email.pack(pady=5)

    frame_resultado = tk.Frame(contenedor, bg=CREMA)
    frame_resultado.pack(pady=20)

    def consultar_puntos():
        for widget in frame_resultado.winfo_children():
            widget.destroy()
        imagenes_michilovers.clear()

        email = entry_email.get().strip()
        if not email:
            messagebox.showwarning("Atención", "Ingresa tu email")
            return

        user_encontrado = None
        user_id = None
        for doc in db.collection("usuarios").stream():
            if doc.to_dict().get("email") == email:
                user_encontrado = doc.to_dict()
                user_id = doc.id
                break

        if not user_encontrado:
            tk.Label(frame_resultado, text="Usuario no encontrado. Regístrate primero.", bg=CREMA, fg="red", font=(FONT, 12)).pack(pady=10)
            return

        puntos = user_encontrado.get("puntos", 0)

        # Mostrar foto del usuario
        try:
            img = Image.open(user_encontrado.get("imagen", "")).resize((120, 120))
            img_tk = ImageTk.PhotoImage(img)
            imagenes_michilovers.append(img_tk)
            tk.Label(frame_resultado, image=img_tk, bg=CREMA).pack(pady=10)
        except:
            tk.Label(frame_resultado, text="📷 Sin foto", bg=CREMA, fg=ESPRESSO, font=(FONT, 20)).pack(pady=10)

        tk.Label(frame_resultado, text=f"¡Hola {user_encontrado['nombre']}!", bg=CREMA, fg=ESPRESSO, font=(FONT, 14, "bold")).pack(pady=5)

        rango = "Bronce" if puntos < 200 else "Plata" if puntos < 500 else "Oro"
        medalla = "🥉" if rango == "Bronce" else "🥈" if rango == "Plata" else "🥇"
        tk.Label(frame_resultado, text=f"Rango: MichiLover {rango} {medalla}", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(pady=5)

        if puntos < 100: faltan, premio = 100-puntos, "Café gratis"
        elif puntos < 200: faltan, premio = 200-puntos, "Postre gratis"
        elif puntos < 500: faltan, premio = 500-puntos, "Desayuno para 2"
        else: faltan, premio = 1000-puntos, "Kit MichiLover"

        if faltan > 0:
            tk.Label(frame_resultado, text=f"Te faltan {faltan} pts para: {premio}", bg=CREMA, fg=LATTE, font=(FONT, 11)).pack(pady=5)

        canvas_barra = tk.Canvas(frame_resultado, width=300, height=20, bg=BLANCO, highlightthickness=1)
        canvas_barra.pack(pady=5)
        progreso = min(puntos / 1000, 1) * 300
        canvas_barra.create_rectangle(0, 0, progreso, 20, fill=LATTE, outline="")
        tk.Label(frame_resultado, text=f"{puntos}/1000 puntos", bg=CREMA, fg=ESPRESSO).pack()

        def canjear():
            if puntos >= 100:
                nuevos_puntos = puntos - 100 if puntos >= 100 and puntos < 200 else puntos - 200 if puntos >= 200 and puntos < 500 else puntos - 500
                db.collection("usuarios").document(user_id).update({"puntos": nuevos_puntos})
                messagebox.showinfo("Canje", f"¡Felicidades! Canjeaste {premio}\nTus puntos ahora: {nuevos_puntos}")
                consultar_puntos()
            else:
                messagebox.showwarning("Puntos insuficientes", "Necesitas mínimo 100 puntos para canjear")

        if faltan <= 0:
            tk.Button(frame_resultado, text=f"Canjear {premio} 🎁", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), command=canjear).pack(pady=10)

        tk.Label(frame_resultado, text="\n📊 Historial de Actividad", bg=CREMA, fg=ESPRESSO, font=(FONT, 14, "bold")).pack(pady=(20,10))

        tabla_historial, _ = crear_tabla_con_scroll(frame_resultado, ("Fecha", "Actividad", "Puntos", "Total"))

        pedidos_usuario = []
        for doc in db.collection("pedidos").stream():
            d = doc.to_dict()
            if d.get("id") == email:
                pedidos_usuario.append(d)

        if not pedidos_usuario:
            tk.Label(frame_resultado, text="No hay actividad registrada aún", bg=CREMA, fg=LATTE, font=(FONT, 10, "italic")).pack(pady=5)
        else:
            for pedido_data in pedidos_usuario:
                productos_str = ", ".join([f"{p['nombre']} x{p['cantidad']}" for p in pedido_data.get('productos', [])])
                tabla_historial.insert("", "end", text="",
                    values=(pedido_data.get("fecha", ""),
                           productos_str[:50],
                           f"+{pedido_data.get('puntos', 0)}",
                           f"${pedido_data.get('total', 0):.0f}"))

    tk.Button(frame_busqueda, text="Consultar Puntos", bg=ESPRESSO, fg=BLANCO, font=(FONT, 11, "bold"), command=consultar_puntos).pack(pady=10)

    tk.Label(contenedor, text="\n🎁 Beneficios MichiLovers", bg=CREMA, fg=ESPRESSO, font=(FONT, 14, "bold")).pack(pady=(20,10))
    beneficios = """🥉 BRONCE (0-199 pts): 5% descuento en bebidas
🥈 PLATA (200-499 pts): 10% descuento + postre gratis en tu cumpleaños
🥇 ORO (500+ pts): 15% descuento + café gratis mensual + acceso prioritario a adopciones

Cada $10 de compra = 1 punto MichiLover"""

    frame_beneficios = tk.Frame(contenedor, bg=BLANCO, bd=2, relief="ridge")
    frame_beneficios.pack(pady=10, padx=40, fill="x")
    tk.Label(frame_beneficios, text=beneficios, bg=BLANCO, fg=ESPRESSO, font=(FONT, 10),
             justify="left", padx=20, pady=15).pack()

# ---------------- 19. CARGAR MENÚ NUEVO ORDEN ----------------
def cargar_menu_completo():
    for widget in menu_lateral.winfo_children():
        widget.destroy()

    tk.Label(menu_lateral, text="☕ Nekocoffe", bg=ESPRESSO, fg=BLANCO, font=(FONT, 16, "bold")).pack(pady=(20,10))
    tk.Frame(menu_lateral, bg=LATTE, height=2).pack(fill="x", pady=(0,15))

    if not sesion_iniciada:
        crear_boton_menu(menu_lateral, "🏠 Conoce Nekocoffe", conoce)
        crear_boton_menu(menu_lateral, "🔐 Login", login)
    else:
        crear_boton_menu(menu_lateral, "📝 Registro Usuarios", abrir_registro)
        crear_boton_menu(menu_lateral, "🔑 Modificar Credenciales", modificar_perfil)
        tk.Frame(menu_lateral, bg=LATTE, height=1).pack(fill="x", pady=10)

        crear_boton_menu(menu_lateral, "🏠 Conoce Nekocoffe", conoce)
        crear_boton_menu(menu_lateral, "📞 Contacto", contacto)
        crear_boton_menu(menu_lateral, "☕ Menú & Pedidos", filtro_menu)
        crear_boton_menu(menu_lateral, "📅 Reservación", reservacion)
        crear_boton_menu(menu_lateral, "🐱 Michis Adopción", perfiles_michis)
        crear_boton_menu(menu_lateral, "📋 Normas", normas)
        crear_boton_menu(menu_lateral, "🛒 Pedido Online", pedido)
        crear_boton_menu(menu_lateral, "⭐ MichiLovers", michilovers)

# ---------------- 20. FOOTER ----------------
footer = tk.Frame(main_container, bg=ESPRESSO, height=60)
footer.pack(fill="x", side="bottom")
footer.pack_propagate(False)

footer_content = tk.Frame(footer, bg=ESPRESSO)
footer_content.pack(expand=True)

tk.Label(footer_content, text="© 2025 Nekocoffe | Donde cada sorbo ronronea | Hecho con ❤️ por Michis",
         bg=ESPRESSO, fg=BLANCO, font=(FONT, 9)).pack(side="left", padx=20)

# ---------------- 21. INICIO CON CONOCE ----------------
cargar_menu_completo()
conoce()
root.mainloop()