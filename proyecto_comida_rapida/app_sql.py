from flask import Flask, request, jsonify, render_template
import logging
import os
import json
import re
from consultas_negocio import CONSULTAS, ConsultasNegocio
from init_database import init_database

# Configurar el logging para ver información en la consola
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Crear la aplicación Flask
app = Flask(__name__)

# Funciones para inicializar la base de datos
def setup_database():
    """Inicializar la base de datos"""
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'restaurante_simulado.db')):
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
    Endpoint que recibe una pregunta en lenguaje natural, identifica la consulta SQL
    correspondiente y devuelve los resultados.
    """
    try:
        # Obtener datos del request
        data = request.get_json()
        
        # Verificar que la solicitud contiene una pregunta
        if not data or 'question' not in data:
            return jsonify({'error': 'Se requiere una pregunta'}), 400
        
        user_question = data['question']
        logger.info(f"Pregunta recibida: {user_question}")
        
        # Encontrar la consulta más similar en nuestro catálogo de consultas
        consulta_clave, consulta_info = encontrar_consulta_similar(user_question)
        
        if not consulta_clave:
            return jsonify({'error': 'No se pudo identificar una consulta adecuada para esta pregunta'}), 400
        
        # Extraer la consulta SQL
        sql_query = consulta_info['sql']
        
        # Registrar la consulta SQL identificada
        logger.info(f"Consulta SQL identificada: {consulta_clave}")
        logger.info(f"SQL: {sql_query}")
        
        # Ejecutar la consulta SQL
        consultas = ConsultasNegocio()
        resultados, columnas = consultas.ejecutar_consulta(sql_query)
        
        # Formatear resultados para ChartJS
        chart_data = consultas.formatear_para_chartjs(resultados, columnas)
        
        # Preparar respuesta
        response = {
            'original_question': user_question,
            'sql_query': sql_query,
            'results': chart_data,
            'status': 'success'
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error al procesar la consulta: {str(e)}")
        return jsonify({'error': str(e)}), 500

def encontrar_consulta_similar(pregunta):
    """
    Encuentra la consulta más similar a la pregunta del usuario
    
    Args:
        pregunta (str): La pregunta del usuario
        
    Returns:
        tuple: (key, info) de la consulta más similar
    """
    mejor_match = None
    mejor_puntuacion = -1
    
    pregunta = pregunta.lower()
    
    for key, info in CONSULTAS.items():
        # Puntuar similitud basada en palabras clave
        puntuacion = calcular_similitud(pregunta, info['pregunta'].lower())
        
        if puntuacion > mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_match = (key, info)
    
    # Si la puntuación es muy baja, no consideramos que haya match
    if mejor_puntuacion < 0.3:  # Umbral arbitrario
        return None, None
        
    return mejor_match

def calcular_similitud(texto1, texto2):
    """
    Calcula una similitud simple entre dos textos basada en palabras coincidentes
    
    Args:
        texto1 (str): Primer texto
        texto2 (str): Segundo texto
        
    Returns:
        float: Puntuación de similitud (0-1)
    """
    # Normalizar textos: convertir a minúsculas y eliminar signos de puntuación
    texto1 = re.sub(r'[^\w\s]', '', texto1.lower())
    texto2 = re.sub(r'[^\w\s]', '', texto2.lower())
    
    # Dividir en palabras
    palabras1 = set(texto1.split())
    palabras2 = set(texto2.split())
    
    # Calcular intersección
    palabras_comunes = palabras1.intersection(palabras2)
    
    # Si no hay palabras en alguno de los textos, la similitud es 0
    if not palabras1 or not palabras2:
        return 0
    
    # Fórmula de coeficiente de Jaccard
    return len(palabras_comunes) / (len(palabras1) + len(palabras2) - len(palabras_comunes))

@app.route('/consultas', methods=['GET'])
def listar_consultas():
    """
    Endpoint que lista todas las consultas disponibles
    """
    consultas_info = []
    for key, info in CONSULTAS.items():
        consultas_info.append({
            'id': key,
            'pregunta': info['pregunta'],
            'descripcion': info['descripcion']
        })
    
    return jsonify(consultas_info)

if __name__ == '__main__':
    # Iniciar el servidor Flask en modo debug
    app.run(debug=True) 