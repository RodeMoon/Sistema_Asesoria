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
            self.escribir_consola("\n[!] Procesando información...")
            # Leer el archivo de asesorías
            df_asesorias = pd.read_excel(ruta_asesorias)
            
            # Buscar la columna de número de control y limpiarla
            col_ctrl_asesorias = next((c for c in df_asesorias.columns if 'control' in str(c).lower()), 'No. de control')
            df_asesorias[col_ctrl_asesorias] = df_asesorias[col_ctrl_asesorias].astype(str).str.strip().str.replace(r'\.0$', '', regex=True).str.upper()

            # Guardar el DataFrame limpio
            self.df_asesorias_limpio = df_asesorias
            self.escribir_consola("[OK] Análisis completado. Listo para exportar PDFs.")
            return True
            
        except Exception as e:
            self.escribir_consola(f"[ERROR] {str(e)}")
            return False