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

# Credenciales de acceso - se pueden cambiar en página 2
USUARIO_LOGIN = "Michelle"
PASS_LOGIN = "110425"

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
    
    # ARREGLO: Más espacio para imágenes y rowheight
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

# ---------------- 7. FUNCIONES CRUD NEKOCOFFE ----------------
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
    tabla = tabla_perfil if coleccion == "perfiles" else tabla_reserva if coleccion == "reservas" else tabla_pedido if coleccion == "pedidos" else tabla_contacto
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
            # ARREGLO: Siempre buscar campo "imagen" unificado
            img = Image.open(d.get("imagen", "")).resize((75, 75))
            img_tk = ImageTk.PhotoImage(img)
            imagenes_guardadas.append(img_tk)
        except: pass
        if coleccion == "contactos":
            tabla.insert("", "end", text="", image=img_tk if img_tk else "",
                        values=(d.get("nombre", ""), d.get("correo", ""), d.get("telefono", ""), d.get("asunto", ""), d.get("mensaje", "")[:30]))
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
        # ARREGLO: Buscar en id, email, nombre y doc.id
        if (d.get("id") == clave or 
            d.get("email") == clave or 
            d.get("nombre", "").lower() == clave.lower() or
            doc.id == clave):
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
        if d["id"] == clave or d.get("nombre", "").lower() == clave.lower():
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

