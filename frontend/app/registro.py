"""
Módulo para registrar descargas de facturas
Mantiene un registro en JSON de cada factura descargada
"""

import json
import os
from datetime import datetime
from pathlib import Path


class RegistroDescargas:
    def __init__(self, archivo_registro='descargas.json'):
        """
        Inicializa el registro de descargas
        
        Args:
            archivo_registro: Nombre del archivo donde se guardará el registro
        """
        self.archivo_registro = archivo_registro
        self.ruta_archivo = Path(archivo_registro)
        self._crear_archivo_si_no_existe()
    
    def _crear_archivo_si_no_existe(self):
        """Crea el archivo de registro si no existe"""
        if not self.ruta_archivo.exists():
            self._guardar_json({
                "metadata": {
                    "version": "1.0",
                    "fecha_creacion": datetime.now().isoformat(),
                    "descripcion": "Registro de facturas descargadas"
                },
                "descargas": []
            })
    
    def _cargar_json(self):
        """Carga el contenido del archivo JSON"""
        try:
            with open(self.ruta_archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                "metadata": {
                    "version": "1.0",
                    "fecha_creacion": datetime.now().isoformat(),
                    "descripcion": "Registro de facturas descargadas"
                },
                "descargas": []
            }
    
    def _guardar_json(self, datos):
        """Guarda datos en el archivo JSON con formato indentado"""
        with open(self.ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    
    def registrar_descarga(self, id_factura, ip_cliente, estado='exitosa', detalles=None):
        """
        Registra una descarga de factura
        
        Args:
            id_factura: ID de la factura descargada
            ip_cliente: IP del cliente que descargó
            estado: Estado de la descarga ('exitosa', 'error', etc.)
            detalles: Diccionario con información adicional
        
        Returns:
            bool: True si se registró correctamente
        """
        try:
            datos = self._cargar_json()
            
            registro = {
                "id_factura": id_factura,
                "fecha_hora": datetime.now().isoformat(),
                "ip_cliente": ip_cliente,
                "estado": estado,
                "detalles": detalles or {}
            }
            
            datos["descargas"].append(registro)
            datos["metadata"]["ultima_actualizacion"] = datetime.now().isoformat()
            datos["metadata"]["total_descargas"] = len(datos["descargas"])
            
            self._guardar_json(datos)
            return True
        except Exception as e:
            print(f"Error al registrar descarga: {str(e)}")
            return False
    
    def obtener_historial(self):
        """
        Obtiene el historial completo de descargas
        
        Returns:
            list: Lista de descargas registradas
        """
        datos = self._cargar_json()
        return datos.get("descargas", [])
    
    def obtener_historial_por_factura(self, id_factura):
        """
        Obtiene el historial de descargas de una factura específica
        
        Args:
            id_factura: ID de la factura
        
        Returns:
            list: Lista de descargas para esa factura
        """
        historial = self.obtener_historial()
        return [desc for desc in historial if desc["id_factura"] == id_factura]
    
    def obtener_resumen(self):
        """
        Obtiene un resumen estadístico del registro
        
        Returns:
            dict: Estadísticas de descargas
        """
        datos = self._cargar_json()
        descargas = datos.get("descargas", [])
        
        total = len(descargas)
        exitosas = len([d for d in descargas if d["estado"] == "exitosa"])
        errores = len([d for d in descargas if d["estado"] == "error"])
        
        facturas_unicas = set(d["id_factura"] for d in descargas)
        ips_unicas = set(d["ip_cliente"] for d in descargas)
        
        return {
            "total_descargas": total,
            "descargas_exitosas": exitosas,
            "descargas_con_error": errores,
            "facturas_unicas": len(facturas_unicas),
            "ips_unicas": len(ips_unicas),
            "ultima_actualizacion": datos.get("metadata", {}).get("ultima_actualizacion"),
        }


# Instancia global del registro
registro_global = RegistroDescargas()
