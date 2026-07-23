import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import pandas as pd
from fpdf import FPDF
import threading

# =====================================================================
# CONFIGURACIÓN GLOBAL
# Archivo donde se guardan las configuraciones institucionales
# =====================================================================
CONFIG_FILE = "config_encabezado.json"

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

        # --- INICIALIZACIÓN DE VARIABLES ---
        self.cargar_configuracion()
        self.configurar_estilos()

        self.ruta_asesorias = None
        self.ruta_lista = None
        
        # Carpeta donde se guardarán los PDFs
        self.carpeta_reportes = "Reportes_Generados"
        if not os.path.exists(self.carpeta_reportes):
            os.makedirs(self.carpeta_reportes)

        # Construir Interfaz
        self.crear_menu()
        self.crear_interfaz()

    # =====================================================================
    # ESTILOS VISUALES (Tkinter)
    # Aquí puedes modificar tamaños de fuente y colores de la interfaz
    # =====================================================================
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

    # =====================================================================
    # PERSISTENCIA DE DATOS (JSON)
    # Lógica para guardar y cargar encabezados y logos
    # =====================================================================
    def cargar_configuracion(self):
        self.config_data = {
            "codigo": "CE-RG-25",
            "emision": "31-03-2025",
            "revision": "07",
            "periodo": "Mayo - Agosto 2026",
            "titulo": "Registro de asesorías académicas",
            "logo_izq": "",
            "logo_cen": "",
            "logo_der": ""
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.config_data.update(json.load(f))
            except Exception:
                pass

    def guardar_configuracion(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=4, ensure_ascii=False)

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
            ent.insert(0, self.config_data.get(key, ""))
            ent.grid(row=i, column=1, pady=6, padx=10)
            entries[key] = ent

        ttk.Separator(frame, orient="horizontal").grid(row=5, column=0, columnspan=2, sticky="ew", pady=15)

        def crear_selector_logo(fila, texto_label, clave_config):
            ttk.Label(frame, text=texto_label, font=("Segoe UI", 10, "bold")).grid(row=fila, column=0, sticky="w", pady=6)
            frame_btn = ttk.Frame(frame)
            frame_btn.grid(row=fila, column=1, sticky="w", padx=10)
            
            lbl_ruta = ttk.Label(frame_btn, text=os.path.basename(self.config_data.get(clave_config, '')) or "Sin logo", width=25, style="Ruta.TLabel")
            lbl_ruta.pack(side="left")

            def seleccionar():
                ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
                if ruta:
                    self.config_data[clave_config] = ruta
                    lbl_ruta.config(text=os.path.basename(ruta), foreground=self.c_azul)
            
            ttk.Button(frame_btn, text="Examinar", command=seleccionar).pack(side="left", padx=5)

        crear_selector_logo(6, "Logo Izquierdo (Gto):", "logo_izq")
        crear_selector_logo(7, "Logo Central (UPJR):", "logo_cen")
        crear_selector_logo(8, "Logo Derecho (Educ):", "logo_der")

        def guardar_cambios():
            for key in keys:
                self.config_data[key] = entries[key].get()
            self.guardar_configuracion()
            messagebox.showinfo("Éxito", "Configuración guardada correctamente.", parent=win)
            win.destroy()

        ttk.Button(win, text="Guardar Cambios", style="Accion.TButton", command=guardar_cambios).pack(pady=15)

    # =====================================================================
    # CONSTRUCCIÓN DE LA INTERFAZ PRINCIPAL
    # =====================================================================
    def crear_menu(self):
        menubar = tk.Menu(self, bg=self.c_fondo, fg=self.c_texto)
        menu_archivo = tk.Menu(menubar, tearoff=0, bg="white", fg=self.c_texto)
        menu_archivo.add_command(label="Salir", command=self.quit)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)

        menu_ajustes = tk.Menu(menubar, tearoff=0, bg="white", fg=self.c_texto)
        menu_ajustes.add_command(label="Ajustes de Reporte...", command=self.abrir_ventana_configuracion)
        menubar.add_cascade(label="Configuración", menu=menu_ajustes)
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

    # =====================================================================
    # MÉTODOS DE LÓGICA CORE (Carga y Limpieza de Excel)
    # =====================================================================
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
        if not self.ruta_asesorias or not self.ruta_lista:
            self.escribir_consola("[ERROR] Faltan archivos por cargar.")
            return
        try:
            self.escribir_consola("\n[!] Procesando información...")
            df_asesorias = pd.read_excel(self.ruta_asesorias)
            
            # Sanitizar No. de Control (limpia los .0 que arroja Excel y lo pasa a mayúsculas)
            col_ctrl_asesorias = next((c for c in df_asesorias.columns if 'control' in str(c).lower()), 'No. de control')
            df_asesorias[col_ctrl_asesorias] = df_asesorias[col_ctrl_asesorias].astype(str).str.strip().str.replace(r'\.0$', '', regex=True).str.upper()

            self.df_asesorias_limpio = df_asesorias
            self.escribir_consola("[OK] Análisis completado. Listo para exportar PDFs.")
        except Exception as e:
            self.escribir_consola(f"[ERROR] {str(e)}")

    # =====================================================================
    # MÉTODOS DE DIBUJO DE PDF (FPDF)
    # =====================================================================
    def aplicar_encabezado_fpdf(self, pdf):
        # Esta función dibuja el formato oficial en la parte superior de todas las hojas PDF
        cfg = self.config_data
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(100, 5, cfg.get("titulo", ""), ln=True)
        
        pdf.set_font("Arial", '', 8)
        info_txt = f"Código: {cfg.get('codigo', '')} | Emisión: {cfg.get('emision', '')} | Revisión: {cfg.get('revision', '')}"
        pdf.cell(100, 4, info_txt, ln=True)
        
        pdf.line(10, pdf.get_y() + 1, 200, pdf.get_y() + 1)

        if cfg.get("logo_izq") and os.path.exists(cfg["logo_izq"]):
            pdf.image(cfg["logo_izq"], x=108, y=7, w=28)
            
        if cfg.get("logo_cen") and os.path.exists(cfg["logo_cen"]):
            pdf.image(cfg["logo_cen"], x=152, y=8, w=16)
            
        if cfg.get("logo_der") and os.path.exists(cfg["logo_der"]):
            pdf.image(cfg["logo_der"], x=172, y=7, w=28)

        pdf.ln(18)

    # --- REPORTE DE JEFATURA ---
    def generar_pdf_jefatura(self):
        if not hasattr(self, 'df_asesorias_limpio'):
            self.escribir_consola("[ERROR] Calcula los indicadores primero.")
            return

        try:
            self.escribir_consola("\n[*] Generando PDF de Jefatura...")
            df = self.df_asesorias_limpio.copy()
            
            df_maestra = pd.DataFrame()
            col_ctrl_m, col_nombre_m, col_cal_reg = None, None, None
            
            if self.ruta_lista and os.path.exists(self.ruta_lista):
                df_maestra = pd.read_excel(self.ruta_lista)
                cols_normalizadas = {str(c).lower().strip(): c for c in df_maestra.columns}
                
                for norm, original in cols_normalizadas.items():
                    if 'control' in norm: col_ctrl_m = original
                    elif 'nombre' in norm or 'alumno' in norm: col_nombre_m = original
                    elif 'calific' in norm and 'reg' in norm: col_cal_reg = original
                
                if col_ctrl_m:
                    df_maestra[col_ctrl_m] = df_maestra[col_ctrl_m].astype(str).str.strip().str.replace(r'\.0$', '', regex=True).str.upper()

            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            self.aplicar_encabezado_fpdf(pdf)

            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 6, "CONCENTRADO GENERAL DE ASESORÍAS", align='C', ln=True)
            pdf.set_font("Arial", 'B', 8)
            pdf.cell(0, 5, f"PERÍODO: {self.config_data.get('periodo', '')}", align='C', ln=True)
            pdf.ln(4)

            pdf.set_font("Arial", 'B', 7)
            pdf.set_fill_color(230, 230, 230)
            
            pdf.cell(50, 6, "MATERIA", border=1, align='C', fill=True)
            pdf.cell(25, 6, "MATRÍCULA", border=1, align='C', fill=True)
            pdf.cell(85, 6, "ALUMNO", border=1, align='C', fill=True)
            pdf.cell(30, 6, "CAL. REGULAR", border=1, align='C', fill=True, ln=True)

            pdf.set_font("Arial", '', 6)
            col_ctrl_asesorias = next((c for c in df.columns if 'control' in str(c).lower()), 'No. de control')

            for _, row in df.iterrows():
                materia = str(row.get('Materia', ''))[:35]
                ctrl = str(row.get(col_ctrl_asesorias, '')).strip().replace('.0', '').upper()
                
                nombre_alumno = "No encontrado"
                cal_reg = "-"
                
                if not df_maestra.empty and col_ctrl_m:
                    alumno_info = df_maestra[df_maestra[col_ctrl_m] == ctrl]
                    if not alumno_info.empty:
                        if col_nombre_m: nombre_alumno = str(alumno_info.iloc[0].get(col_nombre_m, ''))[:60]
                        if col_cal_reg: 
                            valor = alumno_info.iloc[0].get(col_cal_reg)
                            cal_reg = str(valor) if pd.notnull(valor) else "S/C"
                        else:
                            cal_reg = "Col. no encontrada"
                    else:
                        nombre_alumno = "Matrícula no en lista"

                pdf.cell(50, 5, f" {materia}", border=1)
                pdf.cell(25, 5, ctrl, border=1, align='C')
                pdf.cell(85, 5, f" {nombre_alumno}", border=1)
                pdf.cell(30, 5, cal_reg, border=1, align='C', ln=True)

            ruta = os.path.join(self.carpeta_reportes, "Reporte_Jefatura.pdf")
            pdf.output(ruta)
            self.escribir_consola(f"[OK] Reporte Jefatura guardado en: {ruta}")
            
        except Exception as e:
            self.escribir_consola(f"[ERROR] PDF Jefatura: {str(e)}")

    # --- REPORTE INDIVIDUAL POR DOCENTE ---
    def generar_pdf_docente(self):
        if not hasattr(self, 'df_asesorias_limpio'):
            self.escribir_consola("[ERROR] Calcula los indicadores primero.")
            return
            
        try:
            self.escribir_consola("\n[*] Generando reportes por docentes...")
            df_asesorias = self.df_asesorias_limpio
            
            df_maestra = pd.DataFrame()
            col_ctrl_m, col_nombre_m, col_sexo_m = None, None, None

            # Buscar y normalizar columnas de la lista maestra
            if self.ruta_lista and os.path.exists(self.ruta_lista):
                df_maestra = pd.read_excel(self.ruta_lista)
                for col in df_maestra.columns:
                    nombre_c = str(col).lower().strip()
                    if 'control' in nombre_c: col_ctrl_m = col
                    elif 'nombre' in nombre_c or 'alumno' in nombre_c: col_nombre_m = col
                    elif 'sexo' in nombre_c or 'género' in nombre_c or 'genero' in nombre_c: col_sexo_m = col

                if col_ctrl_m:
                    df_maestra[col_ctrl_m] = df_maestra[col_ctrl_m].astype(str).str.strip().str.replace(r'\.0$', '', regex=True).str.upper()

            # Extraer lista de docentes únicos
            docentes = df_asesorias['Nombre del asesor(a)'].dropna().unique()
            
            for docente in docentes:
                df_docente = df_asesorias[df_asesorias['Nombre del asesor(a)'] == docente].copy()
                
                pdf = FPDF(orientation='P', unit='mm', format='A4')
                pdf.add_page()
                
                # Cargar el formato institucional
                self.aplicar_encabezado_fpdf(pdf)

                # --- DATOS DEL ASESOR ---
                pdf.set_font("Arial", 'B', 8)
                pdf.cell(63, 5, "NOMBRE DEL(LA) ASESOR(A) ACADÉMICO(A):", border=0)
                pdf.set_font("Arial", '', 9)
                pdf.cell(117, 5, str(docente), border='B', align='C', ln=True)
                
                pdf.set_font("Arial", 'B', 8)
                pdf.cell(16, 5, "CARRERA:", border=0)
                pdf.set_font("Arial", '', 7)
                pdf.cell(94, 5, "Ingeniería en Tecnologías de la Información e Innovación Digital", border=0)
                
                pdf.set_font("Arial", 'B', 8)
                pdf.cell(16, 5, "PERÍODO:", border=0)
                pdf.set_font("Arial", '', 8)
                periodo_txt = self.config_data.get("periodo", "Mayo - Agosto 2026")
                pdf.cell(54, 5, periodo_txt, border='B', align='C', ln=True)
                pdf.ln(3)

                # --- CABECERAS DE LA TABLA PRINCIPAL DE ALUMNOS ---
                x_inicio = 10
                y_inicio = pdf.get_y()
                pdf.set_fill_color(230, 230, 230)

                pdf.set_font("Arial", 'B', 7)
                pdf.set_xy(x_inicio, y_inicio)
                pdf.multi_cell(8, 10, "No.", border=1, align='C', fill=True)
                
                pdf.set_xy(x_inicio + 8, y_inicio)
                pdf.multi_cell(22, 5, "No. DE\nCONTROL", border=1, align='C', fill=True)
                
                pdf.set_xy(x_inicio + 30, y_inicio)
                pdf.multi_cell(62, 10, "NOMBRE DEL(LA) ALUMNO(A)", border=1, align='C', fill=True)

                pdf.set_font("Arial", 'B', 6)
                pdf.set_xy(x_inicio + 92, y_inicio)
                pdf.cell(16, 5, "TIPO ASESORÍA", border=1, align='C', fill=True)
                
                pdf.set_font("Arial", 'B', 7)
                pdf.set_xy(x_inicio + 108, y_inicio)
                pdf.cell(72, 5, "ASESORÍA RECIBIDA", border=1, align='C', fill=True)

                y_sub = y_inicio + 5
                pdf.set_font("Arial", 'B', 5.5)
                pdf.set_xy(x_inicio + 92, y_sub)
                pdf.cell(8, 5, "INDV.", border=1, align='C', fill=True)
                pdf.cell(8, 5, "GRUP.", border=1, align='C', fill=True)
                
                pdf.set_font("Arial", 'B', 7)
                pdf.cell(54, 5, "MATERIA", border=1, align='C', fill=True) 
                pdf.cell(18, 5, "FECHA", border=1, align='C', fill=True)
                
                pdf.set_xy(x_inicio, y_inicio + 10)

                # --- VARIABLES PARA ESTADÍSTICAS ---
                alumnos_procesados = set() # Set para asegurar el conteo de alumnos únicos
                total_hombres = 0
                total_mujeres = 0
                contador = 1

                # Detectar columnas relevantes
                col_ctrl_asesorias = next((c for c in df_docente.columns if 'control' in str(c).lower()), 'No. de control')
                col_sexo_asesorias = next((c for c in df_docente.columns if 'sexo' in str(c).lower() or 'género' in str(c).lower()), None)

                # Iterar sobre cada asesoría dada por este docente
                for _, row in df_docente.iterrows():
                    ctrl = str(row.get(col_ctrl_asesorias, '')).strip().replace('.0', '').upper()
                    materia = str(row.get('Materia', ''))[:45] 
                    tipo = str(row.get('Tipo de asesoría', '')).upper()
                    fecha_raw = str(row.get('Marca temporal', ''))
                    fecha = fecha_raw[:10] if fecha_raw else ""

                    nombre_alumno = ""
                    sexo = ""

                    if col_sexo_asesorias:
                        sexo = str(row.get(col_sexo_asesorias, '')).upper().strip()
                    
                    # Buscar el alumno en la lista maestra
                    if not df_maestra.empty and col_ctrl_m:
                        alumno_info = df_maestra[df_maestra[col_ctrl_m] == ctrl]
                        if not alumno_info.empty:
                            if col_nombre_m:
                                nombre_alumno = str(alumno_info.iloc[0].get(col_nombre_m, ''))[:40]
                            if not sexo and col_sexo_m:
                                sexo = str(alumno_info.iloc[0].get(col_sexo_m, '')).upper().strip()

                    # Lógica para contar ALUMNOS ÚNICOS, HOMBRES y MUJERES
                    if ctrl not in alumnos_procesados:
                        alumnos_procesados.add(ctrl)
                        if sexo.startswith('H') or 'MASCULINO' in sexo or 'HOMBRE' in sexo:
                            total_hombres += 1
                        elif sexo.startswith('M') or 'FEMENINO' in sexo or 'MUJER' in sexo:
                            total_mujeres += 1

                    es_indv = "X" if "IND" in tipo else ""
                    es_grup = "X" if "GRUP" in tipo else ""

                    # Dibujar fila de datos del alumno en el PDF
                    pdf.set_font("Arial", '', 7)
                    pdf.cell(8, 5, str(contador), border=1, align='C')
                    pdf.cell(22, 5, ctrl, border=1, align='C')
                    pdf.cell(62, 5, f" {nombre_alumno}", border=1)
                    
                    pdf.set_font("Arial", '', 6)
                    pdf.cell(8, 5, es_indv, border=1, align='C')
                    pdf.cell(8, 5, es_grup, border=1, align='C')
                    
                    pdf.set_font("Arial", '', 7)
                    pdf.cell(54, 5, f" {materia}", border=1)
                    pdf.cell(18, 5, fecha, border=1, align='C')
                    pdf.ln()

                    contador += 1

                pdf.ln(4)
                
                # --- AQUÍ INICIA EL CAMBIO SOLICITADO (TABLITA DE OBSERVACIONES) ---
                total_asesorias = len(df_docente)
                personas_unicas = len(alumnos_procesados)

                # Título de la sección
                pdf.set_font("Arial", 'B', 8)
                pdf.cell(180, 5, "OBSERVACIONES GENERALES / RESUMEN ESTADÍSTICO", border=1, align='C', fill=True, ln=True)
                
                # 1. Fila de Encabezados (La "tablita")
                pdf.set_font("Arial", 'B', 7)
                pdf.cell(45, 5, "TOTAL DE ASESORÍAS", border=1, align='C', fill=True)
                pdf.cell(45, 5, "ALUMNOS ÚNICOS", border=1, align='C', fill=True)
                pdf.cell(45, 5, "TOTAL HOMBRES", border=1, align='C', fill=True)
                pdf.cell(45, 5, "TOTAL MUJERES", border=1, align='C', fill=True, ln=True)
                
                # 2. Fila de Valores calculados
                pdf.set_font("Arial", '', 8)
                pdf.cell(45, 6, str(total_asesorias), border=1, align='C')
                pdf.cell(45, 6, str(personas_unicas), border=1, align='C')
                pdf.cell(45, 6, str(total_hombres), border=1, align='C')
                pdf.cell(45, 6, str(total_mujeres), border=1, align='C', ln=True)
                
                # 3. Espacio opcional en blanco dentro del mismo recuadro por si el docente necesita escribir a mano
                pdf.set_font("Arial", 'I', 7)
                pdf.cell(180, 4, " Notas del docente:", border='LR', align='L', ln=True)
                pdf.cell(180, 10, "", border='LRB', align='L', ln=True) # Cierra el recuadro
                # --- FIN DEL CAMBIO ---

                pdf.ln(4)
                pdf.set_font("Arial", '', 6)
                pdf.cell(0, 4, "Documento controlado por medios electrónicos. Para uso exclusivo de la Universidad Politécnica de Juventino Rosas", align='C')

                # Guardar el PDF con el nombre del docente
                nombre_clean = str(docente).replace(' ', '_').replace('.', '')
                ruta = os.path.join(self.carpeta_reportes, f"Reporte_{nombre_clean}.pdf")
                pdf.output(ruta)
                
            self.escribir_consola("[OK] Reportes por docente generados correctamente.")
        except Exception as e:
            self.escribir_consola(f"[ERROR] PDF Docente: {str(e)}")

if __name__ == "__main__":
    app = SistemaAsesorias()
    app.mainloop()