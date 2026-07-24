import os
import pandas as pd
from fpdf import FPDF

class GeneradorPDF:
    def __init__(self, configuracion, logger_callback):
        """
        configuracion: Instancia de ManejadorConfiguracion
        logger_callback: Función para imprimir mensajes en la consola de Tkinter
        """
        self.config = configuracion
        self.escribir_consola = logger_callback

    def aplicar_encabezado_fpdf(self, pdf):
        cfg = self.config.config_data
        
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

    def generar_reporte_jefatura(self, df_asesorias_limpio, ruta_lista):
        try:
            self.escribir_consola("\n[*] Generando PDF de Jefatura...")
            df = df_asesorias_limpio.copy()
            
            df_maestra = pd.DataFrame()
            col_ctrl_m, col_nombre_m, col_cal_reg = None, None, None
            
            if ruta_lista and os.path.exists(ruta_lista):
                df_maestra = pd.read_excel(ruta_lista)
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
            pdf.cell(0, 5, f"PERÍODO: {self.config.config_data.get('periodo', '')}", align='C', ln=True)
            pdf.ln(4)

            # ... (Cabeceras de tabla)
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
                
                nombre_alumno, cal_reg = "No encontrado", "-"
                
                if not df_maestra.empty and col_ctrl_m:
                    alumno_info = df_maestra[df_maestra[col_ctrl_m] == ctrl]
                    if not alumno_info.empty:
                        if col_nombre_m: nombre_alumno = str(alumno_info.iloc[0].get(col_nombre_m, ''))[:60]
                        if col_cal_reg: 
                            valor = alumno_info.iloc[0].get(col_cal_reg)
                            cal_reg = str(valor) if pd.notnull(valor) else "S/C"
                        else: cal_reg = "Col. no encontrada"
                    else:
                        nombre_alumno = "Matrícula no en lista"

                pdf.cell(50, 5, f" {materia}", border=1)
                pdf.cell(25, 5, ctrl, border=1, align='C')
                pdf.cell(85, 5, f" {nombre_alumno}", border=1)
                pdf.cell(30, 5, cal_reg, border=1, align='C', ln=True)

            ruta = os.path.join(self.config.carpeta_reportes, "Reporte_Jefatura.pdf")
            pdf.output(ruta)
            self.escribir_consola(f"[OK] Reporte Jefatura guardado en: {ruta}")
        except Exception as e:
            self.escribir_consola(f"[ERROR] PDF Jefatura: {str(e)}")

    def generar_reporte_docentes(self, df_asesorias_limpio, ruta_lista):
        try:
            self.escribir_consola("\n[*] Generando reportes por docentes...")
            df_asesorias = df_asesorias_limpio
            
            df_maestra = pd.DataFrame()
            col_ctrl_m, col_nombre_m, col_sexo_m = None, None, None

            if ruta_lista and os.path.exists(ruta_lista):
                df_maestra = pd.read_excel(ruta_lista)
                for col in df_maestra.columns:
                    nombre_c = str(col).lower().strip()
                    if 'control' in nombre_c: col_ctrl_m = col
                    elif 'nombre' in nombre_c or 'alumno' in nombre_c: col_nombre_m = col
                    elif 'sexo' in nombre_c or 'género' in nombre_c or 'genero' in nombre_c: col_sexo_m = col

                if col_ctrl_m:
                    df_maestra[col_ctrl_m] = df_maestra[col_ctrl_m].astype(str).str.strip().str.replace(r'\.0$', '', regex=True).str.upper()

            docentes = df_asesorias['Nombre del asesor(a)'].dropna().unique()
            
            for docente in docentes:
                df_docente = df_asesorias[df_asesorias['Nombre del asesor(a)'] == docente].copy()
                pdf = FPDF(orientation='P', unit='mm', format='A4')
                pdf.add_page()
                self.aplicar_encabezado_fpdf(pdf)

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
                periodo_txt = self.config.config_data.get("periodo", "Mayo - Agosto 2026")
                pdf.cell(54, 5, periodo_txt, border='B', align='C', ln=True)
                pdf.ln(3)

                x_inicio, y_inicio = 10, pdf.get_y()
                pdf.set_fill_color(230, 230, 230)

                # Cabeceras
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

                alumnos_procesados = set() 
                total_hombres, total_mujeres, contador = 0, 0, 1

                col_ctrl_asesorias = next((c for c in df_docente.columns if 'control' in str(c).lower()), 'No. de control')
                col_sexo_asesorias = next((c for c in df_docente.columns if 'sexo' in str(c).lower() or 'género' in str(c).lower()), None)

                for _, row in df_docente.iterrows():
                    ctrl = str(row.get(col_ctrl_asesorias, '')).strip().replace('.0', '').upper()
                    materia = str(row.get('Materia', ''))[:45] 
                    tipo = str(row.get('Tipo de asesoría', '')).upper()
                    fecha_raw = str(row.get('Marca temporal', ''))
                    fecha = fecha_raw[:10] if fecha_raw else ""
                    nombre_alumno, sexo = "", ""

                    if col_sexo_asesorias: sexo = str(row.get(col_sexo_asesorias, '')).upper().strip()
                    
                    if not df_maestra.empty and col_ctrl_m:
                        alumno_info = df_maestra[df_maestra[col_ctrl_m] == ctrl]
                        if not alumno_info.empty:
                            if col_nombre_m: nombre_alumno = str(alumno_info.iloc[0].get(col_nombre_m, ''))[:40]
                            if not sexo and col_sexo_m: sexo = str(alumno_info.iloc[0].get(col_sexo_m, '')).upper().strip()

                    if ctrl not in alumnos_procesados:
                        alumnos_procesados.add(ctrl)
                        if sexo.startswith('H') or 'MASCULINO' in sexo or 'HOMBRE' in sexo: total_hombres += 1
                        elif sexo.startswith('M') or 'FEMENINO' in sexo or 'MUJER' in sexo: total_mujeres += 1

                    es_indv, es_grup = ("X" if "IND" in tipo else ""), ("X" if "GRUP" in tipo else "")

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
                
                total_asesorias = len(df_docente)
                personas_unicas = len(alumnos_procesados)

                pdf.set_font("Arial", 'B', 8)
                pdf.cell(180, 5, "OBSERVACIONES GENERALES / RESUMEN ESTADÍSTICO", border=1, align='C', fill=True, ln=True)
                pdf.set_font("Arial", 'B', 7)
                pdf.cell(45, 5, "TOTAL DE ASESORÍAS", border=1, align='C', fill=True)
                pdf.cell(45, 5, "ALUMNOS ÚNICOS", border=1, align='C', fill=True)
                pdf.cell(45, 5, "TOTAL HOMBRES", border=1, align='C', fill=True)
                pdf.cell(45, 5, "TOTAL MUJERES", border=1, align='C', fill=True, ln=True)
                pdf.set_font("Arial", '', 8)
                pdf.cell(45, 6, str(total_asesorias), border=1, align='C')
                pdf.cell(45, 6, str(personas_unicas), border=1, align='C')
                pdf.cell(45, 6, str(total_hombres), border=1, align='C')
                pdf.cell(45, 6, str(total_mujeres), border=1, align='C', ln=True)
                pdf.set_font("Arial", 'I', 7)
                pdf.cell(180, 4, " Notas del docente:", border='LR', align='L', ln=True)
                pdf.cell(180, 10, "", border='LRB', align='L', ln=True)

                pdf.ln(4)
                pdf.set_font("Arial", '', 6)
                pdf.cell(0, 4, "Documento controlado por medios electrónicos. Para uso exclusivo de la Universidad Politécnica de Juventino Rosas", align='C')

                nombre_clean = str(docente).replace(' ', '_').replace('.', '')
                ruta = os.path.join(self.config.carpeta_reportes, f"Reporte_{nombre_clean}.pdf")
                pdf.output(ruta)
                
            self.escribir_consola("[OK] Reportes por docente generados correctamente.")
        except Exception as e:
            self.escribir_consola(f"[ERROR] PDF Docente: {str(e)}")