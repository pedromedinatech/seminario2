from flask import Flask, request, jsonify, render_template
import logging
import os
import requests
import json
import sqlite3
from dotenv import load_dotenv
from init_database import init_database

# Configurar el logging para ver información en la consola
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde archivo .env si existe
load_dotenv()

# Configurar la API key de OpenAI
# Se puede definir en variable de entorno OPENAI_API_KEY o directamente aquí
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.warning("No se encontró API key de OpenAI en variables de entorno")
    # Descomentar y configurar directamente si es necesario
    # OPENAI_API_KEY = "tu-api-key-aquí"

# Crear la aplicación Flask
app = Flask(__name__)

# Ruta a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), 'restaurante_simulado.db')

# Funciones para inicializar la base de datos
def setup_database():
    """Inicializar la base de datos"""
    if not os.path.exists(DB_PATH):
        init_database()
        logger.info("Base de datos inicializada correctamente")

# Inicializar la base de datos al inicio
with app.app_context():
    setup_database()

@app.route('/')
def index():
    """Renderiza la página principal con el formulario de consulta."""
    return render_template('index.html')

@app.route('/consulta', methods=['POST'])
def procesar_consulta():
    """
    Endpoint que recibe una pregunta en lenguaje natural, la envía a la API de OpenAI
    para transformarla en una consulta SQL, y devuelve el resultado.
    """
    try:
        # Obtener datos del request
        data = request.get_json()
        
        # Verificar que la solicitud contiene una pregunta
        if not data or 'question' not in data:
            return jsonify({'error': 'Se requiere una pregunta'}), 400
        
        user_question = data['question']
        logger.info(f"Pregunta recibida: {user_question}")
        
        # Generar la consulta SQL usando OpenAI
        sql_query = generate_sql_from_question(user_question)
        
        # Registrar la consulta SQL generada
        logger.info(f"Consulta SQL generada: {sql_query}")
        
        # Ejecutar la consulta y obtener resultados
        try:
            results = execute_sql_query(sql_query)
            logger.info(f"Consulta ejecutada correctamente")
        except Exception as sql_error:
            logger.error(f"Error al ejecutar la consulta SQL: {str(sql_error)}")
            results = {
                "error": f"Error al ejecutar la consulta SQL: {str(sql_error)}"
            }
        
        # Preparar respuesta
        response = {
            'original_question': user_question,
            'sql_query': sql_query,
            'results': results,
            'status': 'success'
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error al procesar la consulta: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_sql_from_question(question):
    """
    Utiliza la API de OpenAI para transformar una pregunta en lenguaje natural
    en una consulta SQL válida.
    
    Args:
        question (str): La pregunta en lenguaje natural del usuario
        
    Returns:
        str: La consulta SQL generada por OpenAI
    """
    # Definir el esquema de la base de datos para el prompt
    db_schema = """
    Esquema de la base de datos de restaurante:
    
    Tabla: product_template
        - id INTEGER PRIMARY KEY
        - name TEXT (nombre del producto)
        - list_price REAL (precio de venta)
        - cost_price REAL (costo del producto)
        - category TEXT (categoría del producto)
        - is_active BOOLEAN (1 si está activo, 0 si está descontinuado)
    
    Tabla: sale_order
        - id INTEGER PRIMARY KEY
        - date_order TEXT (fecha del pedido en formato 'YYYY-MM-DD')
        - customer_name TEXT (nombre del cliente)
        - total_amount REAL (monto total del pedido)
    
    Tabla: sale_order_line
        - id INTEGER PRIMARY KEY
        - order_id INTEGER (id del pedido relacionado)
        - product_id INTEGER (id del producto vendido)
        - quantity INTEGER (cantidad vendida)
        - price_unit REAL (precio por unidad)
    
    Tabla: stock_quant
        - product_id INTEGER PRIMARY KEY
        - quantity_available INTEGER (cantidad disponible en stock)
    
    Tabla: res_partner
        - id INTEGER PRIMARY KEY
        - name TEXT (nombre del cliente o empresa)
        - email TEXT
        - city TEXT (ciudad)
        - number_of_orders INTEGER (número de pedidos realizados)
    
    Relaciones:
    - sale_order_line.order_id se relaciona con sale_order.id
    - sale_order_line.product_id se relaciona con product_template.id
    - stock_quant.product_id se relaciona con product_template.id
    - sale_order.customer_name se relaciona con res_partner.name

    Información relevante:
    - Se considera que un producto está en riesgo de agotarse cuando quantity_available <= 5 y es un producto activo (is_active = 1)
    - Los productos descontinuados tienen is_active = 0
    - Las categorías de productos incluyen: hamburguesas, wraps, patatas, bebidas, postres, complementos, promociones
    - Las fechas están en formato 'YYYY-MM-DD', siendo 2025-04 el mes actual (abril)
    - Las principales ciudades son: Madrid, Barcelona, Valencia, Sevilla
    """
    
    # Agregar ejemplos de consultas comunes
    query_examples = """
    Ejemplos de consultas SQL para preguntas comunes:
    
    1. Pregunta: "¿Qué productos están en riesgo de agotarse?"
       SQL: 
       SELECT p.name AS Producto, sq.quantity_available AS Stock
       FROM product_template p
       JOIN stock_quant sq ON p.id = sq.product_id
       WHERE sq.quantity_available <= 5 AND sq.quantity_available > 0 AND p.is_active = 1
       ORDER BY sq.quantity_available ASC;
    
    2. Pregunta: "¿Cuáles son los productos más vendidos?"
       SQL:
       SELECT p.name AS Producto, SUM(sol.quantity) AS TotalVendido
       FROM product_template p
       JOIN sale_order_line sol ON p.id = sol.product_id
       GROUP BY p.id
       ORDER BY TotalVendido DESC
       LIMIT 10;
    
    3. Pregunta: "¿Qué categoría genera más ingresos?"
       SQL:
       SELECT p.category AS Categoría, ROUND(SUM(sol.quantity * sol.price_unit), 2) AS TotalVentas
       FROM product_template p
       JOIN sale_order_line sol ON p.id = sol.product_id
       GROUP BY p.category
       ORDER BY TotalVentas DESC;
       
    4. Pregunta: "Mostrar todas las órdenes de venta con su cliente y monto"
       SQL:
       SELECT so.id AS ID, so.date_order AS Fecha, so.customer_name AS Cliente, so.total_amount AS Total
       FROM sale_order so
       ORDER BY so.date_order DESC
       LIMIT 15;
    """
    
    # Crear el prompt para OpenAI
    prompt = f"""
    {db_schema}
    
    {query_examples}
    
    Basándote en el esquema de la base de datos y los ejemplos anteriores, genera una consulta SQL válida para SQLite que responda a la siguiente pregunta: "{question}"
    
    Reglas importantes:
    1. Genera SOLO el código SQL, sin explicaciones ni comentarios adicionales.
    2. Para visualizaciones y gráficos, utiliza 2 columnas: una para etiquetas (textos descriptivos) y otra para valores numéricos.
    3. Para consultas que requieran mostrar múltiples datos o detalles, puedes utilizar más columnas.
    4. Usa alias claros para las columnas como "Producto", "Cantidad", "Ventas", etc.
    5. Si la consulta trata sobre riesgo de agotarse, usa el criterio quantity_available <= 5 para productos activos.
    6. Asegúrate de unir correctamente las tablas según las relaciones descritas.
    7. Limita los resultados a 15 filas si es una consulta que puede devolver muchos resultados.
    
    Genera únicamente la consulta SQL:
    """
    
    try:
        # Llamar a la API de OpenAI directamente con requests
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Eres un experto en SQLite que genera consultas SQL precisas para análisis de datos de restaurantes."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,  # Reducido para mayor precisión
            "max_tokens": 300
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        # Verificar que la respuesta fue exitosa
        response.raise_for_status()
        
        # Extraer la consulta SQL de la respuesta
        response_data = response.json()
        sql_query = response_data['choices'][0]['message']['content'].strip()
        return sql_query
        
    except Exception as e:
        logger.error(f"Error al llamar a la API de OpenAI: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                logger.error(f"Detalles del error: {error_detail}")
            except:
                logger.error(f"Código de estado HTTP: {e.response.status_code}")
        raise Exception(f"Error al generar consulta SQL: {str(e)}")

def execute_sql_query(sql_query):
    """
    Ejecuta una consulta SQL en la base de datos SQLite.
    
    Args:
        sql_query (str): La consulta SQL a ejecutar
        
    Returns:
        dict: Resultados de la consulta en formato adecuado para visualización
    """
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Ejecutar la consulta
        cursor.execute(sql_query)
        
        # Obtener resultados
        results = cursor.fetchall()
        
        # Obtener nombres de columnas
        column_names = [description[0] for description in cursor.description]
        
        # Cerrar conexión
        conn.close()
        
        # Si no hay resultados, devolver mensaje de error
        if not results:
            return {
                "error": "La consulta no devolvió resultados."
            }
        
        # Preparar el formato de respuesta
        formatted_results = {
            "columns": column_names,
            "rows": []
        }
        
        # Convertir los resultados a formato adecuado para tabla
        for row in results:
            formatted_row = {}
            for i, value in enumerate(row):
                formatted_row[column_names[i]] = value
            formatted_results["rows"].append(formatted_row)
        
        # Para consultas con exactamente 2 columnas, también preparar datos para gráfico
        if len(column_names) == 2 and all(isinstance(row[1], (int, float)) for row in results):
            formatted_results["labels"] = [str(row[0]) for row in results]
            formatted_results["values"] = [float(row[1]) if row[1] is not None else 0 for row in results]
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error al ejecutar la consulta SQL: {str(e)}")
        return {
            "error": f"Error al ejecutar la consulta: {str(e)}"
        }

if __name__ == '__main__':
    # Verificar que la API key está configurada
    if not OPENAI_API_KEY:
        logger.error("API key de OpenAI no configurada. Configure OPENAI_API_KEY en las variables de entorno o en el código.")
    
    # Iniciar el servidor Flask en modo debug
    app.run(debug=True) 