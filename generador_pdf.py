import os
import pandas as pd
from fpdf import FPDF

class GeneradorPDF:
    def __init__(self, configuracion, logger_callback):
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

    # --- MÓDULOS DE DIBUJO DE CABECERAS PARA PAGINACIÓN ---
    def _dibujar_cabecera_jefatura(self, pdf):
        pdf.set_font("Arial", 'B', 7)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(50, 6, "MATERIA", border=1, align='C', fill=True)
        pdf.cell(25, 6, "MATRÍCULA", border=1, align='C', fill=True)
        pdf.cell(85, 6, "ALUMNO", border=1, align='C', fill=True)
        pdf.cell(30, 6, "CAL. REGULAR", border=1, align='C', fill=True, ln=True)

    def _dibujar_cabecera_docente(self, pdf, x_inicio, y_inicio):
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

    # --- GENERACIÓN DE REPORTES ---
    def generar_reporte_jefatura(self, df_asesorias_limpio, df_maestra):
        try:
            self.escribir_consola("\n[*] Generando PDF de Jefatura...")
            df = df_asesorias_limpio.copy()
            
            # Buscar columnas dinámicamente
            col_ctrl_asesorias = next((c for c in df.columns if 'control' in str(c).lower()), 'No. de control')
            col_ctrl_m = next((c for c in df_maestra.columns if 'control' in str(c).lower()), None)
            col_nombre_m = next((c for c in df_maestra.columns if 'nombre' in str(c).lower() or 'alumno' in str(c).lower()), None)
            col_cal_reg = next((c for c in df_maestra.columns if 'calific' in str(c).lower() and 'reg' in str(c).lower()), None)

            # Optimización 3: Cruce de datos (Merge) para evitar buscar fila por fila
            if col_ctrl_m:
                columnas_maestra = [col_ctrl_m]
                if col_nombre_m: columnas_maestra.append(col_nombre_m)
                if col_cal_reg: columnas_maestra.append(col_cal_reg)
                
                df_full = pd.merge(df, df_maestra[columnas_maestra], 
                                   left_on=col_ctrl_asesorias, right_on=col_ctrl_m, how='left')
            else:
                df_full = df

            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            self.aplicar_encabezado_fpdf(pdf)

            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 6, "CONCENTRADO GENERAL DE ASESORÍAS", align='C', ln=True)
            pdf.set_font("Arial", 'B', 8)
            pdf.cell(0, 5, f"PERÍODO: {self.config.config_data.get('periodo', '')}", align='C', ln=True)
            pdf.ln(4)

            self._dibujar_cabecera_jefatura(pdf)

            pdf.set_font("Arial", '', 6)
            
            for _, row in df_full.iterrows():
                # Optimización 1: PAGINACIÓN AUTOMÁTICA
                if pdf.get_y() > 270:
                    pdf.add_page()
                    self.aplicar_encabezado_fpdf(pdf)
                    self._dibujar_cabecera_jefatura(pdf)
                    pdf.set_font("Arial", '', 6)

                materia = str(row.get('Materia', ''))[:35]
                ctrl = str(row.get(col_ctrl_asesorias, '')).strip().replace('.0', '').upper()
                
                nombre_alumno = str(row.get(col_nombre_m, 'Matrícula no en lista'))[:60] if col_nombre_m else "No encontrado"
                if pd.isna(nombre_alumno) or nombre_alumno == 'nan': nombre_alumno = "No encontrado"

                if col_cal_reg:
                    valor = row.get(col_cal_reg)
                    cal_reg = str(valor) if pd.notnull(valor) else "S/C"
                else:
                    cal_reg = "N/A"

                pdf.cell(50, 5, f" {materia}", border=1)
                pdf.cell(25, 5, ctrl, border=1, align='C')
                pdf.cell(85, 5, f" {nombre_alumno}", border=1)
                pdf.cell(30, 5, cal_reg, border=1, align='C', ln=True)

            ruta = os.path.join(self.config.carpeta_reportes, "Reporte_Jefatura.pdf")
            pdf.output(ruta)
            self.escribir_consola(f"[OK] Reporte Jefatura guardado en: {ruta}")
            
        except Exception as e:
            self.escribir_consola(f"[ERROR] PDF Jefatura: {str(e)}")

    def generar_reporte_docentes(self, df_asesorias_limpio, df_maestra):
        try:
            self.escribir_consola("\n[*] Generando reportes por docentes...")
            
            # Columnas de asesorías
            col_ctrl_asesorias = next((c for c in df_asesorias_limpio.columns if 'control' in str(c).lower()), 'No. de control')
            col_sexo_asesorias = next((c for c in df_asesorias_limpio.columns if 'sexo' in str(c).lower() or 'género' in str(c).lower()), None)
            
            # Columnas de maestra
            col_ctrl_m = next((c for c in df_maestra.columns if 'control' in str(c).lower()), None)
            col_nombre_m = next((c for c in df_maestra.columns if 'nombre' in str(c).lower() or 'alumno' in str(c).lower()), None)
            col_sexo_m = next((c for c in df_maestra.columns if 'sexo' in str(c).lower() or 'género' in str(c).lower() or 'genero' in str(c).lower()), None)

            # Optimización 3: Cruce masivo en RAM antes de iterar
            if col_ctrl_m:
                columnas_maestra = [col_ctrl_m]
                if col_nombre_m: columnas_maestra.append(col_nombre_m)
                if col_sexo_m: columnas_maestra.append(col_sexo_m)
                
                df_full = pd.merge(df_asesorias_limpio, df_maestra[columnas_maestra], 
                                   left_on=col_ctrl_asesorias, right_on=col_ctrl_m, how='left')
            else:
                df_full = df_asesorias_limpio

            docentes = df_full['Nombre del asesor(a)'].dropna().unique()
            
            for docente in docentes:
                df_docente = df_full[df_full['Nombre del asesor(a)'] == docente].copy()
                
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
                
                # Optimización 2: CARRERA DINÁMICA
                carrera_txt = self.config.config_data.get("carrera", "Ingeniería en Tecnologías de la Información")
                pdf.cell(94, 5, carrera_txt, border=0)
                
                pdf.set_font("Arial", 'B', 8)
                pdf.cell(16, 5, "PERÍODO:", border=0)
                pdf.set_font("Arial", '', 8)
                periodo_txt = self.config.config_data.get("periodo", "Mayo - Agosto 2026")
                pdf.cell(54, 5, periodo_txt, border='B', align='C', ln=True)
                pdf.ln(3)

                # Dibujar cabecera inicial de la tabla
                self._dibujar_cabecera_docente(pdf, 10, pdf.get_y())

                alumnos_procesados = set() 
                total_hombres, total_mujeres, contador = 0, 0, 1

                for _, row in df_docente.iterrows():
                    # Optimización 1: PAGINACIÓN AUTOMÁTICA
                    if pdf.get_y() > 265: # A 3 centímetros de terminar la hoja
                        pdf.add_page()
                        self.aplicar_encabezado_fpdf(pdf)
                        self._dibujar_cabecera_docente(pdf, 10, pdf.get_y())
                    
                    ctrl = str(row.get(col_ctrl_asesorias, '')).strip().replace('.0', '').upper()
                    materia = str(row.get('Materia', ''))[:45] 
                    tipo = str(row.get('Tipo de asesoría', '')).upper()
                    fecha_raw = str(row.get('Marca temporal', ''))
                    fecha = fecha_raw[:10] if fecha_raw else ""
                    
                    # Extracción directa del merge (súper veloz)
                    nombre_alumno = str(row.get(col_nombre_m, ''))[:40] if col_nombre_m else ""
                    if pd.isna(nombre_alumno) or nombre_alumno == 'nan': nombre_alumno = ""
                    
                    sexo = ""
                    if col_sexo_asesorias: 
                        sexo = str(row.get(col_sexo_asesorias, '')).upper().strip()
                    if not sexo and col_sexo_m: 
                        sexo = str(row.get(col_sexo_m, '')).upper().strip()
                    if pd.isna(sexo) or sexo == 'NAN': sexo = ""

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

                # --- ZONA DE RESUMEN FINAL ---
                if pdf.get_y() > 235:
                    pdf.add_page()
                    self.aplicar_encabezado_fpdf(pdf)

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