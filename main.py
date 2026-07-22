import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import pandas as pd
from fpdf import FPDF
import threading

CONFIG_FILE = "config_encabezado.json"

class SistemaAsesorias(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Análisis de Asesorías UPJR")
        self.geometry("850x720")
        self.minsize(850, 720)

        # Cargar configuración del encabezado y periodo
        self.cargar_configuracion()

        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        self.ruta_asesorias = None
        self.ruta_lista = None
        
        self.carpeta_reportes = "Reportes_Generados"
        if not os.path.exists(self.carpeta_reportes):
            os.makedirs(self.carpeta_reportes)

        # Construir Interfaz
        self.crear_menu()
        self.crear_interfaz()

    # ==================== CONFIGURACIÓN Y PERSISTENCIA (JSON) ====================
    def cargar_configuracion(self):
        """Carga las variables del encabezado desde un JSON local."""
        self.config_data = {
            "codigo": "CE-RG-25",
            "emision": "31-03-2025",
            "revision": "07",
            "periodo": "Mayo - Agosto 2026",
            "titulo": "Registro de asesorías académicas",
            "logo_izq": "", # Ej. Gobierno Guanajuato
            "logo_cen": "", # Ej. UPJR
            "logo_der": ""  # Ej. Educación
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.config_data.update(json.load(f))
            except Exception:
                pass

    def guardar_configuracion(self):
        """Guarda los cambios del encabezado en el JSON."""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=4, ensure_ascii=False)

    def abrir_ventana_configuracion(self):
        """Ventana emergente para editar el encabezado del PDF y Período."""
        win = tk.Toplevel(self)
        win.title("Configuración de Encabezado y Período PDF")
        win.geometry("580x480")
        win.resizable(False, False)
        win.grab_set()

        ttk.Label(win, text="Parámetros Institucionales (Formatos)", font=("Arial", 11, "bold")).pack(pady=10)

        frame = ttk.Frame(win, padding=15)
        frame.pack(fill="both", expand=True)

        # Textos de formato
        ttk.Label(frame, text="Título del Formato:").grid(row=0, column=0, sticky="w", pady=4)
        ent_titulo = ttk.Entry(frame, width=42)
        ent_titulo.insert(0, self.config_data.get("titulo", ""))
        ent_titulo.grid(row=0, column=1, pady=4)

        ttk.Label(frame, text="Código del Formato:").grid(row=1, column=0, sticky="w", pady=4)
        ent_codigo = ttk.Entry(frame, width=42)
        ent_codigo.insert(0, self.config_data.get("codigo", ""))
        ent_codigo.grid(row=1, column=1, pady=4)

        ttk.Label(frame, text="Fecha de Emisión:").grid(row=2, column=0, sticky="w", pady=4)
        ent_emision = ttk.Entry(frame, width=42)
        ent_emision.insert(0, self.config_data.get("emision", ""))
        ent_emision.grid(row=2, column=1, pady=4)

        ttk.Label(frame, text="Revisión:").grid(row=3, column=0, sticky="w", pady=4)
        ent_revision = ttk.Entry(frame, width=42)
        ent_revision.insert(0, self.config_data.get("revision", ""))
        ent_revision.grid(row=3, column=1, pady=4)

        ttk.Label(frame, text="Período Escolar:").grid(row=4, column=0, sticky="w", pady=4)
        ent_periodo = ttk.Entry(frame, width=42)
        ent_periodo.insert(0, self.config_data.get("periodo", ""))
        ent_periodo.grid(row=4, column=1, pady=4)

        # Separador visual
        ttk.Separator(frame, orient="horizontal").grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)

        # Selectores de Logos
        def crear_selector_logo(fila, texto_label, clave_config):
            ttk.Label(frame, text=texto_label).grid(row=fila, column=0, sticky="w", pady=4)
            
            frame_btn = ttk.Frame(frame)
            frame_btn.grid(row=fila, column=1, sticky="w")
            
            lbl_ruta = ttk.Label(frame_btn, text=os.path.basename(self.config_data.get(clave_config, '')) or "Sin logo", width=25)
            lbl_ruta.pack(side="left")

            def seleccionar():
                ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
                if ruta:
                    self.config_data[clave_config] = ruta
                    lbl_ruta.config(text=os.path.basename(ruta))

            ttk.Button(frame_btn, text="Examinar...", command=seleccionar).pack(side="left", padx=5)

        crear_selector_logo(6, "Logo Izquierdo (Guanajuato):", "logo_izq")
        crear_selector_logo(7, "Logo Central (UPJR):", "logo_cen")
        crear_selector_logo(8, "Logo Derecho (Educación):", "logo_der")

        def guardar_cambios():
            self.config_data["titulo"] = ent_titulo.get()
            self.config_data["codigo"] = ent_codigo.get()
            self.config_data["emision"] = ent_emision.get()
            self.config_data["revision"] = ent_revision.get()
            self.config_data["periodo"] = ent_periodo.get()
            self.guardar_configuracion()
            messagebox.showinfo("Éxito", "Configuración guardada correctamente.", parent=win)
            win.destroy()

        ttk.Button(win, text="Guardar Cambios", command=guardar_cambios).pack(pady=10)

    # ==================== INTERFAZ PRINCIPAL ====================
    def crear_menu(self):
        menubar = tk.Menu(self)
        
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menu_archivo.add_command(label="Salir", command=self.quit)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)

        menu_ajustes = tk.Menu(menubar, tearoff=0)
        menu_ajustes.add_command(label="Encabezado y Período...", command=self.abrir_ventana_configuracion)
        menubar.add_cascade(label="Configuración", menu=menu_ajustes)

        self.config(menu=menubar)

    def crear_interfaz(self):
        lbl_titulo = ttk.Label(self, text="Panel de Control - Asesorías Académicas", font=("Arial", 16, "bold"))
        lbl_titulo.pack(pady=15)

        frame_archivos = ttk.LabelFrame(self, text=" 1. Carga de datos (.xlsx) ", padding=(15, 10))
        frame_archivos.pack(pady=5, padx=20, fill="x")

        ttk.Button(frame_archivos, text="Cargar respuestas (Forms)", command=self.cargar_archivo_asesorias).grid(row=0, column=0, padx=10, pady=5)
        self.lbl_ruta_asesorias = ttk.Label(frame_archivos, text="Ningún archivo seleccionado...", foreground="gray")
        self.lbl_ruta_asesorias.grid(row=0, column=1, sticky="w")

        ttk.Button(frame_archivos, text="Cargar lista de alumnos", command=self.cargar_archivo_lista).grid(row=1, column=0, padx=10, pady=5)
        self.lbl_ruta_lista = ttk.Label(frame_archivos, text="Ningún archivo seleccionado...", foreground="gray")
        self.lbl_ruta_lista.grid(row=1, column=1, sticky="w")

        frame_procesar = ttk.LabelFrame(self, text=" 2. Análisis ", padding=(15, 10))
        frame_procesar.pack(pady=10, padx=20, fill="x")

        ttk.Button(frame_procesar, text="Calcular indicadores", command=lambda: threading.Thread(target=self.procesar_datos, daemon=True).start()).pack(pady=5)

        self.consola = tk.Text(frame_procesar, height=10, wrap="word", font=("Consolas", 10), bg="#1e1e1e", fg="#00ff00")
        self.consola.pack(pady=5, fill="x")
        self.consola.insert("1.0", "Esperando archivos...\n")
        self.consola.config(state="disabled")

        frame_reportes = ttk.LabelFrame(self, text=" 3. Generación de PDF ", padding=(15, 10))
        frame_reportes.pack(pady=5, padx=20, fill="x")

        ttk.Button(frame_reportes, text="PDF: Reporte para Jefatura", command=lambda: threading.Thread(target=self.generar_pdf_jefatura, daemon=True).start()).pack(side="left", padx=20, pady=10)
        ttk.Button(frame_reportes, text="PDF: Reportes por Docente", command=lambda: threading.Thread(target=self.generar_pdf_docente, daemon=True).start()).pack(side="right", padx=20, pady=10)

    # ==================== LÓGICA CORE ====================
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
            self.lbl_ruta_asesorias.config(text=os.path.basename(ruta), foreground="black")
            self.escribir_consola(f"[*] Asesorías: {os.path.basename(ruta)}")

    def cargar_archivo_lista(self):
        ruta = filedialog.askopenfilename(filetypes=(("Excel", "*.xlsx"),))
        if ruta:
            self.ruta_lista = ruta
            self.lbl_ruta_lista.config(text=os.path.basename(ruta), foreground="black")
            self.escribir_consola(f"[*] Lista: {os.path.basename(ruta)}")

    def procesar_datos(self):
        if not self.ruta_asesorias or not self.ruta_lista:
            self.escribir_consola("[ERROR] Sube ambos archivos .xlsx primero.")
            return
        try:
            self.escribir_consola("\n[!] Procesando datos...")
            df_asesorias = pd.read_excel(self.ruta_asesorias)
            
            # Sanitizar No. de Control en asesorías
            col_ctrl_asesorias = next((c for c in df_asesorias.columns if 'control' in str(c).lower()), 'No. de control')
            df_asesorias[col_ctrl_asesorias] = df_asesorias[col_ctrl_asesorias].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

            self.df_asesorias_limpio = df_asesorias
            self.escribir_consola("[OK] Análisis listo para imprimir PDF.")
        except Exception as e:
            self.escribir_consola(f"[ERROR] {str(e)}")

    # ==================== ENCABEZADO DIBUJADO EN PDF ====================
    def aplicar_encabezado_fpdf(self, pdf):
        cfg = self.config_data
        
        # 1. TEXTO DE RECTORÍA (IZQUIERDA)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(100, 5, cfg.get("titulo", ""), ln=True)
        
        pdf.set_font("Arial", '', 8)
        info_txt = f"Código: {cfg.get('codigo', '')} | Emisión: {cfg.get('emision', '')} | Revisión: {cfg.get('revision', '')}"
        pdf.cell(100, 4, info_txt, ln=True)
        
        # Línea horizontal separadora
        pdf.line(10, pdf.get_y() + 1, 200, pdf.get_y() + 1)

        # 2. LOGOS CON PROPORCIONES Y ESPACIADOS
        if cfg.get("logo_izq") and os.path.exists(cfg["logo_izq"]):
            pdf.image(cfg["logo_izq"], x=108, y=7, w=28)
            
        if cfg.get("logo_cen") and os.path.exists(cfg["logo_cen"]):
            pdf.image(cfg["logo_cen"], x=152, y=8, w=16)
            
        if cfg.get("logo_der") and os.path.exists(cfg["logo_der"]):
            pdf.image(cfg["logo_der"], x=172, y=7, w=28)

        pdf.ln(18)

    def generar_pdf_jefatura(self):
        if not hasattr(self, 'df_asesorias_limpio'):
            self.escribir_consola("[ERROR] Calcula los indicadores primero.")
            return

        try:
            self.escribir_consola("\n[*] Generando PDF de Jefatura...")
            df = self.df_asesorias_limpio
            pdf = FPDF()
            pdf.add_page()

            self.aplicar_encabezado_fpdf(pdf)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "1. Concentrado General por Materia", ln=True)
            
            pdf.set_fill_color(220, 230, 241)
            pdf.set_font("Arial", 'B', 9)
            pdf.cell(140, 7, "Materia", border=1, fill=True)
            pdf.cell(45, 7, "Total Asesorías", border=1, align='C', fill=True, ln=True)
            
            pdf.set_font("Arial", '', 9)
            for materia, total in df['Materia'].value_counts().items():
                pdf.cell(140, 7, f" {str(materia)[:65]}", border=1)
                pdf.cell(45, 7, str(total), border=1, align='C', ln=True)

            ruta = os.path.join(self.carpeta_reportes, "Reporte_Jefatura.pdf")
            pdf.output(ruta)
            self.escribir_consola(f"[OK] PDF guardado en: {ruta}")
            
        except Exception as e:
            self.escribir_consola(f"[ERROR] Generando PDF: {str(e)}")

    def generar_pdf_docente(self):
        if not hasattr(self, 'df_asesorias_limpio'):
            self.escribir_consola("[ERROR] Calcula los indicadores primero.")
            return
            
        try:
            self.escribir_consola("\n[*] Generando reportes por docentes con formato oficial...")
            df_asesorias = self.df_asesorias_limpio
            
            # --- DETECCIÓN INTELIGENTE DE COLUMNAS EN LA LISTA MAESTRA ---
            df_maestra = pd.DataFrame()
            col_ctrl_m, col_nombre_m, col_sexo_m = None, None, None

            if self.ruta_lista and os.path.exists(self.ruta_lista):
                df_maestra = pd.read_excel(self.ruta_lista)
                
                # Buscar columnas por similitud de texto
                for col in df_maestra.columns:
                    nombre_c = str(col).lower().strip()
                    if 'control' in nombre_c:
                        col_ctrl_m = col
                    elif 'nombre' in nombre_c or 'alumno' in nombre_c:
                        col_nombre_m = col
                    elif 'sexo' in nombre_c or 'género' in nombre_c or 'genero' in nombre_c:
                        col_sexo_m = col

                # Limpiar No. de control para la búsqueda
                if col_ctrl_m:
                    df_maestra[col_ctrl_m] = df_maestra[col_ctrl_m].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)

            docentes = df_asesorias['Nombre del asesor(a)'].dropna().unique()
            
            for docente in docentes:
                df_docente = df_asesorias[df_asesorias['Nombre del asesor(a)'] == docente].copy()
                
                pdf = FPDF(orientation='P', unit='mm', format='A4')
                pdf.add_page()
                
                # 1. Logos y datos institucionales
                self.aplicar_encabezado_fpdf(pdf)

                # 2. Datos generales del docente y período (Alineado y Centrado sobre las líneas)
                pdf.set_font("Arial", 'B', 8)
                pdf.cell(63, 5, "NOMBRE DEL(LA) ASESOR(A) ACADÉMICO(A):", border=0)
                pdf.set_font("Arial", '', 9)
                pdf.cell(117, 5, str(docente), border='B', align='C', ln=True) # Centrado en la línea
                
                pdf.set_font("Arial", 'B', 8)
                pdf.cell(16, 5, "CARRERA:", border=0)
                pdf.set_font("Arial", '', 7)
                pdf.cell(94, 5, "Ingeniería en Tecnologías de la Información e Innovación Digital", border=0)
                
                pdf.set_font("Arial", 'B', 8)
                pdf.cell(16, 5, "PERÍODO:", border=0)
                pdf.set_font("Arial", '', 8)
                periodo_txt = self.config_data.get("periodo", "Mayo - Agosto 2026")
                pdf.cell(54, 5, periodo_txt, border='B', align='C', ln=True) # Centrado en la línea
                pdf.ln(3)

                # 3. ENCABEZADO DE TABLA (TIPO DE ASESORÍA CON TEXTO MÁS PEQUEÑO)
                x_inicio = 10
                y_inicio = pdf.get_y()
                
                pdf.set_fill_color(230, 230, 230)

                # Columnas de 2 filas de alto
                pdf.set_font("Arial", 'B', 7)
                pdf.set_xy(x_inicio, y_inicio)
                pdf.multi_cell(8, 10, "No.", border=1, align='C', fill=True)
                
                pdf.set_xy(x_inicio + 8, y_inicio)
                pdf.multi_cell(22, 5, "No. DE\nCONTROL", border=1, align='C', fill=True)
                
                pdf.set_xy(x_inicio + 30, y_inicio)
                pdf.multi_cell(50, 10, "NOMBRE DEL(LA) ALUMNO(A)", border=1, align='C', fill=True)

                # Agrupación: TIPO DE ASESORÍA (Fuente ajustada a 6pt para caber perfecto)
                pdf.set_font("Arial", 'B', 6)
                pdf.set_xy(x_inicio + 80, y_inicio)
                pdf.cell(16, 5, "TIPO ASESORÍA", border=1, align='C', fill=True)
                
                # Agrupación: ASESORÍA RECIBIDA
                pdf.set_font("Arial", 'B', 7)
                pdf.set_xy(x_inicio + 96, y_inicio)
                pdf.cell(72, 5, "ASESORÍA RECIBIDA", border=1, align='C', fill=True)

                # Agrupación: SEXO
                pdf.set_xy(x_inicio + 168, y_inicio)
                pdf.cell(12, 5, "SEXO", border=1, align='C', fill=True)

                # Sub-encabezados (Fila 2)
                y_sub = y_inicio + 5
                
                # Sub-columnas Tipo Asesoría (Fuente reducida a 5.5pt)
                pdf.set_font("Arial", 'B', 5.5)
                pdf.set_xy(x_inicio + 80, y_sub)
                pdf.cell(8, 5, "INDV.", border=1, align='C', fill=True)
                pdf.cell(8, 5, "GRUP.", border=1, align='C', fill=True)
                
                # Sub-columnas Asesoría
                pdf.set_font("Arial", 'B', 7)
                pdf.cell(32, 5, "MATERIA", border=1, align='C', fill=True)
                pdf.cell(18, 5, "FECHA", border=1, align='C', fill=True)
                pdf.cell(22, 5, "FIRMA", border=1, align='C', fill=True)
                
                # Sub-columnas Sexo
                pdf.cell(6, 5, "H", border=1, align='C', fill=True)
                pdf.cell(6, 5, "M", border=1, align='C', fill=True)
                
                pdf.set_xy(x_inicio, y_inicio + 10)

                # 4. LLENADO DE REGISTROS DE ALUMNO
                total_hombres = 0
                total_mujeres = 0
                contador = 1

                # Determinar cuál es la columna de control en el Excel de Asesorías
                col_ctrl_asesorias = next((c for c in df_docente.columns if 'control' in str(c).lower()), 'No. de control')

                for _, row in df_docente.iterrows():
                    ctrl = str(row.get(col_ctrl_asesorias, '')).strip().replace('.0', '')
                    materia = str(row.get('Materia', ''))[:28]
                    tipo = str(row.get('Tipo de asesoría', '')).upper()
                    
                    fecha_raw = str(row.get('Marca temporal', ''))
                    fecha = fecha_raw[:10] if fecha_raw else ""

                    # Búsqueda dinámica del alumno en la Lista Maestra
                    nombre_alumno = ""
                    sexo = ""
                    if not df_maestra.empty and col_ctrl_m:
                        alumno_info = df_maestra[df_maestra[col_ctrl_m] == ctrl]
                        if not alumno_info.empty:
                            if col_nombre_m:
                                nombre_alumno = str(alumno_info.iloc[0].get(col_nombre_m, ''))[:32]
                            if col_sexo_m:
                                sexo = str(alumno_info.iloc[0].get(col_sexo_m, '')).upper().strip()

                    # Marcar tipo de asesoría
                    es_indv = "X" if "IND" in tipo or "INDIVIDUAL" in tipo else ""
                    es_grup = "X" if "GRUP" in tipo or "GRUPAL" in tipo else ""
                    
                    # Marcar Sexo
                    es_h, es_m = "", ""
                    if sexo in ['H', 'HOMBRE', 'MASCULINO']:
                        es_h = "X"
                        total_hombres += 1
                    elif sexo in ['M', 'MUJER', 'FEMENINO']:
                        es_m = "X"
                        total_mujeres += 1

                    # Imprimir fila
                    pdf.set_font("Arial", '', 7)
                    pdf.cell(8, 5, str(contador), border=1, align='C')
                    pdf.cell(22, 5, ctrl, border=1, align='C')
                    pdf.cell(50, 5, f" {nombre_alumno}", border=1)
                    
                    pdf.set_font("Arial", '', 6)
                    pdf.cell(8, 5, es_indv, border=1, align='C')
                    pdf.cell(8, 5, es_grup, border=1, align='C')
                    
                    pdf.set_font("Arial", '', 7)
                    pdf.cell(32, 5, f" {materia}", border=1)
                    pdf.cell(18, 5, fecha, border=1, align='C')
                    pdf.cell(22, 5, "", border=1) # Espacio para Firma
                    pdf.cell(6, 5, es_h, border=1, align='C')
                    pdf.cell(6, 5, es_m, border=1, align='C')
                    pdf.ln()

                    contador += 1

                # 5. RESUMEN Y PIE DE PÁGINA
                pdf.ln(4)
                pdf.set_font("Arial", 'B', 8)
                
                total_asesorias = len(df_docente)
                pdf.cell(75, 6, f"TOTAL DE ASESORÍAS OFRECIDAS:  [ {total_asesorias} ]", border=0)
                pdf.cell(50, 6, f"HOMBRES:  [ {total_hombres} ]", border=0)
                pdf.cell(55, 6, f"MUJERES:  [ {total_mujeres} ]", border=0, ln=True)
                pdf.ln(2)

                # Observaciones
                pdf.cell(180, 5, "OBSERVACIONES GENERALES", border=1, align='C', fill=True, ln=True)
                pdf.cell(180, 12, "", border=1, ln=True)

                # Pie de página oficial
                pdf.ln(4)
                pdf.set_font("Arial", '', 6)
                pdf.cell(0, 4, "Documento controlado por medios electrónicos. Para uso exclusivo de la Universidad Politécnica de Juventino Rosas", align='C')

                # Guardar PDF
                nombre_clean = str(docente).replace(' ', '_').replace('.', '')
                ruta = os.path.join(self.carpeta_reportes, f"Reporte_{nombre_clean}.pdf")
                pdf.output(ruta)
                
            self.escribir_consola("[OK] Reportes por docente generados correctamente.")
        except Exception as e:
            self.escribir_consola(f"[ERROR] Generando reportes por docente: {str(e)}")

if __name__ == "__main__":
    app = SistemaAsesorias()
    app.mainloop()