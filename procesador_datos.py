import pandas as pd

class ProcesadorDatos:
    def __init__(self, logger_callback):
        """
        logger_callback: Función para imprimir mensajes en la consola de Tkinter
        """
        self.escribir_consola = logger_callback
        self.df_asesorias_limpio = None

    def procesar(self, ruta_asesorias, ruta_lista):
        if not ruta_asesorias or not ruta_lista:
            self.escribir_consola("[ERROR] Faltan archivos por cargar.")
            return False

        try:
            self.escribir_consola("\n[!] Procesando información y cruzando listas...")
            
            # 1. Leer ambos archivos
            df_asesorias = pd.read_excel(ruta_asesorias)
            df_maestra = pd.read_excel(ruta_lista)
            
            # Buscar la columna que contenga la palabra 'correo' o 'dirección'
            col_correo = next((c for c in df_asesorias.columns if 'correo' in str(c).lower() or 'email' in str(c).lower()), None)
            
            if col_correo:
                # Tomamos el correo (ej. 323030001@upjr.edu.mx), lo partimos en el '@' y nos quedamos con la primera parte [0]
                df_asesorias['No. de control'] = df_asesorias[col_correo].astype(str).str.split('@').str[0].str.strip()
                self.escribir_consola("[*] Matrículas extraídas exitosamente de los correos.")
            else:
                self.escribir_consola("[ADVERTENCIA] No se encontró la columna de correo. Se buscará matrícula manual.")

            # 2. Buscar columnas dinámicamente
            col_ctrl_asesorias = next((c for c in df_asesorias.columns if 'control' in str(c).lower()), 'No. de control')
            col_ctrl_maestra = next((c for c in df_maestra.columns if 'control' in str(c).lower()), 'No. de control')
            col_estatus = next((c for c in df_maestra.columns if 'estatus' in str(c).lower()), 'Estatus')

            # 3. Limpieza avanzada 
            df_asesorias[col_ctrl_asesorias] = df_asesorias[col_ctrl_asesorias].astype(str).str.strip().str.replace(r'\.0$', '', regex=True).str.upper()
            df_maestra[col_ctrl_maestra] = df_maestra[col_ctrl_maestra].astype(str).str.strip().str.replace(r'\.0$', '', regex=True).str.upper()
            
            # Limpiar estatus a mayúsculas estrictas
            df_maestra[col_estatus] = df_maestra[col_estatus].astype(str).str.strip().str.upper()

            # 4. Solución a la inconsistencia del >100%
            total_asesorias = len(df_asesorias)
            df_unicos = df_asesorias.drop_duplicates(subset=[col_ctrl_asesorias])
            total_personas = len(df_unicos)

            # 5. Cruce de datos (Merge)
            df_cruce = pd.merge(df_maestra, df_unicos[[col_ctrl_asesorias]], 
                                left_on=col_ctrl_maestra, 
                                right_on=col_ctrl_asesorias, 
                                how='left', 
                                indicator=True)

            # 6. Cálculo de los 4 Indicadores
            tomo_acredito = ((df_cruce['_merge'] == 'both') & (df_cruce[col_estatus] == 'ACREDITADO')).sum()
            notomo_acredito = ((df_cruce['_merge'] == 'left_only') & (df_cruce[col_estatus] == 'ACREDITADO')).sum()
            tomo_noacredito = ((df_cruce['_merge'] == 'both') & (df_cruce[col_estatus] == 'NO ACREDITADO')).sum()
            notomo_noacredito = ((df_cruce['_merge'] == 'left_only') & (df_cruce[col_estatus] == 'NO ACREDITADO')).sum()

            # Imprimir resultados en la consola de Tkinter
            self.escribir_consola(f"[*] Asesorías totales: {total_asesorias} | Personas únicas: {total_personas}")
            self.escribir_consola("--- INDICADORES DE ACREDITACIÓN ---")
            self.escribir_consola(f"1. Tomó asesoría y acreditó: {tomo_acredito}")
            self.escribir_consola(f"2. No tomó asesoría y acreditó: {notomo_acredito}")
            self.escribir_consola(f"3. Tomó asesoría y no acreditó: {tomo_noacredito}")
            self.escribir_consola(f"4. No tomó asesoría y no acreditó: {notomo_noacredito}")

            # Guardar el DataFrame limpio para que generador_pdf lo pueda consumir
            self.df_asesorias_limpio = df_asesorias
            self.df_maestra = df_maestra 
            self.escribir_consola("\n[OK] Análisis completado. Listo para exportar PDFs.")
            return True
            
        except KeyError as e:
            self.escribir_consola(f"[ERROR] No se encontró una columna vital: {str(e)}")
            return False
        except Exception as e:
            self.escribir_consola(f"[ERROR FATAL] {str(e)}")
            return False