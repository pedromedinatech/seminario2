import sqlite3
import os
import logging

# Configurar el logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """
    Inicializa la base de datos con los datos simulados
    """
    # Comprobar si el archivo SQL existe
    sql_file_path = os.path.join(os.path.dirname(__file__), 'datos_simulados.sql')
    if not os.path.exists(sql_file_path):
        logger.error(f"No se encontró el archivo SQL: {sql_file_path}")
        return False
    
    # Nombre de la base de datos
    db_path = os.path.join(os.path.dirname(__file__), 'restaurante_simulado.db')
    
    # Eliminar la base de datos si ya existe
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info(f"Base de datos anterior eliminada: {db_path}")
    
    # Leer el contenido del archivo SQL
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Conectar a la base de datos y ejecutar el script
    try:
        conn = sqlite3.connect(db_path)
        conn.executescript(sql_script)
        conn.commit()
        logger.info(f"Base de datos inicializada correctamente: {db_path}")
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
        return False

if __name__ == "__main__":
    if init_database():
        logger.info("Base de datos lista para usar!")
    else:
        logger.error("No se pudo inicializar la base de datos.") 