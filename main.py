import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading    

# --- TUS NUEVOS MÓDULOS SEPARADOS ---
from configuracion import ManejadorConfiguracion
from generador_pdf import GeneradorPDF
from procesador_datos import ProcesadorDatos

class SistemaAsesorias(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- VENTANA PRINCIPAL ---
        self.title("Análisis de Asesorías UPJR")
        self.geometry("880x750")
        self.minsize(880, 750)

        # --- PALETA DE COLORES ---
        self.c_azul = "#107C9D"
        self.c_naranja = "#F17D00"
        self.c_fondo = "#EAEAEA"
        self.c_sombra = "#A8A8A8"
        self.c_texto = "#333333"

        self.configure(bg=self.c_fondo)

        # --- INSTANCIAR MÓDULOS EXTERNOS ---
        # CORRECCIÓN: Cambiamos el nombre de la variable a gestor_config
        self.gestor_config = ManejadorConfiguracion()
        self.pdf_engine = GeneradorPDF(self.gestor_config, self.escribir_consola)
        self.procesador = ProcesadorDatos(self.escribir_consola)

        # --- INICIALIZACIÓN DE VARIABLES ---
        self.configurar_estilos()

        self.ruta_asesorias = None
        self.ruta_lista = None

        # Construir Interfaz
        self.crear_menu()
        self.crear_interfaz()

    def configurar_estilos(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(".", background=self.c_fondo, foreground=self.c_texto, font=("Segoe UI", 10))
        style.configure("TLabel", background=self.c_fondo)
        style.configure("Titulo.TLabel", font=("Segoe UI", 18, "bold"), foreground=self.c_azul)
        style.configure("Ruta.TLabel", font=("Segoe UI", 9, "italic"), foreground=self.c_sombra)
        style.configure("TLabelframe", background=self.c_fondo, bordercolor=self.c_sombra, borderwidth=1)
        style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"), foreground=self.c_azul, background=self.c_fondo)
        
        style.configure("TButton", background=self.c_azul, foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0, focuscolor="none", padding=6)
        style.map("TButton", background=[("active", "#0C5E78")])

        style.configure("Accion.TButton", background=self.c_naranja, foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0, focuscolor="none", padding=8)
        style.map("Accion.TButton", background=[("active", "#C26400")])
        style.configure("TSeparator", background=self.c_sombra)

    def abrir_ventana_configuracion(self):
        win = tk.Toplevel(self)
        win.title("Configuración de Encabezado y Período")
        win.geometry("600x520")
        win.configure(bg=self.c_fondo)
        win.resizable(False, False)
        win.grab_set()

        ttk.Label(win, text="Parámetros Institucionales", style="Titulo.TLabel").pack(pady=15)
        frame = ttk.Frame(win, padding=20)
        frame.pack(fill="both", expand=True)

        labels = ["Título del Formato:", "Código del Formato:", "Fecha de Emisión:", "Revisión:", "Período Escolar:"]
        keys = ["titulo", "codigo", "emision", "revision", "periodo"]
        entries = {}

        for i, (text, key) in enumerate(zip(labels, keys)):
            ttk.Label(frame, text=text, font=("Segoe UI", 10, "bold")).grid(row=i, column=0, sticky="w", pady=6)
            ent = ttk.Entry(frame, width=45, font=("Segoe UI", 10))
            # CORRECCIÓN: Usar gestor_config
            ent.insert(0, self.gestor_config.config_data.get(key, ""))
            ent.grid(row=i, column=1, pady=6, padx=10)
            entries[key] = ent

        ttk.Separator(frame, orient="horizontal").grid(row=5, column=0, columnspan=2, sticky="ew", pady=15)

        def crear_selector_logo(fila, texto_label, clave_config):
            ttk.Label(frame, text=texto_label, font=("Segoe UI", 10, "bold")).grid(row=fila, column=0, sticky="w", pady=6)
            frame_btn = ttk.Frame(frame)
            frame_btn.grid(row=fila, column=1, sticky="w", padx=10)
            
            # CORRECCIÓN: Usar gestor_config
            lbl_ruta = ttk.Label(frame_btn, text=os.path.basename(self.gestor_config.config_data.get(clave_config, '')) or "Sin logo", width=25, style="Ruta.TLabel")
            lbl_ruta.pack(side="left")

            def seleccionar():
                ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
                if ruta:
                    # CORRECCIÓN: Usar gestor_config
                    self.gestor_config.config_data[clave_config] = ruta
                    lbl_ruta.config(text=os.path.basename(ruta), foreground=self.c_azul)
            
            ttk.Button(frame_btn, text="Examinar", command=seleccionar).pack(side="left", padx=5)

        crear_selector_logo(6, "Logo Izquierdo (Gto):", "logo_izq")
        crear_selector_logo(7, "Logo Central (UPJR):", "logo_cen")
        crear_selector_logo(8, "Logo Derecho (Educ):", "logo_der")

        def guardar_cambios():
            for key in keys:
                # CORRECCIÓN: Usar gestor_config
                self.gestor_config.config_data[key] = entries[key].get()
            self.gestor_config.guardar_configuracion()
            messagebox.showinfo("Éxito", "Configuración guardada correctamente.", parent=win)
            win.destroy()

        ttk.Button(win, text="Guardar Cambios", style="Accion.TButton", command=guardar_cambios).pack(pady=15)

    def crear_menu(self):
        menubar = tk.Menu(self, bg=self.c_fondo, fg=self.c_texto)
        menu_archivo = tk.Menu(menubar, tearoff=0, bg="white", fg=self.c_texto)
        menu_archivo.add_command(label="Salir", command=self.quit)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)

        menu_ajustes = tk.Menu(menubar, tearoff=0, bg="white", fg=self.c_texto)
        menu_ajustes.add_command(label="Ajustes de Reporte...", command=self.abrir_ventana_configuracion)
        menubar.add_cascade(label="Configuración", menu=menu_ajustes)
        
        # Ahora esto funcionará correctamente
        self.config(menu=menubar)

    def crear_interfaz(self):
        frame_header = tk.Frame(self, bg=self.c_fondo)
        frame_header.pack(fill="x", pady=15)
        ttk.Label(frame_header, text="SISTEMA DE ANÁLISIS DE ASESORÍAS", style="Titulo.TLabel").pack()
        ttk.Label(frame_header, text="Universidad Politécnica de Juventino Rosas", font=("Segoe UI", 11)).pack()

        # --- SECCIÓN 1: ARCHIVOS ---
        frame_archivos = ttk.LabelFrame(self, text=" 1. Carga de Datos ", padding=(20, 15))
        frame_archivos.pack(pady=10, padx=25, fill="x")

        ttk.Button(frame_archivos, text="📄 Cargar Formulario (.xlsx)", command=self.cargar_archivo_asesorias).grid(row=0, column=0, padx=(0, 15), pady=8)
        self.lbl_ruta_asesorias = ttk.Label(frame_archivos, text="Ningún archivo seleccionado...", style="Ruta.TLabel")
        self.lbl_ruta_asesorias.grid(row=0, column=1, sticky="w")

        ttk.Button(frame_archivos, text="📋 Cargar Lista de Alumnos", command=self.cargar_archivo_lista).grid(row=1, column=0, padx=(0, 15), pady=8)
        self.lbl_ruta_lista = ttk.Label(frame_archivos, text="Ningún archivo seleccionado...", style="Ruta.TLabel")
        self.lbl_ruta_lista.grid(row=1, column=1, sticky="w")

        # --- SECCIÓN 2: PROCESAMIENTO ---
        frame_procesar = ttk.LabelFrame(self, text=" 2. Análisis de Datos ", padding=(20, 15))
        frame_procesar.pack(pady=10, padx=25, fill="x")

        ttk.Button(frame_procesar, text="⚙️ Calcular Indicadores", command=lambda: threading.Thread(target=self.procesar_datos, daemon=True).start()).pack(pady=(0, 10), anchor="w")

        self.consola = tk.Text(frame_procesar, height=10, wrap="word", font=("Consolas", 10), bg="white", fg=self.c_texto,
                               highlightthickness=1, highlightbackground=self.c_sombra, highlightcolor=self.c_azul,
                               relief="flat", padx=10, pady=10)
        self.consola.pack(fill="x")
        self.consola.insert("1.0", "Sistema inicializado. Esperando archivos...\n")
        self.consola.config(state="disabled")

        # --- SECCIÓN 3: EXPORTACIÓN ---
        frame_reportes = ttk.LabelFrame(self, text=" 3. Exportar Reportes ", padding=(20, 15))
        frame_reportes.pack(pady=10, padx=25, fill="x")

        frame_botones_pdf = ttk.Frame(frame_reportes)
        frame_botones_pdf.pack(anchor="center")

        ttk.Button(frame_botones_pdf, text="📥 Reporte Jefatura", style="Accion.TButton", 
                    command=lambda: threading.Thread(target=self.generar_pdf_jefatura, daemon=True).start()).grid(row=0, column=0, padx=15, pady=10)
        
        ttk.Button(frame_botones_pdf, text="📥 Reportes Docentes", style="Accion.TButton", 
                    command=lambda: threading.Thread(target=self.generar_pdf_docente, daemon=True).start()).grid(row=0, column=1, padx=15, pady=10)

    # --- FUNCIONES DE INTERFAZ Y PUENTES A LOS MÓDULOS ---
    
    def escribir_consola(self, mensaje):
        def _insertar():
            self.consola.config(state="normal")
            self.consola.insert("end", mensaje + "\n")
            self.consola.see("end")
            self.consola.config(state="disabled")
        self.after(0, _insertar)

    def cargar_archivo_asesorias(self):
        ruta = filedialog.askopenfilename(filetypes=(("Excel", "*.xlsx"),))
        if ruta:
            self.ruta_asesorias = ruta
            self.lbl_ruta_asesorias.config(text=os.path.basename(ruta), foreground=self.c_azul, font=("Segoe UI", 9, "bold"))
            self.escribir_consola(f"[*] Formulario cargado: {os.path.basename(ruta)}")

    def cargar_archivo_lista(self):
        ruta = filedialog.askopenfilename(filetypes=(("Excel", "*.xlsx"),))
        if ruta:
            self.ruta_lista = ruta
            self.lbl_ruta_lista.config(text=os.path.basename(ruta), foreground=self.c_azul, font=("Segoe UI", 9, "bold"))
            self.escribir_consola(f"[*] Lista cargada: {os.path.basename(ruta)}")

    def procesar_datos(self):
        self.procesador.procesar(self.ruta_asesorias, self.ruta_lista)

    def generar_pdf_jefatura(self):
        if self.procesador.df_asesorias_limpio is None:
            self.escribir_consola("[ERROR] Calcula los indicadores primero.")
            return
        self.pdf_engine.generar_reporte_jefatura(self.procesador.df_asesorias_limpio, self.ruta_lista)

    def generar_pdf_docente(self):
        if self.procesador.df_asesorias_limpio is None:
            self.escribir_consola("[ERROR] Calcula los indicadores primero.")
            return
        self.pdf_engine.generar_reporte_docentes(self.procesador.df_asesorias_limpio, self.ruta_lista)

if __name__ == "__main__":
    app = SistemaAsesorias()
    app.mainloop()