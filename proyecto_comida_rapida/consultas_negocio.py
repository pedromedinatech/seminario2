import sqlite3
import json
import os

# Ruta a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), 'restaurante_simulado.db')

# Clase para manejar las consultas
class ConsultasNegocio:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
    
    def ejecutar_consulta(self, consulta):
        """
        Ejecuta una consulta SQL y devuelve los resultados
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(consulta)
            resultados = cursor.fetchall()
            # Obtener nombres de columnas
            column_names = [description[0] for description in cursor.description]
            conn.close()
            return resultados, column_names
        except Exception as e:
            print(f"Error al ejecutar consulta: {e}")
            return [], []
    
    def formatear_para_chartjs(self, resultados, column_names):
        """
        Formatea los resultados para ChartJS (labels y values)
        """
        if not resultados or len(resultados[0]) < 2:
            return {"labels": [], "values": []}
        
        labels = [row[0] for row in resultados]
        values = [row[1] for row in resultados]
        
        return {
            "labels": labels,
            "values": values
        }

# Diccionario con las consultas SQL para cada pregunta de negocio
CONSULTAS = {
    "productos_stock_critico": {
        "pregunta": "¿Qué productos están en riesgo de agotarse esta semana?",
        "sql": """
        SELECT p.name AS Producto, sq.quantity_available AS Stock
        FROM stock_quant sq
        JOIN product_template p ON sq.product_id = p.id
        WHERE sq.quantity_available <= 5 AND sq.quantity_available > 0 AND p.is_active = 1
        ORDER BY sq.quantity_available ASC;
        """,
        "descripcion": "Muestra los productos activos con stock bajo (menor a 5 unidades)"
    },
    
    "productos_mas_rentables": {
        "pregunta": "¿Cuál es el producto más rentable?",
        "sql": """
        SELECT p.name AS Producto, 
               ROUND(((p.list_price - p.cost_price) / p.cost_price) * 100, 2) AS MargenPorcentaje
        FROM product_template p
        WHERE p.is_active = 1
        ORDER BY ((p.list_price - p.cost_price) / p.cost_price) DESC
        LIMIT 10;
        """,
        "descripcion": "Muestra los 10 productos activos con mayor margen de beneficio en porcentaje"
    },
    
    "categorias_mayor_ingreso": {
        "pregunta": "¿Cuáles son las categorías que generan más ingresos?",
        "sql": """
        SELECT p.category AS Categoría, 
               ROUND(SUM(sol.quantity * sol.price_unit), 2) AS TotalVentas
        FROM sale_order_line sol
        JOIN product_template p ON sol.product_id = p.id
        JOIN sale_order so ON sol.order_id = so.id
        GROUP BY p.category
        ORDER BY TotalVentas DESC;
        """,
        "descripcion": "Muestra las categorías de productos ordenadas por el total de ventas generadas"
    },
    
    "pedidos_por_ciudad": {
        "pregunta": "¿Cuántos pedidos hemos recibido por ciudad?",
        "sql": """
        SELECT rp.city AS Ciudad, 
               COUNT(DISTINCT so.id) AS NumeroPedidos
        FROM sale_order so
        JOIN res_partner rp ON so.customer_name = rp.name
        GROUP BY rp.city
        ORDER BY NumeroPedidos DESC;
        """,
        "descripcion": "Muestra la cantidad de pedidos recibidos agrupados por ciudad"
    },
    
    "productos_sin_ventas": {
        "pregunta": "¿Qué productos se han dejado de vender en el último mes?",
        "sql": """
        SELECT p.name AS Producto, 
               sq.quantity_available AS StockDisponible
        FROM product_template p
        LEFT JOIN (
            SELECT product_id, COUNT(*) as num_ventas
            FROM sale_order_line sol
            JOIN sale_order so ON sol.order_id = so.id
            WHERE so.date_order LIKE '2025-04%'
            GROUP BY product_id
        ) ventas_recientes ON p.id = ventas_recientes.product_id
        JOIN stock_quant sq ON p.id = sq.product_id
        WHERE ventas_recientes.num_ventas IS NULL 
          AND p.is_active = 1 
          AND sq.quantity_available > 0
        ORDER BY p.name;
        """,
        "descripcion": "Muestra productos activos con stock que no han tenido ventas en abril (mes actual)"
    },
    
    "wraps_vendidos": {
        "pregunta": "¿Cuántos wraps se han vendido desde enero?",
        "sql": """
        SELECT p.name AS Producto, 
               SUM(sol.quantity) AS UnidadesVendidas
        FROM sale_order_line sol
        JOIN product_template p ON sol.product_id = p.id
        JOIN sale_order so ON sol.order_id = so.id
        WHERE p.category = 'wraps'
        GROUP BY p.id
        ORDER BY UnidadesVendidas DESC;
        """,
        "descripcion": "Muestra la cantidad de wraps vendidos agrupados por tipo de wrap"
    },
    
    "productos_mas_vendidos": {
        "pregunta": "¿Cuáles son los productos más vendidos?",
        "sql": """
        SELECT p.name AS Producto, 
               SUM(sol.quantity) AS CantidadVendida
        FROM sale_order_line sol
        JOIN product_template p ON sol.product_id = p.id
        GROUP BY p.id
        ORDER BY CantidadVendida DESC
        LIMIT 10;
        """,
        "descripcion": "Muestra los 10 productos más vendidos en general"
    },
    
    "ventas_por_mes": {
        "pregunta": "¿Cómo han evolucionado las ventas en los últimos meses?",
        "sql": """
        SELECT 
            substr(so.date_order, 1, 7) AS Mes,
            ROUND(SUM(so.total_amount), 2) AS TotalVentas
        FROM sale_order so
        GROUP BY substr(so.date_order, 1, 7)
        ORDER BY Mes;
        """,
        "descripcion": "Muestra la evolución de ventas por mes"
    },
    
    "clientes_destacados": {
        "pregunta": "¿Quiénes son nuestros mejores clientes?",
        "sql": """
        SELECT rp.name AS Cliente, 
               ROUND(SUM(so.total_amount), 2) AS TotalCompras
        FROM sale_order so
        JOIN res_partner rp ON so.customer_name = rp.name
        GROUP BY so.customer_name
        ORDER BY TotalCompras DESC
        LIMIT 10;
        """,
        "descripcion": "Muestra los 10 clientes que más han gastado en total"
    },
    
    "productos_alto_margen": {
        "pregunta": "¿Qué productos tienen mayor margen de beneficio en euros?",
        "sql": """
        SELECT p.name AS Producto, 
               ROUND(p.list_price - p.cost_price, 2) AS MargenEuros
        FROM product_template p
        WHERE p.is_active = 1
        ORDER BY (p.list_price - p.cost_price) DESC
        LIMIT 10;
        """,
        "descripcion": "Muestra los 10 productos con mayor margen de beneficio en euros"
    }
}

# Función para ejecutar todas las consultas y mostrar sus resultados
def ejecutar_todas_consultas():
    consultas = ConsultasNegocio()
    resultados = {}
    
    for key, info in CONSULTAS.items():
        print(f"\n=== {info['pregunta']} ===")
        print(f"Descripción: {info['descripcion']}")
        
        # Ejecutar consulta
        datos, columnas = consultas.ejecutar_consulta(info['sql'])
        
        # Mostrar consulta SQL
        print(f"\nConsulta SQL:")
        print(info['sql'])
        
        # Mostrar resultados en formato tabla
        if datos:
            print("\nResultados:")
            print("-" * 50)
            print(" | ".join(columnas))
            print("-" * 50)
            for fila in datos[:5]:  # Mostrar solo las primeras 5 filas
                print(" | ".join(str(valor) for valor in fila))
            if len(datos) > 5:
                print(f"... (y {len(datos) - 5} filas más)")
        else:
            print("No se encontraron resultados.")
        
        # Formatear para ChartJS
        chart_data = consultas.formatear_para_chartjs(datos, columnas)
        resultados[key] = chart_data
        
        # Mostrar formato para ChartJS
        print("\nFormato para ChartJS:")
        print(json.dumps(chart_data, indent=2, ensure_ascii=False))
    
    return resultados

if __name__ == "__main__":
    ejecutar_todas_consultas() 