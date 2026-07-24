import json
import os

class ManejadorConfiguracion:
    def __init__(self):
        # 1. Rutas del sistema (Ocultas al usuario)
        self.directorio_base = os.path.dirname(os.path.abspath(__file__))
        self.archivo_config = os.path.join(self.directorio_base, "config_encabezado.json")
        
        self.carpeta_assets = os.path.join(self.directorio_base, "assets")
        os.makedirs(self.carpeta_assets, exist_ok=True)

        # 2. Ruta de salida de reportes (Lo que ve el usuario en Documentos)
        # ESTO FALTABA: Le dice al programa dónde guardar los PDFs
        self.carpeta_documentos = os.path.join(os.path.expanduser("~"), "Documents")
        self.carpeta_reportes = os.path.join(self.carpeta_documentos, "Sistema_Asesorias_UPJR")
        
        # Crea la carpeta de reportes en Documentos si no existe
        os.makedirs(self.carpeta_reportes, exist_ok=True)

        # 3. Cargar datos
        self.config_data = self.cargar_configuracion()

    def cargar_configuracion(self):
        default_config = {
            "titulo": "Registro de Asesorías Académicas",
            "codigo": "F-SGC-XX",
            "emision": "Mayo 2026",
            "revision": "00",
            "periodo": "Mayo - Agosto 2026",
            "logo_izq": os.path.join(self.carpeta_assets, "GTO_EDU.png"),
            "logo_cen": os.path.join(self.carpeta_assets, "UPJR.png"),
            "logo_der": os.path.join(self.carpeta_assets, "EDU_MX.png")
        }

        if os.path.exists(self.archivo_config):
            try:
                with open(self.archivo_config, "r", encoding="utf-8") as f:
                    data_guardada = json.load(f)
                    default_config.update(data_guardada)
            except Exception as e:
                print(f"[ADVERTENCIA] No se pudo leer el archivo de configuración: {e}")
        
        return default_config

    def guardar_configuracion(self):
        try:
            with open(self.archivo_config, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] Al guardar la configuración: {e}")