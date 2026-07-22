import tkinter as tk
from tkinter import ttk, filedialog
import os
import pandas as pd
from fpdf import FPDF

class SistemaAsesorias(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Análisis de asesorías")
        self.geometry("850x700")
        self.minsize(850, 700)
        
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        self.ruta_asesorias = None
        self.ruta_lista = None

        self.crear_interfaz()

    def crear_interfaz(self):
        # title
        lbl_titulo = ttk.Label(self, text="Panel de control", font=("Arial", 18, "bold"))
        lbl_titulo.pack(pady=20)

        # cargar los datos
        frame_archivos = ttk.LabelFrame(self, text=" 1. Carga de datos (.xlsx únicamente) ", padding=(20, 10))
        frame_archivos.pack(pady=10, padx=20, fill="x")

        self.btn_cargar_asesorias = ttk.Button(frame_archivos, text="Cargar respuestas (Forms)", command=self.cargar_archivo_asesorias)
        self.btn_cargar_asesorias.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        
        self.lbl_ruta_asesorias = ttk.Label(frame_archivos, text="Ningún archivo seleccionado...", foreground="gray")
        self.lbl_ruta_asesorias.grid(row=0, column=1, pady=10, padx=10, sticky="w")

        self.btn_cargar_lista = ttk.Button(frame_archivos, text="Cargar lista de alumnos", command=self.cargar_archivo_lista)
        self.btn_cargar_lista.grid(row=1, column=0, pady=10, padx=10, sticky="w")

        self.lbl_ruta_lista = ttk.Label(frame_archivos, text="Ningún archivo seleccionado...", foreground="gray")
        self.lbl_ruta_lista.grid(row=1, column=1, pady=10, padx=10, sticky="w")

        # procesamiento
        frame_procesar = ttk.LabelFrame(self, text=" 2. Análisis", padding=(20, 10))
        frame_procesar.pack(pady=10, padx=20, fill="x")

        self.btn_procesar = ttk.Button(frame_procesar, text="Calcular indicadores", command=self.procesar_datos)
        self.btn_procesar.pack(pady=10)

        self.consola = tk.Text(frame_procesar, height=12, wrap="word", font=("Consolas", 10), bg="#1e1e1e", fg="#00ff00")
        self.consola.pack(pady=10, fill="x")
        self.consola.insert("1.0", "Esperando archivos...\n")
        self.consola.config(state="disabled")

        # reportes
        frame_reportes = ttk.LabelFrame(self, text=" 3. Reportes PDF ", padding=(20, 10))
        frame_reportes.pack(pady=10, padx=20, fill="x")

        frame_botones_reportes = ttk.Frame(frame_reportes)
        frame_botones_reportes.pack(pady=10)

        self.btn_reporte_jefatura = ttk.Button(frame_botones_reportes, text="PDF: Reporte para jefatura", command=self.generar_pdf_jefatura)
        self.btn_reporte_jefatura.grid(row=0, column=0, padx=10)

        self.btn_reporte_docente = ttk.Button(frame_botones_reportes, text="PDF: Reporte por docente", command=self.generar_pdf_docente)
        self.btn_reporte_docente.grid(row=0, column=1, padx=10)

    # ==================== FUNCIONALIDADES ====================
    def escribir_consola(self, mensaje):
        self.consola.config(state="normal")
        self.consola.insert("end", mensaje + "\n")
        self.consola.see("end")
        self.consola.config(state="disabled")

    def cargar_archivo_asesorias(self):
        ruta = filedialog.askopenfilename(title="Seleccionar Excel de asesorías", filetypes=(("Excel", "*.xlsx"),))
        if ruta:
            self.ruta_asesorias = ruta
            self.lbl_ruta_asesorias.config(text=os.path.basename(ruta), foreground="black")
            self.escribir_consola(f"[*] Asesorías cargadas: {os.path.basename(ruta)}")

    def cargar_archivo_lista(self):
        ruta = filedialog.askopenfilename(title="Seleccionar lista de alumnos", filetypes=(("Excel", "*.xlsx"),))
        if ruta:
            self.ruta_lista = ruta
            self.lbl_ruta_lista.config(text=os.path.basename(ruta), foreground="black")
            self.escribir_consola(f"[*] Lista cargada: {os.path.basename(ruta)}")

    def determinar_unidad(self, fecha_str):
        """Calcula la unidad evaluada dependiendo de la semana del cuatrimestre."""
        try:
            # convertir fecha a datetime
            fecha = pd.to_datetime(fecha_str)
            semana_del_año = fecha.isocalendar()[1]
            
            # cuatrimestre Mayo - Agosto
            if semana_del_año <= 21: # Hasta finales de mayo
                return "Unidad 1"
            elif semana_del_año <= 25: # Todo junio
                return "Unidad 2"
            else: # Julio y Agosto
                return "Unidad 3"
        except:
            return "N/A"

    def procesar_datos(self):
        if not self.ruta_asesorias or not self.ruta_lista:
            self.escribir_consola("[ERROR] Sube ambos archivos .xlsx primero.")
            return
        
        try:
            self.escribir_consola("\n[!] Procesando...")

            df_asesorias = pd.read_excel(self.ruta_asesorias)
            df_maestra = pd.read_excel(self.ruta_lista)

            # Nombres exactos basados en tu formulario
            col_control = 'No. de control' 
            
            # Estandarización
            if 'No. de Control' in df_maestra.columns:
                df_maestra = df_maestra.rename(columns={'No. de Control': col_control})

            df_asesorias[col_control] = df_asesorias[col_control].astype(str).str.strip()
            df_maestra[col_control] = df_maestra[col_control].astype(str).str.strip()
            df_maestra['Estatus'] = df_maestra['Estatus'].astype(str).str.strip().str.upper()

            # Evitar inconsistencia del >100%
            total_asesorias = len(df_asesorias)
            df_unicos = df_asesorias.drop_duplicates(subset=[col_control])
            total_personas = len(df_unicos)

            # Cruce de listas
            df_cruce = pd.merge(df_maestra, df_unicos[[col_control]], on=col_control, how='left', indicator=True)

            # Indicadores
            tomo_acredito = ((df_cruce['_merge'] == 'both') & (df_cruce['Estatus'] == 'ACREDITADO')).sum()
            notomo_acredito = ((df_cruce['_merge'] == 'left_only') & (df_cruce['Estatus'] == 'ACREDITADO')).sum()
            tomo_noacredito = ((df_cruce['_merge'] == 'both') & (df_cruce['Estatus'] == 'NO ACREDITADO')).sum()
            notomo_noacredito = ((df_cruce['_merge'] == 'left_only') & (df_cruce['Estatus'] == 'NO ACREDITADO')).sum()

            self.escribir_consola(f"[*] Asesorías totales: {total_asesorias} | Personas únicas: {total_personas}")
            self.escribir_consola("--- INDICADORES DE ACREDITACIÓN ---")
            self.escribir_consola(f"1. Tomó asesoría y acreditó: {tomo_acredito}")
            self.escribir_consola(f"2. No tomó asesoría y acreditó: {notomo_acredito}")
            self.escribir_consola(f"3. Tomó asesoría y no acreditó: {tomo_noacredito}")
            self.escribir_consola(f"4. No tomó asesoría y no acreditó: {notomo_noacredito}")

            self.df_asesorias_limpio = df_asesorias
            self.escribir_consola("\n[OK] Datos listos PDF.")

        except KeyError as e:
             self.escribir_consola(f"\n[ERROR] Falta la columna {str(e)} en el Excel.")
        except Exception as e:
            self.escribir_consola(f"\n[ERROR FATAL] {str(e)}")

    def generar_pdf_jefatura(self):
        if not hasattr(self, 'df_asesorias_limpio'):
            self.escribir_consola("[ERROR] Calcula los indicadores primero.")
            return

        self.escribir_consola("\n[*] Generando reporte para jefatura...")
        try:
            df = self.df_asesorias_limpio
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Reporte general - Jefatura", ln=True, align='C')
            pdf.ln(5)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "1. Asesorias por materia", ln=True)
            pdf.set_font("Arial", '', 11)
            for materia, total in df['Materia'].value_counts().items():
                pdf.cell(0, 8, f" - {materia}: {total} registros", ln=True)
                
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "2. Asesorias por docente", ln=True)
            pdf.set_font("Arial", '', 11)
            for docente, total in df['Nombre del asesor(a)'].value_counts().items():
                pdf.cell(0, 8, f" - {docente}: {total} registros", ln=True)

            pdf.output("Reporte_Jefatura.pdf")
            self.escribir_consola("[OK] Reporte_Jefatura.pdf guardado.")
        except Exception as e:
            self.escribir_consola(f"[ERROR] {str(e)}")

    def generar_pdf_docente(self):
        if not hasattr(self, 'df_asesorias_limpio'):
            self.escribir_consola("[ERROR] Calcula los indicadores primero.")
            return

        self.escribir_consola("\n[*] Generando reportes por docente...")
        try:
            df = self.df_asesorias_limpio
            docentes = df['Nombre del asesor(a)'].dropna().unique()
            
            for docente in docentes:
                df_docente = df[df['Nombre del asesor(a)'] == docente]
                
                pdf = FPDF()
                pdf.add_page()
                
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, "Reporte Individual de asesorias", ln=True, align='C')
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, f"Docente: {docente}", ln=True, align='C')
                pdf.ln(5)
                
                # Encabezados de tabla
                pdf.set_font("Arial", 'B', 9)
                pdf.cell(25, 8, "Fecha", border=1, align='C')
                pdf.cell(25, 8, "Unidad", border=1, align='C')
                pdf.cell(75, 8, "Materia", border=1, align='C')
                pdf.cell(30, 8, "Tipo", border=1, align='C')
                pdf.cell(35, 8, "No. Control", border=1, align='C')
                pdf.ln()
                
                # Filas
                pdf.set_font("Arial", '', 8)
                for _, row in df_docente.iterrows():
                    fecha_raw = str(row.get('Marca temporal', ''))
                    fecha_corta = fecha_raw[:10] if fecha_raw else "N/A"
                    
                    # Llamada a la nueva función de plan de estudios
                    unidad = self.determinar_unidad(fecha_raw)
                    
                    materia = str(row.get('Materia', ''))[:40]
                    tipo = str(row.get('Tipo de asesoría', ''))
                    control = str(row.get('No. de control', ''))
                    
                    pdf.cell(25, 8, fecha_corta, border=1)
                    pdf.cell(25, 8, unidad, border=1, align='C')
                    pdf.cell(75, 8, materia, border=1)
                    pdf.cell(30, 8, tipo, border=1, align='C')
                    pdf.cell(35, 8, control, border=1, align='C')
                    pdf.ln()
                
                nombre = f"Reporte_{str(docente).replace(' ', '_')}.pdf"
                pdf.output(nombre)
                self.escribir_consola(f"[OK] Generado: {nombre}")
                
        except Exception as e:
            self.escribir_consola(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    app = SistemaAsesorias()
    app.mainloop()