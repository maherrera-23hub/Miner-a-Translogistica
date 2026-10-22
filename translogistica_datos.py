import os
import io
from datetime import datetime
from sqlalchemy import create_engine, text
import pandas as pd
# ==========================================
# Configuración de los parámetros de conexión
# ==========================================
DB_HOST = "localhost"
DB_PORT = "3306"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "translogistica"

def conexion_pymysql():
    """
    Conexión directa utilizando pymysql
    """
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        print("Conexión exitosa con pymysql!")
        # Ejemplo de consulta de prueba
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"Versión de MySql: {version[0]}")
        conn.close()
        print("Conexión cerrada correctamente")
    except Exception as e:
        print(f"Error al conectar con pymysql: {e}")

def guardar_reportes(df: pd.DataFrame, nombre_tabla: str = "rutas"):
    """
    Crea la carpeta de salida y exporta los datos y resúmenes analizados.
    """
    carpeta_salida = "reportes"
    os.makedirs(carpeta_salida, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 1. Guardar los datos en CSV
    ruta_csv = os.path.join(carpeta_salida, f"{nombre_tabla}_datos.csv")
    df.to_csv(ruta_csv, index=False)
    print(f"\n📁 Datos guardados en: {ruta_csv}")
    # 2. Guardar el resumen estadístico (describe) en CSV
    ruta_stats = os.path.join(carpeta_salida, f"{nombre_tabla}_estadisticas.csv")
    df.describe().to_csv(ruta_stats)
    print(f"📊 Estadísticas guardadas en: {ruta_stats}")
    # 3. Capturar la salida de df.info() en memoria
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    # 4. Generar reporte consolidado en archivo de texto (.txt)
    ruta_txt = os.path.join(carpeta_salida, f"{nombre_tabla}_analisis.txt")
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"REPORTE DE EXPLORACIÓN DE DATOS - TABLA: {nombre_tabla.upper()}\n")
        f.write(f"Fecha de ejecución: {timestamp}\n")
        f.write(f"Dimensiones: {df.shape[0]} filas, {df.shape[1]} columnas\n")
        f.write("=" * 60 + "\n\n")
        f.write("1. COLUMNAS DISPONIBLES:\n")
        f.write("-" * 40 + "\n")
        f.write(str(df.columns.tolist()) + "\n\n")
        f.write("2. PRIMERAS 5 FILAS (df.head()):\n")
        f.write("-" * 40 + "\n")
        f.write(df.head().to_string() + "\n\n")
        f.write("3. INFORMACIÓN GENERAL Y TIPOS (df.info()):\n")
        f.write("-" * 40 + "\n")
        f.write(info_str + "\n\n")
        f.write("4. RESUMEN ESTADÍSTICO (df.describe()):\n")
        f.write("-" * 40 + "\n")
        f.write(df.describe().to_string() + "\n")
    print(f"📝 Reporte completo generado en: {ruta_txt}")

def conexion_sqlalchemy():
    """
    Conexión utilizando SQLAlchemy y lectura de datos con Pandas.
    Recomendado para minería de datos y análisis.
    """
    try:
        # Cadena de conexión URI
        database_url = (f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4")
        
        # Crear el motor de conexión (engine)
        engine = create_engine(database_url)
        with engine.connect() as connection:
            print("Conexión exitosa con SQLAlchemy!")
            
            # Prueba de consulta del estado de la conexión
            resultado = connection.execute(text("SELECT DATABASE(), CURRENT_USER();"))
            db_actual, usuario_actual = resultado.fetchone()
            print(f"📌 Base de datos actual: {db_actual} | Usuario: {usuario_actual}\n")
            # ==========================================
            # Ejemplo con Pandas
            # ==========================================
            consulta_sql = "SELECT * FROM rutas;"
            df = pd.read_sql_query(text(consulta_sql), con=connection)
            print("Primeras 5 filas del DataFrame (df.head()):")
            print("=" * 60)
            print(df.head())
            print("=" * 60)
            # ==========================================
            # Ejemplo con df.columns
            # ==========================================
            print("\nColumnas del DataFrame (df.columns):")
            print("=" * 60)
            print(df.columns)
            print("Lista de columnas:", df.columns.tolist()) # Convierte ese índice en una lista estándar de Python
            print("=" * 60)
            # ==========================================
            # Ejemplo con df.info()
            # ==========================================
            print("\nInformación general del DataFrame (df.info()):")
            print("=" * 60)
            df.info()  # Muestra tipos de datos, valores no nulos y uso de memoria
            print("=" * 60)
            # ==========================================
            # Ejemplo con df.describe()
            # ==========================================
            print("\nResumen estadístico de columnas numéricas (df.describe()):")
            print("=" * 60)
            print(df.describe())  # Media, desviación estándar, mín, máx, cuartiles
            print("=" * 60)
            print(f"\nTotal de filas y columnas: {df.shape}")
            # ==========================================
            # Exportar información a archivos y carpeta
            # ==========================================
            guardar_reportes(df, nombre_tabla="rutas")
        return engine
    except Exception as e:
        print(f"Error al conectar con SQLAlchemy: {e}")
        return None
if __name__ == "__main__":
    print("--- Probando conexión con SQLAlchemy y Pandas ---")
    conexion_sqlalchemy()