# ---------------- 8. LOGIN ----------------
def login():
    global sesion_iniciada
    limpiar_contenido()
    frame_centro = tk.Frame(contenedor, bg=CREMA)
    frame_centro.pack(expand=True)
    tk.Label(frame_centro, text="Iniciar Sesión", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=30)
    form = tk.Frame(frame_centro, bg=CREMA)
    form.pack()

    tk.Label(form, text="Usuario:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(pady=10)
    entry_user = tk.Entry(form, width=30, font=(FONT, 12), justify="center")
    entry_user.pack(pady=5)

    tk.Label(form, text="Contraseña:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(pady=10)
    entry_pass = tk.Entry(form, width=30, font=(FONT, 12), show="*", justify="center")
    entry_pass.pack(pady=5)

    def validar_login():
        global sesion_iniciada
        if entry_user.get() == USUARIO_LOGIN and entry_pass.get() == PASS_LOGIN:
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
    canvas_window = canvas.create_window((600, 0), window=scroll_frame, anchor="n")
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
• Calidad artesanal: Café de especialidad en cada taza
• Compromiso social: 10% de ganancias va a refugios
• Sustentabilidad: Empaques compostables y café de comercio justo
• Comunidad: Creamos lazos entre humanos y gatos"""
    tk.Label(scroll_frame, text=valores, bg=CREMA, fg=ESPRESSO, font=(FONT, 11), justify="center").pack(padx=40)

    tk.Label(scroll_frame, text="\nHorarios", bg=CREMA, fg=LATTE, font=(FONT, 14, "bold")).pack(pady=(20,5))
    tk.Label(scroll_frame, text="Lunes a Domingo: 8:00 AM - 9:00 PM\nTodos nuestros gatos están vacunados y esterilizados",
             bg=CREMA, fg=ESPRESSO, font=(FONT, 11), justify="center").pack()

    frame = tk.Frame(scroll_frame, bg=CREMA)
    frame.pack(pady=20)
    tk.Label(frame, text="¿Quieres adoptar?", bg=CREMA, fg=ESPRESSO, font=(FONT, 14, "bold")).pack(pady=10)
    tk.Label(frame, text="Déjanos tu correo:", bg=CREMA, fg=ESPRESSO).pack()
    entry_lead = tk.Entry(frame, width=40, justify="center")
    entry_lead.pack(pady=5)

    # ARREGLO: Ahora sí guarda en Firebase
    def enviar_lead():
        correo = entry_lead.get().strip()
        if correo:
            try:
                db.collection("contactos").add({
                    "id": correo, "nombre": "Lead Adopción", "correo": correo,
                    "telefono": "", "asunto": "Adopción", "mensaje": "Interesado en adoptar",
                    "imagen": "", "campo3": "", "campo4": "Adopción", "campo5": "Lead"
                })
                messagebox.showinfo("Gracias", "Te contactaremos pronto para el proceso de adopción")
                entry_lead.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    tk.Button(frame, text="Enviar", bg=LATTE, fg=BLANCO, command=enviar_lead).pack(pady=5)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    canvas.bind("<Configure>", _on_canvas_configure)

# ---------------- 10. PÁGINA 1: REGISTRO - CRUD COMPLETO ----------------
def abrir_registro():
    global ruta_imagen, imagen_preview, tabla_usuarios, doc_actual
    global entrada_id, entrada_nombre, entrada_campo3, entrada_campo4, entrada_campo5
    ruta_imagen = ""
    doc_actual = None
    
    tk.Label(contenedor, text="Registro de Usuarios", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    form = tk.Frame(contenedor, bg=CREMA)
    form.pack()
    
    # ARREGLO: Usar variables globales para poder reusar funciones CRUD
    tk.Label(form, text="ID / Email (para buscar/borrar)", bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=5)
    entrada_id = tk.Entry(form, width=40, font=(FONT, 11), justify="center")
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
    
    # ARREGLO: Nueva función registrar adaptada al CRUD
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
                "fecha": datetime.now().strftime("%d/%m/%Y"), "puntos": 0
            }
            db.collection("usuarios").add(datos)
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")
            limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    # ARREGLO: Buscar específico para usuarios
    def buscar_usuario():
        global doc_actual, imagen_actual
        clave = entrada_id.get().strip()
        if not clave:
            messagebox.showwarning("Atención", "Escribe el Email/ID en el primer campo")
            return
        for doc in db.collection("usuarios").stream():
            d = doc.to_dict()
            if d.get("email") == clave or d.get("id") == clave:
                doc_actual = doc.id
                imagen_actual = d.get("imagen", "")
                entrada_id.delete(0, tk.END)
                entrada_id.insert(0, d.get("email", ""))
                entrada_nombre.delete(0, tk.END)
                entrada_nombre.insert(0, d.get("nombre", ""))
                entrada_campo3.delete(0, tk.END)
                entrada_campo3.insert(0, d.get("campo3", ""))  # contraseña
                entrada_campo4.delete(0, tk.END)
                entrada_campo4.insert(0, d.get("campo3", ""))  # confirmar
                entrada_campo5.delete(0, tk.END)
                entrada_campo5.insert(0, d.get("telefono", ""))
                try:
                    img = Image.open(d["imagen"]).resize((100, 100))
                    img_tk = ImageTk.PhotoImage(img)
                    imagen_preview.config(image=img_tk, text="")
                    imagen_preview.image = img_tk
                except: pass
                messagebox.showinfo("OK", "Usuario cargado para modificar")
                return
        messagebox.showerror("Error", "Usuario no encontrado")
    
    # Botones CRUD
    frame_btns = tk.Frame(contenedor, bg=CREMA)
    frame_btns.pack(pady=10)
    tk.Button(frame_btns, text="Registrar", bg=ESPRESSO, fg=BLANCO, command=registrar_usuario).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Buscar", bg=LATTE, fg=BLANCO, command=buscar_usuario).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Actualizar", bg=ESPRESSO, fg=BLANCO, command=lambda: actualizar_registro("usuarios")).pack(side="left", padx=5)
    
    frame_borrar = tk.Frame(contenedor, bg=CREMA)
    frame_borrar.pack(pady=5)
    tk.Label(frame_borrar, text="Email a borrar:", bg=CREMA).pack(side="left")
    entrada_borrar = tk.Entry(frame_borrar, width=25, justify="center")
    entrada_borrar.pack(side="left", padx=5)
    tk.Button(frame_borrar, text="Borrar", bg="red", fg=BLANCO, command=lambda: borrar_registro("usuarios", entrada_borrar)).pack(side="left")
    
    # ARREGLO: Mostrar tabla adaptada para usuarios
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

# ---------------- 11. PÁGINA 2: MODIFICACIÓN CREDENCIALES LOGIN ----------------
def modificar_perfil():
    global USUARIO_LOGIN, PASS_LOGIN
    tk.Label(contenedor, text="Modificar Credenciales de Acceso", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    tk.Label(contenedor, text="Aquí cambias el usuario y contraseña para entrar al sistema", bg=CREMA, fg=LATTE, font=(FONT, 10, "italic")).pack(pady=5)
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
    entry_pass.insert(0, PASS_LOGIN)
    entry_pass.pack(pady=5)

    tk.Label(form, text="Confirmar contraseña:", bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=(15,5))
    entry_confirm = tk.Entry(form, width=30, font=(FONT, 11), show="*", justify="center")
    entry_confirm.pack(pady=5)

    def actualizar_credenciales():
        global USUARIO_LOGIN, PASS_LOGIN
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
        messagebox.showinfo("Éxito", f"Credenciales actualizadas\nUsuario: {USUARIO_LOGIN}")

    tk.Button(form, text="Actualizar Credenciales", bg=ESPRESSO, fg=BLANCO, font=(FONT, 11, "bold"),
              command=actualizar_credenciales).pack(pady=30)

# ---------------- 12. PÁGINA 4: CONTACTO - CRUD COMPLETO ----------------
def contacto():
    global tabla_contacto, imagen_preview, ruta_imagen, doc_actual
    global entrada_id, entrada_nombre, entrada_campo3, entrada_campo4, entrada_campo5
    ruta_imagen = ""
    doc_actual = None
    
    tk.Label(contenedor, text="Contacto", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    form = tk.Frame(contenedor, bg=CREMA)
    form.pack()
    
    # ARREGLO: Usar variables globales para CRUD
    tk.Label(form, text="ID / Correo (para buscar)", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_id = tk.Entry(form, width=40, justify="center")
    entrada_id.pack(pady=5)
    
    tk.Label(form, text="Nombre", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_nombre = tk.Entry(form, width=40, justify="center")
    entrada_nombre.pack(pady=5)
    
    tk.Label(form, text="Teléfono", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo3 = tk.Entry(form, width=40, justify="center")
    entrada_campo3.pack(pady=5)
    
    tk.Label(form, text="Asunto: Reserva/Adopción/Queja/Otro", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo4 = tk.Entry(form, width=40, justify="center")
    entrada_campo4.pack(pady=5)
    
    tk.Label(form, text="Mensaje", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    # ARREGLO: Text no funciona con CRUD, usamos Entry largo
    entrada_campo5 = tk.Entry(form, width=40, justify="center")
    entrada_campo5.pack(pady=5)
    
    imagen_preview = tk.Label(form, bg=CREMA, text="Sin foto")
    imagen_preview.pack(pady=5)
    tk.Button(form, text="Seleccionar foto", bg=LATTE, fg=BLANCO, command=seleccionar_imagen).pack(pady=5)
    
    # ARREGLO: Función guardar adaptada
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
            messagebox.showinfo("Éxito", "Mensaje enviado")
            limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    # Botones CRUD
    frame_btns = tk.Frame(contenedor, bg=CREMA)
    frame_btns.pack(pady=10)
    tk.Button(frame_btns, text="Guardar", bg=ESPRESSO, fg=BLANCO, command=guardar_contacto).pack(side="left", padx=5)
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

# ---------------- 13. PÁGINA 5: FILTRO DE MENÚ ----------------
def filtro_menu():
    tk.Label(contenedor, text="Filtro de Menú", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack(pady=20)
    tk.Label(frame, text="Tipo de bebida:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(pady=10)
    tipo = tk.StringVar(value="Todas")
    for t in ["Todas", "Bebida caliente", "Bebida fría", "Postre"]:
        tk.Radiobutton(frame, text=t, variable=tipo, value=t, bg=CREMA, fg=ESPRESSO).pack()
    tk.Label(frame, text="\nRestricciones:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(pady=10)
    sin_cafeina = tk.BooleanVar()
    sin_lactosa = tk.BooleanVar()
    sin_gluten = tk.BooleanVar()
    vegano = tk.BooleanVar()
    tk.Checkbutton(frame, text="Sin cafeína", variable=sin_cafeina, bg=CREMA, fg=ESPRESSO).pack()
    tk.Checkbutton(frame, text="Sin lactosa", variable=sin_lactosa, bg=CREMA, fg=ESPRESSO).pack()
    tk.Checkbutton(frame, text="Sin gluten", variable=sin_gluten, bg=CREMA, fg=ESPRESSO).pack()
    tk.Checkbutton(frame, text="Vegano", variable=vegano, bg=CREMA, fg=ESPRESSO).pack()
    tk.Label(frame, text="\nRango de precio:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(pady=10)
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
    tk.Label(frame, text="ID Reserva", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_id = tk.Entry(frame, width=40, justify="center")
    entrada_id.pack(pady=5)
    tk.Label(frame, text="Nombre", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_nombre = tk.Entry(frame, width=40, justify="center")
    entrada_nombre.pack(pady=5)
    tk.Label(frame, text="Fecha DD/MM/YYYY", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo3 = tk.Entry(frame, width=40, justify="center")
    entrada_campo3.pack(pady=5)
    tk.Label(frame, text="Hora HH:MM", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo4 = tk.Entry(frame, width=40, justify="center")
    entrada_campo4.pack(pady=5)
    tk.Label(frame, text="Zona: General/Con gatos", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo5 = tk.Entry(frame, width=40, justify="center")
    entrada_campo5.pack(pady=5)
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
    tabla_reserva, _ = crear_tabla_con_scroll(contenedor, ("ID", "Nombre", "Fecha", "Hora", "Zona"))

# ---------------- 15. PÁGINA 7: PERFILES MICHIS - CRUD COMPLETO ARREGLADO ----------------
def perfiles_michis():
    global ruta_imagen, doc_actual, imagen_actual, imagen_preview, tabla_perfil
    global entrada_id, entrada_nombre, entrada_campo3, entrada_campo4, entrada_campo5
    ruta_imagen = ""
    doc_actual = None
    tk.Label(contenedor, text="Perfiles de Michis - Gestión Completa", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
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
    
    imagen_preview = tk.Label(frame, bg=CREMA, text="Sin foto")
    imagen_preview.pack(pady=5)
    tk.Button(frame, text="Seleccionar foto", bg=LATTE, fg=BLANCO, command=seleccionar_imagen).pack(pady=5)
    
    frame_btns = tk.Frame(contenedor, bg=CREMA)
    frame_btns.pack(pady=10)
    tk.Button(frame_btns, text="Guardar", bg=ESPRESSO, fg=BLANCO, command=lambda: guardar_registro("perfiles")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Buscar", bg=LATTE, fg=BLANCO, command=lambda: buscar_modificar("perfiles")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Actualizar", bg=ESPRESSO, fg=BLANCO, command=lambda: actualizar_registro("perfiles")).pack(side="left", padx=5)
    
    frame_borrar = tk.Frame(contenedor, bg=CREMA)
    frame_borrar.pack(pady=5)
    tk.Label(frame_borrar, text="ID a borrar:", bg=CREMA).pack(side="left")
    entrada_borrar = tk.Entry(frame_borrar, width=20, justify="center")
    entrada_borrar.pack(side="left", padx=5)
    tk.Button(frame_borrar, text="Borrar", bg="red", fg=BLANCO, command=lambda: borrar_registro("perfiles", entrada_borrar)).pack(side="left")
    
    tk.Button(contenedor, text="Mostrar tabla", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), command=lambda: mostrar_datos("perfiles")).pack(pady=10)
    tabla_perfil, _ = crear_tabla_con_scroll(contenedor, ("ID", "Nombre", "Edad", "Personalidad", "Estado"))

# ---------------- 16. PÁGINA 8: NORMAS - ARREGLADO CON GUARDADO ----------------
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
8. El tiempo máximo en zona de gatos es de 90 minutos.
9. Prohibido introducir mascotas externas al local.
10. Respeta a los michis y al personal en todo momento."""
    tk.Label(frame, text=normas_texto, bg=BLANCO, fg=ESPRESSO, font=(FONT, 11), justify="left").pack(pady=20, padx=20)
    
    check = tk.BooleanVar()
    tk.Checkbutton(contenedor, text="He leído y acepto las normas de convivencia", variable=check, bg=CREMA, fg=ESPRESSO, font=(FONT, 11, "bold")).pack(pady=20)
    
    # ARREGLO: Ahora guarda en normas_aceptadas
    def confirmar_lectura():
        if not check.get():
            messagebox.showwarning("Atención", "Debes aceptar las normas primero")
            return
        try:
            datos = {
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "usuario": USUARIO_LOGIN if sesion_iniciada else "Visitante"
            }
            db.collection("normas_aceptadas").add(datos)
            messagebox.showinfo("Éxito", "Lectura de normas confirmada y registrada")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    tk.Button(contenedor, text="Confirmar Lectura", bg=ESPRESSO, fg=BLANCO, font=(FONT, 11, "bold"), command=confirmar_lectura).pack(pady=10)

# ---------------- 17. PÁGINA 9: PEDIDO ONLINE + PUNTOS ----------------
def pedido_online():
    global ruta_imagen, doc_actual, imagen_actual, imagen_preview, tabla_pedido
    global entrada_id, entrada_nombre, entrada_campo3, entrada_campo4, entrada_campo5
    ruta_imagen = ""
    doc_actual = None
    tk.Label(contenedor, text="Pedido y Pago Online", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    frame = tk.Frame(contenedor, bg=CREMA)
    frame.pack()
    
    tk.Label(frame, text="ID o Email del cliente", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_id = tk.Entry(frame, width=40, justify="center")
    entrada_id.pack(pady=5)
    tk.Label(frame, text="Nombre", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_nombre = tk.Entry(frame, width=40, justify="center")
    entrada_nombre.pack(pady=5)
    tk.Label(frame, text="Productos", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo3 = tk.Entry(frame, width=40, justify="center")
    entrada_campo3.pack(pady=5)
    tk.Label(frame, text="Monto Total $", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo4 = tk.Entry(frame, width=40, justify="center")
    entrada_campo4.pack(pady=5)
    tk.Label(frame, text="Método Pago: Tarjeta/Transferencia/Efectivo", bg=CREMA, fg=ESPRESSO).pack(pady=5)
    entrada_campo5 = tk.Entry(frame, width=40, justify="center")
    entrada_campo5.pack(pady=5)
    imagen_preview = tk.Label(frame, bg=CREMA, text="Sin foto")
    imagen_preview.pack(pady=5)
    tk.Button(frame, text="Seleccionar foto", bg=LATTE, fg=BLANCO, command=seleccionar_imagen).pack(pady=5)
    
    def guardar_pedido_con_puntos():
        global ruta_imagen
        id_cliente = entrada_id.get().strip()
        nom = entrada_nombre.get().strip()
        productos = entrada_campo3.get().strip()
        try:
            monto = float(entrada_campo4.get().strip())
        except:
            messagebox.showerror("Error", "El monto debe ser un número")
            return
        pago = entrada_campo5.get().strip()
        
        if not all([id_cliente, nom, productos, monto, pago, ruta_imagen]):
            messagebox.showwarning("Atención", "Faltan datos y foto obligatoria.")
            return
        
        puntos_ganados = int(monto // 10)
        
        try:
            user_doc = None
            for doc in db.collection("usuarios").stream():
                d = doc.to_dict()
                if d.get("email") == id_cliente or doc.id == id_cliente:
                    user_doc = doc
                    break
            
            if not user_doc:
                messagebox.showerror("Error", "Usuario no registrado. Regístralo en Página 1 primero")
                return
            
            nombre_img = f"{id_cliente}_{os.path.basename(ruta_imagen)}"
            ruta_destino = os.path.join(IMAGES_DIR, nombre_img)
            shutil.copy(ruta_imagen, ruta_destino)
            datos_pedido = {
                "id": id_cliente, "nombre": nom, "campo3": productos, 
                "campo4": str(monto), "campo5": pago, "imagen": ruta_destino,
                "puntos_ganados": puntos_ganados, "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            db.collection("pedidos").add(datos_pedido)
            
            puntos_actuales = user_doc.to_dict().get("puntos", 0)
            db.collection("usuarios").document(user_doc.id).update({
                "puntos": puntos_actuales + puntos_ganados
            })
            
            messagebox.showinfo("Éxito", f"Pedido guardado\n+{puntos_ganados} puntos para {nom}")
            limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    frame_btns = tk.Frame(contenedor, bg=CREMA)
    frame_btns.pack(pady=10)
    tk.Button(frame_btns, text="Guardar Pedido", bg=ESPRESSO, fg=BLANCO, command=guardar_pedido_con_puntos).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Buscar", bg=LATTE, fg=BLANCO, command=lambda: buscar_modificar("pedidos")).pack(side="left", padx=5)
    tk.Button(frame_btns, text="Actualizar", bg=ESPRESSO, fg=BLANCO, command=lambda: actualizar_registro("pedidos")).pack(side="left", padx=5)
    
    frame_borrar = tk.Frame(contenedor, bg=CREMA)
    frame_borrar.pack(pady=5)
    tk.Label(frame_borrar, text="ID a borrar:", bg=CREMA).pack(side="left")
    entrada_borrar = tk.Entry(frame_borrar, width=20, justify="center")
    entrada_borrar.pack(side="left", padx=5)
    tk.Button(frame_borrar, text="Borrar", bg="red", fg=BLANCO, command=lambda: borrar_registro("pedidos", entrada_borrar)).pack(side="left")
    
    tk.Button(contenedor, text="Mostrar tabla", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), command=lambda: mostrar_datos("pedidos")).pack(pady=10)
    tabla_pedido, _ = crear_tabla_con_scroll(contenedor, ("ID", "Nombre", "Productos", "Monto", "Pago"))

# ---------------- 18. PÁGINA 10: MICHILOVERS CON CONSULTA DE PUNTOS ----------------
def michilovers():
    tk.Label(contenedor, text="Programa MichiLovers", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    
    frame = tk.Frame(contenedor, bg=BLANCO, bd=2, relief="ridge")
    frame.pack(pady=20, padx=50, fill="x")
    texto = """1 punto = $10 gastados | Puntos vencen en 6 meses\n\nRecompensas:\n100 puntos = Café gratis | 200 puntos = Postre gratis\n500 puntos = Desayuno para 2 | 1000 puntos = Kit MichiLover"""
    tk.Label(frame, text=texto, bg=BLANCO, fg=ESPRESSO, font=(FONT, 12), justify="center").pack(pady=20, padx=20)
    
    frame_buscar = tk.Frame(contenedor, bg=CREMA)
    frame_buscar.pack(pady=10)
    tk.Label(frame_buscar, text="Ingresa tu ID o email para consultar puntos:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(pady=10)
    entry_email = tk.Entry(frame_buscar, width=40, justify="center", font=(FONT, 11))
    entry_email.pack(pady=5)
    
    frame_resultado = tk.Frame(contenedor, bg=CREMA)
    frame_resultado.pack(pady=10, fill="x")
    
    # ---------------- 18. PÁGINA 10: MICHILOVERS CON CONSULTA DE PUNTOS ----------------
def michilovers():
    global imagenes_guardadas
    tk.Label(contenedor, text="Programa MichiLovers", bg=CREMA, fg=ESPRESSO, font=(FONT, 18, "bold")).pack(pady=20)
    
    frame = tk.Frame(contenedor, bg=BLANCO, bd=2, relief="ridge")
    frame.pack(pady=20, padx=50, fill="x")
    texto = """1 punto = $10 gastados | Puntos vencen en 6 meses\n\nRecompensas:\n100 puntos = Café gratis | 200 puntos = Postre gratis\n500 puntos = Desayuno para 2 | 1000 puntos = Kit MichiLover"""
    tk.Label(frame, text=texto, bg=BLANCO, fg=ESPRESSO, font=(FONT, 12), justify="center").pack(pady=20, padx=20)
    
    frame_buscar = tk.Frame(contenedor, bg=CREMA)
    frame_buscar.pack(pady=10)
    tk.Label(frame_buscar, text="Ingresa tu ID o email para consultar puntos:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(pady=10)
    entry_email = tk.Entry(frame_buscar, width=40, justify="center", font=(FONT, 11))
    entry_email.pack(pady=5)
    
    # ARREGLO: frame_resultado debe existir antes del botón
    frame_resultado = tk.Frame(contenedor, bg=CREMA)
    frame_resultado.pack(pady=10, fill="both", expand=True)
    
    def consultar_puntos():
        global imagenes_guardadas
        for widget in frame_resultado.winfo_children():
            widget.destroy()
            
        email = entry_email.get().strip()
        if not email:
            messagebox.showwarning("Atención", "Escribe tu ID o email")
            return
        
        user_encontrado = None
        user_id = None
        for doc in db.collection("usuarios").stream():
            d = doc.to_dict()
            if d.get("email") == email or doc.id == email:
                user_encontrado = d
                user_id = doc.id
                break
        
        if not user_encontrado:
            tk.Label(frame_resultado, text="Usuario no encontrado. Regístrate en Página 1", bg=CREMA, fg="red", font=(FONT, 12)).pack()
            return
        
        puntos = user_encontrado.get("puntos", 0)
        nombre = user_encontrado.get("nombre", "")
        
        # Mostrar foto del usuario
        try:
            img = Image.open(user_encontrado.get("imagen", "")).resize((100, 100))
            img_tk = ImageTk.PhotoImage(img)
            imagenes_guardadas.append(img_tk)
            tk.Label(frame_resultado, image=img_tk, bg=CREMA).pack(pady=5)
        except: pass
        
        tk.Label(frame_resultado, text=f"Hola {nombre}", bg=CREMA, fg=ESPRESSO, font=(FONT, 14, "bold")).pack(pady=5)
        tk.Label(frame_resultado, text=f"Puntos acumulados: {puntos}", bg=CREMA, fg=ESPRESSO, font=(FONT, 16, "bold")).pack(pady=5)
        
        compras = []
        for doc in db.collection("pedidos").stream():
            d = doc.to_dict()
            if d.get("id") == email or d.get("id") == user_id:
                compras.append(d)
        
        if compras:
            tk.Label(frame_resultado, text="Historial de compras:", bg=CREMA, fg=ESPRESSO, font=(FONT, 12, "bold")).pack(pady=10)
            # ARREGLO: Tabla dentro de frame_resultado para que no se borre
            tabla_compras, _ = crear_tabla_con_scroll(frame_resultado, ("Productos", "Monto", "Puntos", "Fecha"))
            for compra in compras:
                tabla_compras.insert("", "end", values=(
                    compra.get("campo3", ""), 
                    f"${compra.get('campo4', '0')}", 
                    compra.get("puntos_ganados", 0),
                    compra.get("fecha", "")[:10]
                ))
        else:
            tk.Label(frame_resultado, text="Aún no tienes compras registradas", bg=CREMA, fg=ESPRESSO).pack(pady=10)
    
    # ARREGLO: El botón va después de definir la función y el frame
    tk.Button(frame_buscar, text="Consultar Puntos", bg=LATTE, fg=BLANCO, font=(FONT, 11, "bold"), command=consultar_puntos).pack(pady=10)

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
        ("2. Modificar Credenciales", modificar_perfil),
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