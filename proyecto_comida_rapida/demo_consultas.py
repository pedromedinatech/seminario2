import os
import sqlite3
import json
from init_database import init_database
from consultas_negocio import ConsultasNegocio, CONSULTAS

def ejecutar_demo():
    """
    Script de demostración que ejecuta las consultas SQL y muestra los resultados.
    """
    # Verificar si existe la base de datos, si no, inicializarla
    db_path = os.path.join(os.path.dirname(__file__), 'restaurante_simulado.db')
    if not os.path.exists(db_path):
        print("Inicializando la base de datos...")
        init_database()
        print(f"Base de datos creada en: {db_path}")
    else:
        print(f"Usando base de datos existente: {db_path}")
    
    # Crear instancia de consultas
    consultas = ConsultasNegocio()
    
    # Ejecutar cada consulta y mostrar resultados para ChartJS
    print("\n" + "="*60)
    print("DEMOSTRACION DE CONSULTAS SQL PARA NEGOCIO DE COMIDA RÁPIDA")
    print("="*60)
    
    for key, info in CONSULTAS.items():
        print(f"\n\n{'#'*80}")
        print(f"# CONSULTA: {info['pregunta']}")
        print(f"# Descripción: {info['descripcion']}")
        print(f"{'#'*80}")
        
        # Mostrar SQL
        print("\nSQL:")
        print("-"*40)
        print(info['sql'])
        
        # Ejecutar consulta
        resultados, columnas = consultas.ejecutar_consulta(info['sql'])
        
        # Mostrar resultados en formato tabla
        if resultados:
            print("\nRESULTADOS:")
            print("-"*40)
            # Encabezados
            header = " | ".join(f"{col}" for col in columnas)
            print(header)
            print("-" * len(header))
            
            # Filas
            for fila in resultados:
                print(" | ".join(f"{val}" for val in fila))
        else:
            print("\nNo se encontraron resultados.")
        
        # Formatear para ChartJS
        chart_data = consultas.formatear_para_chartjs(resultados, columnas)
        
        # Mostrar formato para ChartJS
        print("\nJSON PARA CHARTJS:")
        print("-"*40)
        print(json.dumps(chart_data, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    print("FIN DE LA DEMOSTRACIÓN")
    print("="*60)

if __name__ == "__main__":
    ejecutar_demo() 