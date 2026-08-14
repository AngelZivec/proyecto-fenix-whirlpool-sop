import pandas as pd
from sqlalchemy import create_engine
import urllib

# =======================================================
# FASE 1: GENERACIÓN Y CARGA DE DIM_PRODUCTO
# =======================================================

# 1. Creación del Catálogo Maestro (Reglas PIPO y Nomenclatura)
data_productos = [
    # PRODUCTOS ESTRELLA (Transición PIPO - Innovación 2026)
    ['W-R-1000', 'Whirlpool', 'Refrigeración', 'French Door', 'Phase Out', 'W-R-2026'],
    ['W-R-2026', 'Whirlpool', 'Refrigeración', 'French Door', 'Phase In', None],
    ['W-L-3000', 'Whirlpool', 'Lavado', 'Carga Frontal', 'Phase Out', 'W-L-2026'],
    ['W-L-2026', 'Whirlpool', 'Lavado', 'Carga Frontal', 'Phase In', None],
    ['K-R-5100', 'KitchenAid', 'Refrigeración', 'Bottom Mount', 'Phase Out', 'K-R-2026'],
    ['K-R-2026', 'KitchenAid', 'Refrigeración', 'Bottom Mount', 'Phase In', None],
    ['A-C-1000', 'Acros', 'Cocción', 'Estufa de Piso', 'Phase Out', 'A-C-2026'],
    ['A-C-2026', 'Acros', 'Cocción', 'Estufa de Piso', 'Phase In', None],
    
    # CATÁLOGO REGULAR (Volumen normal)
    ['W-R-3100', 'Whirlpool', 'Refrigeración', 'Top Mount', 'Regular', None],
    ['W-R-5200', 'Whirlpool', 'Refrigeración', 'Side by Side', 'Regular', None],
    ['W-L-1000', 'Whirlpool', 'Lavado', 'Carga Superior', 'Regular', None],
    ['W-L-3100', 'Whirlpool', 'Lavado', 'Secadora', 'Regular', None],
    ['W-L-5100', 'Whirlpool', 'Lavado', 'Centro de Lavado', 'Regular', None],
    ['W-C-3000', 'Whirlpool', 'Cocción', 'Estufa de Piso', 'Regular', None],
    ['A-C-5010', 'Acros', 'Cocción', 'Estufa de Piso', 'Regular', None],
    ['A-R-1000', 'Acros', 'Refrigeración', 'Top Mount', 'Regular', None],
    ['K-C-5100', 'KitchenAid', 'Cocción', 'Horno Empotrable', 'Regular', None],
    ['K-C-5200', 'KitchenAid', 'Cocción', 'Parrilla', 'Regular', None]
]

columnas = ['SKU', 'Marca', 'Categoria', 'Sub_Tipo', 'Estatus_PIPO', 'SKU_Reemplazo']
df_dim_producto = pd.DataFrame(data_productos, columns=columnas)

# Mostramos las primeras filas para validar la estructura visualmente
print("Vista previa de Dim_Producto:")
display(df_dim_producto.head(10))

# =======================================================
# FASE 2: CONEXIÓN E INYECCIÓN A SQL SERVER
# =======================================================

# 2. Configuración de credenciales de servidor
# Usamos el nombre exacto de tu equipo para evitar errores de autenticación de Windows
nombre_servidor = r'DESKTOP-QSCIA1E\SQLEXPRESS' 
nombre_bd = 'ProyectoFenix_SOP' 

# Usamos una cadena de conexión directa de SQLAlchemy (suele ser más estable)
string_conexion = f"mssql+pyodbc://@{nombre_servidor}/{nombre_bd}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"
engine = create_engine(string_conexion)

# 3. Volcado de datos
try:
    df_dim_producto.to_sql('Dim_Producto', con=engine, if_exists='replace', index=False)
    print("\n¡Éxito! La tabla 'Dim_Producto' se inyectó en SQL Server correctamente.")
except Exception as e:
    print(f"\nError de conexión o inyección: {e}")


import pandas as pd
import numpy as np
import random
from sqlalchemy import create_engine
import urllib

# =======================================================
# FASE 3: SIMULADOR DE PRODUCCIÓN E INYECCIÓN (FACT_PRODUCCION)
# =======================================================

# 1. Conexión a SQL Server (Reutilizamos tus credenciales)
nombre_servidor = r'DESKTOP-QSCIA1E\SQLEXPRESS'
nombre_bd = 'ProyectoFenix_SOP'
string_conexion = f"mssql+pyodbc://@{nombre_servidor}/{nombre_bd}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"
engine = create_engine(string_conexion)

# 2. Extraer Dim_Producto para tener los SKUs reales
df_dim = pd.read_sql("SELECT SKU, Marca, Categoria, Sub_Tipo FROM Dim_Producto", con=engine)

# 3. Parámetros del Histórico
num_registros = 12000 
fecha_inicio = pd.to_datetime('2021-08-01')
fecha_fin = pd.to_datetime('2026-08-07')

# Generar fechas aleatorias
fechas_aleatorias = fecha_inicio + (fecha_fin - fecha_inicio) * np.random.rand(num_registros)

# Crear el DataFrame base con SKUs aleatorios
df_fact = pd.DataFrame({
    'Fecha_Produccion': pd.Series(fechas_aleatorias).dt.normalize(),
    'SKU': np.random.choice(df_dim['SKU'], size=num_registros)
})

# Agregamos las columnas de tiempo extrayéndolas de la fecha
df_fact['Año'] = df_fact['Fecha_Produccion'].dt.year
df_fact['Mes'] = df_fact['Fecha_Produccion'].dt.month

# Hacemos un cruce (merge) temporal con Dim_Producto para saber qué es cada SKU
df_fact = df_fact.merge(df_dim, on='SKU', how='left')

# 4. Lógica de Negocio: Vocación Productiva
def asignar_origen(row):
    cat = row['Categoria']
    marca = row['Marca']
    sub = row['Sub_Tipo']
    
    if cat == 'Cocción':
        if marca == 'KitchenAid': 
            return pd.Series(['Italia', 'Cassinetta', 'EMEA'])
        else: 
            return pd.Series(['México', 'Celaya', 'NAR'])
            
    elif cat == 'Refrigeración':
        if sub == 'French Door': 
            return pd.Series(['Estados Unidos', 'Amana', 'NAR'])
        else: 
            # Repartimos el volumen Core entre México y Brasil
            opciones = [('México', 'Ramos Arizpe', 'NAR'), ('Brasil', 'Joinville', 'LARS')]
            return pd.Series(random.choice(opciones))
            
    elif cat == 'Lavado':
        # Repartimos entre México, EE.UU. y Colombia
        if sub == 'Carga Superior' or sub == 'Secadora':
            return pd.Series(['Estados Unidos', 'Clyde', 'NAR'])
        else:
            opciones = [('México', 'Apodaca', 'NAR'), ('Colombia', 'Medellín', 'LARN')]
            return pd.Series(random.choice(opciones))

# Aplicamos la función para generar País, Planta y Macro Región
df_fact[['País_Producción', 'Planta_Origen', 'Macro_Region_Manufactura']] = df_fact.apply(asignar_origen, axis=1)

# Lógica para Región (Nacional vs Importado). Siendo LARN el mercado foco, MX y CO son Nacionales/Regionales
df_fact['Región'] = np.where(df_fact['País_Producción'].isin(['México', 'Colombia']), 'Nacional', 'Importado')

# 5. Lógica de Negocio: Parametrización Financiera
def asignar_costo(cat):
    if cat == 'Lavado': return round(random.uniform(150.0, 350.0), 2)
    elif cat == 'Refrigeración': return round(random.uniform(250.0, 650.0), 2)
    elif cat == 'Cocción': return round(random.uniform(120.0, 400.0), 2)

df_fact['Costo_Fabricacion_Unitario'] = df_fact['Categoria'].apply(asignar_costo)

# Generamos Unidades (Lotes entre 50 y 300 equipos) y Costo Total
df_fact['Unidades_Producidas'] = np.random.randint(50, 301, size=num_registros)
df_fact['Costo_Total_Produccion'] = df_fact['Unidades_Producidas'] * df_fact['Costo_Fabricacion_Unitario']

# Generamos el ID único de producción y ordenamos columnas
df_fact['ID_Produccion'] = 'PRD-' + df_fact.index.astype(str).str.zfill(5)
columnas_finales = [
    'ID_Produccion', 'Fecha_Produccion', 'Año', 'Mes', 'SKU', 
    'País_Producción', 'Planta_Origen', 'Región', 'Unidades_Producidas', 
    'Costo_Fabricacion_Unitario', 'Costo_Total_Produccion', 'Macro_Region_Manufactura'
]
df_fact_final = df_fact[columnas_finales].copy()

# Ordenar por fecha cronológicamente
df_fact_final = df_fact_final.sort_values('Fecha_Produccion').reset_index(drop=True)

# 6. Inyección a SQL Server
print("Inyectando 12,000 registros transaccionales en SQL Server...")
try:
    df_fact_final.to_sql('Fact_Produccion', con=engine, if_exists='replace', index=False)
    print("¡Éxito! La tabla 'Fact_Produccion' está lista y conectada a la Dimensión.")
    display(df_fact_final.head())
except Exception as e:
    print(f"Error: {e}")


import pandas as pd
import numpy as np
import random
from sqlalchemy import create_engine
import urllib

# =======================================================
# FASE 4: SIMULADOR DE VENTAS Y MÁRGENES (FACT_VENTAS)
# =======================================================

# 1. Conexión a SQL Server
nombre_servidor = r'DESKTOP-QSCIA1E\SQLEXPRESS'
nombre_bd = 'ProyectoFenix_SOP'
string_conexion = f"mssql+pyodbc://@{nombre_servidor}/{nombre_bd}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"
engine = create_engine(string_conexion)

print("Extrayendo dimensiones y costos base de Producción...")
# 2. Extraer Dim_Producto y el resumen de Produccion para cruzar costos y orígenes
df_dim = pd.read_sql("SELECT SKU, Estatus_PIPO FROM Dim_Producto", con=engine)
df_prod = pd.read_sql("""
    SELECT 
        SKU, 
        MAX(País_Producción) AS País_Origen, 
        AVG(Costo_Fabricacion_Unitario) AS Costo_Base 
    FROM Fact_Produccion 
    GROUP BY SKU
""", con=engine)

# Unimos todo en un maestro temporal
df_maestro = df_dim.merge(df_prod, on='SKU', how='inner')

# 3. Parámetros del Histórico de Ventas
num_ventas = 35000 
fecha_inicio = pd.to_datetime('2021-08-01')
fecha_fin = pd.to_datetime('2026-08-07')

fechas_aleatorias = fecha_inicio + (fecha_fin - fecha_inicio) * np.random.rand(num_ventas)

df_ventas = pd.DataFrame({
    'Fecha_Venta': pd.Series(fechas_aleatorias).dt.normalize(),
    'SKU': np.random.choice(df_maestro['SKU'], size=num_ventas)
})

df_ventas['Año'] = df_ventas['Fecha_Venta'].dt.year
df_ventas['Mes'] = df_ventas['Fecha_Venta'].dt.month

# Traemos la info de PIPO, Origen y Costo Base al dataframe de ventas
df_ventas = df_ventas.merge(df_maestro, on='SKU', how='left')

# 4. Lógica Comercial: Canales y Países Destino
paises_larn = ['Colombia', 'México', 'Perú', 'Ecuador', 'Guatemala']
df_ventas['País_Destino'] = np.random.choice(paises_larn, size=num_ventas)

def asignar_canal(row):
    canales = ['Retail', 'Home Centers', 'Mayoreo / Especializado', 'Exportación Intercompany']
    # Probabilidades sesgadas (más ventas en Retail y Mayoreo)
    canal = np.random.choice(canales, p=[0.4, 0.25, 0.3, 0.05])
    
    if canal == 'Retail':
        cuenta = random.choice(['Liverpool', 'Falabella', 'Almacenes Éxito'])
    elif canal == 'Home Centers':
        cuenta = random.choice(['The Home Depot', 'Sodimac', 'Easy'])
    elif canal == 'Mayoreo / Especializado':
        cuenta = random.choice(['Elektra', 'Coppel', 'Distribuidores Locales'])
    else:
        cuenta = 'N/A'
        
    return pd.Series([canal, cuenta])

df_ventas[['Canal_Venta', 'Key_Account']] = df_ventas.apply(asignar_canal, axis=1)

# 5. Lógica Financiera: El Secreto del Dashboard (Márgenes y Descuentos)
df_ventas['Unidades_Vendidas'] = np.random.randint(10, 150, size=num_ventas)

# Precio Lista = Costo Base * Multiplicador (1.8x a 2.5x)
df_ventas['Multiplicador'] = np.random.uniform(1.8, 2.5, size=num_ventas)
df_ventas['Precio_Lista'] = round(df_ventas['Costo_Base'] * df_ventas['Multiplicador'], 2)

# Descuentos agresivos basados en el Estatus PIPO
def aplicar_descuento(estatus):
    if estatus == 'Phase Out': return round(random.uniform(0.35, 0.55), 2) # ¡La crisis!
    elif estatus == 'Phase In': return 0.00 # Sin descuento
    else: return round(random.uniform(0.00, 0.15), 2) # Regular

df_ventas['%_Descuento_Aplicado'] = df_ventas['Estatus_PIPO'].apply(aplicar_descuento)

# Costo Logístico Unitario ($25 - $60)
df_ventas['Costo_Operacion_Logistica'] = np.round(np.random.uniform(25.0, 60.0, size=num_ventas), 2)

# 6. Cálculo del Margen Neto Total por Transacción
# Ingreso = (Precio Lista - Descuento) * Unidades
df_ventas['Precio_Final_Unitario'] = df_ventas['Precio_Lista'] * (1 - df_ventas['%_Descuento_Aplicado'])
df_ventas['Ingreso_Neto'] = df_ventas['Precio_Final_Unitario'] * df_ventas['Unidades_Vendidas']

# Egresos = (Costo Fabricación + Costo Logístico) * Unidades
df_ventas['Costo_Total_Operacion'] = (df_ventas['Costo_Base'] + df_ventas['Costo_Operacion_Logistica']) * df_ventas['Unidades_Vendidas']

# MARGEN NETO
df_ventas['Margen_Neto'] = round(df_ventas['Ingreso_Neto'] - df_ventas['Costo_Total_Operacion'], 2)

# 7. Limpieza final e Inyección a SQL
df_ventas['ID_Venta'] = 'VT-' + df_ventas.index.astype(str).str.zfill(6)

columnas_finales = [
    'ID_Venta', 'Fecha_Venta', 'Año', 'Mes', 'SKU', 'País_Origen', 'País_Destino',
    'Canal_Venta', 'Key_Account', 'Unidades_Vendidas', 'Precio_Lista', 
    '%_Descuento_Aplicado', 'Costo_Operacion_Logistica', 'Margen_Neto'
]
df_ventas_final = df_ventas[columnas_finales].copy()
df_ventas_final = df_ventas_final.sort_values('Fecha_Venta').reset_index(drop=True)

print("Inyectando 35,000 registros de ventas en SQL Server...")
try:
    df_ventas_final.to_sql('Fact_Ventas', con=engine, if_exists='replace', index=False)
    print("¡Éxito! La tabla 'Fact_Ventas' se inyectó con todos los cálculos financieros.")
    display(df_ventas_final.head())
except Exception as e:
    print(f"Error: {e}")

import pandas as pd
import numpy as np
import random
from sqlalchemy import create_engine
import urllib

# =======================================================
# FASE 5: SIMULADOR DE INVENTARIO Y ALMACENAJE (FACT_INVENTARIO)
# =======================================================

# 1. Conexión a SQL Server
nombre_servidor = r'DESKTOP-QSCIA1E\SQLEXPRESS'
nombre_bd = 'ProyectoFenix_SOP'
string_conexion = f"mssql+pyodbc://@{nombre_servidor}/{nombre_bd}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"
engine = create_engine(string_conexion)

print("Extrayendo dimensiones y costos para valorizar el inventario...")
# 2. Extraer Dim_Producto y el Costo Base de Producción
df_dim = pd.read_sql("SELECT SKU, Estatus_PIPO, Categoria FROM Dim_Producto", con=engine)
df_prod = pd.read_sql("SELECT SKU, AVG(Costo_Fabricacion_Unitario) AS Costo_Base FROM Fact_Produccion GROUP BY SKU", con=engine)
df_maestro = df_dim.merge(df_prod, on='SKU', how='inner')

# 3. Parámetros del Histórico (Cortes Semanales de los últimos 12 meses)
fechas_corte = pd.date_range(start='2025-08-01', end='2026-08-07', freq='W-FRI')
registros_inv = []

# Generamos múltiples lotes de inventario por cada SKU en cada semana
for fecha in fechas_corte:
    for _, row in df_maestro.iterrows():
        # Entre 2 y 6 lotes reportados por SKU cada viernes
        num_lotes = random.randint(2, 6)
        for _ in range(num_lotes):
            registros_inv.append({
                'Fecha_Corte_Semanal': fecha,
                'SKU': row['SKU'],
                'Estatus_PIPO': row['Estatus_PIPO'],
                'Categoria': row['Categoria'],
                'Costo_Base': row['Costo_Base']
            })

df_inv = pd.DataFrame(registros_inv)
df_inv['Año'] = df_inv['Fecha_Corte_Semanal'].dt.year
df_inv['Mes'] = df_inv['Fecha_Corte_Semanal'].dt.month

# 4. Lógica Maestra: "El Truco" del Caso Fénix
def asignar_red_logistica(estatus_pipo):
    # REGLA 1: Phase Out (90% atascado en CD listo para remate)
    if estatus_pipo == 'Phase Out':
        if random.random() < 0.90:
            tipo = 'Centro de Distribución (CD)'
            pais = random.choice(['México', 'Colombia', 'Perú', 'Ecuador', 'Guatemala'])
            estatus = 'Disponible'
        else:
            tipo = 'Planta de Manufactura'
            pais = random.choice(['EE.UU.', 'Colombia', 'México', 'Brasil', 'Italia'])
            estatus = 'En Tránsito'
            
    # REGLA 2: Phase In (85% atorado en Planta o Cuarentena)
    elif estatus_pipo == 'Phase In':
        if random.random() < 0.85:
            tipo = 'Planta de Manufactura'
            pais = random.choice(['EE.UU.', 'Colombia', 'México', 'Brasil', 'Italia'])
            estatus = random.choice(['Cuarentena / Bloqueado', 'En Tránsito'])
        else:
            tipo = 'Centro de Distribución (CD)'
            pais = random.choice(['México', 'Colombia', 'Perú', 'Ecuador', 'Guatemala'])
            estatus = 'Disponible'
            
    # REGLA 3: Regular (Flujo logístico normal y sano)
    else:
        if random.random() < 0.65:
            tipo = 'Centro de Distribución (CD)'
            pais = random.choice(['México', 'Colombia', 'Perú', 'Ecuador', 'Guatemala'])
            estatus = 'Disponible'
        else:
            tipo = 'Planta de Manufactura'
            pais = random.choice(['EE.UU.', 'Colombia', 'México', 'Brasil', 'Italia'])
            estatus = random.choice(['En Tránsito', 'Disponible'])
            
    return pd.Series([tipo, pais, estatus])

# Aplicamos las reglas de distribución
df_inv[['Tipo_Ubicación', 'País_Ubicación', 'Estatus_Inventario']] = df_inv['Estatus_PIPO'].apply(asignar_red_logistica)

# 5. Lógica Financiera: Volumetría y Costo de Almacenaje
df_inv['Unidades_Fisicas'] = np.random.randint(50, 600, size=len(df_inv))
# Dinero inmovilizado = Unidades * Lo que costó fabricarlas
df_inv['Valor_Total_Inventario'] = np.round(df_inv['Unidades_Fisicas'] * df_inv['Costo_Base'], 2)

# El costo de almacenaje es más alto en CD y para productos grandes (Refrigeración)
def calcular_almacenaje(row):
    costo_base = random.uniform(1.0, 3.5)
    if row['Tipo_Ubicación'] == 'Centro de Distribución (CD)':
        costo_base += 2.0  # El metro cuadrado en CD logístico es más caro
    if row['Categoria'] == 'Refrigeración':
        costo_base += 3.5  # Penalización por volumen (aire)
    return round(costo_base, 2)

df_inv['Costo_Almacenaje_Unitario'] = df_inv.apply(calcular_almacenaje, axis=1)

# 6. Limpieza y formateo final
df_inv['ID_Corte'] = 'INV-' + df_inv.index.astype(str).str.zfill(6)

columnas_finales = [
    'ID_Corte', 'Fecha_Corte_Semanal', 'Año', 'Mes', 'SKU', 
    'País_Ubicación', 'Tipo_Ubicación', 'Estatus_Inventario', 
    'Unidades_Fisicas', 'Costo_Almacenaje_Unitario', 'Valor_Total_Inventario'
]
df_inv_final = df_inv[columnas_finales].copy()
df_inv_final = df_inv_final.sort_values(['Fecha_Corte_Semanal', 'SKU']).reset_index(drop=True)

print(f"Inyectando {len(df_inv_final)} registros de inventario en SQL Server...")
try:
    df_inv_final.to_sql('Fact_Inventario', con=engine, if_exists='replace', index=False)
    print("¡Éxito! La tabla 'Fact_Inventario' se inyectó aplicando las reglas de crisis.")
    display(df_inv_final.head())
except Exception as e:
    print(f"Error: {e}")

import pandas as pd
import numpy as np
import random
from sqlalchemy import create_engine

# =======================================================
# FASE 6: SIMULADOR DE CAPTURA OPERATIVA (STAGING_EXCEL)
# =======================================================

# 1. Conexión a SQL Server
nombre_servidor = r'DESKTOP-QSCIA1E\SQLEXPRESS'
nombre_bd = 'ProyectoFenix_SOP'
string_conexion = f"mssql+pyodbc://@{nombre_servidor}/{nombre_bd}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"
engine = create_engine(string_conexion)

print("Extrayendo catálogo de productos para la validación cruzada...")
# Extraemos el catálogo real para conectar las listas desplegables
df_dim = pd.read_sql("SELECT SKU, Estatus_PIPO FROM Dim_Producto", con=engine)

# 2. Parámetros de la simulación de reportes semanales
num_registros = 22000
fechas = pd.date_range(start='2025-08-01', end='2026-08-07', freq='W-FRI')
paises = ['México', 'Colombia', 'Perú', 'Ecuador', 'Guatemala']
cuentas = ['Liverpool', 'Falabella', 'Almacenes Éxito', 'The Home Depot', 'Sodimac', 'Easy', 'Elektra', 'Coppel', 'Wal-Mart']

# Generación aleatoria inicial del reporte operativo
df_staging = pd.DataFrame({
    'Fecha_Reporte': np.random.choice(fechas, size=num_registros),
    'País_Reporta': np.random.choice(paises, size=num_registros),
    'SKU_Reportado': np.random.choice(df_dim['SKU'], size=num_registros),
    'Key_Account': np.random.choice(cuentas, size=num_registros)
})

# Cruzamos para alinear el estatus PIPO real del SKU
df_staging = df_staging.merge(df_dim, left_on='SKU_Reportado', right_on='SKU', how='left').drop(columns=['SKU'])

# 3. Creación de la Llave Primaria Compuesta (Evita duplicados exactos)
df_staging['Llave_Primaria_Compuesta'] = (
    df_staging['Fecha_Reporte'].dt.strftime('%Y%m%d') + '_' +
    df_staging['País_Reporta'] + '_' +
    df_staging['SKU_Reportado'] + '_' +
    df_staging['Key_Account']
)

# Eliminamos duplicados generados por azar para mantener la integridad de la llave
df_staging = df_staging.drop_duplicates(subset=['Llave_Primaria_Compuesta']).reset_index(drop=True)

# 4. Lógica del Drama Operativo (Phase Out vs Phase In)
def aplicar_drama_staging(row):
    estatus = row['Estatus_PIPO']
    
    if estatus == 'Phase Out':
        # Inventario bajo en piso porque se está liquidando a marchas forzadas
        inv = random.randint(5, 35)
        sell_out = random.randint(70, 180)
        precio = round(random.uniform(300, 800), 2)
        desc = round(random.uniform(0.35, 0.55), 2) # Descuentos agresivos (35% - 55%)
        codif = 'Sí'
        
    elif estatus == 'Phase In':
        # Inventario casi nulo y el drama de la falta de codificación
        inv = random.randint(0, 4)
        sell_out = random.randint(0, 5)
        precio = round(random.uniform(600, 1300), 2)
        desc = 0.00
        # 75% de probabilidad de que la tienda aún no lo dé de alta ('No')
        codif = np.random.choice(['Sí', 'No'], p=[0.25, 0.75])
        
    else: # Regular
        inv = random.randint(20, 90)
        sell_out = random.randint(25, 55)
        precio = round(random.uniform(400, 1000), 2)
        desc = round(random.uniform(0.00, 0.15), 2)
        codif = 'Sí'
        
    return pd.Series([inv, sell_out, precio, desc, codif])

df_staging[['Inventario_Piso_Venta', 'Unidades_Sell_Out', 'Precio_Venta_Publico_Real', '%_Descuento_Aplicado', 'Codificacion_Activa']] = df_staging.apply(aplicar_drama_staging, axis=1)

# Formatear la fecha para SQL
df_staging['Fecha_Reporte'] = pd.to_datetime(df_staging['Fecha_Reporte']).dt.date

# 5. Ordenamiento y Estructura Final
columnas_finales = [
    'Llave_Primaria_Compuesta', 'Fecha_Reporte', 'País_Reporta', 'SKU_Reportado', 
    'Estatus_PIPO', 'Key_Account', 'Inventario_Piso_Venta', 'Unidades_Sell_Out', 
    'Precio_Venta_Publico_Real', '%_Descuento_Aplicado', 'Codificacion_Activa'
]
df_staging_final = df_staging[columnas_finales].copy()

# 6. Inyección a SQL Server
print(f"Inyectando {len(df_staging_final)} registros de Staging en SQL Server...")
try:
    df_staging_final.to_sql('Staging_Captura_Excel', con=engine, if_exists='replace', index=False)
    print("¡Éxito total! La tabla 'Staging_Captura_Excel' está integrada al servidor.")
    display(df_staging_final.head())
except Exception as e:
    print(f"Error: {e}")


import pandas as pd
from sqlalchemy import create_engine

# =======================================================
# FASE 7: CREACIÓN DE LA DIMENSIÓN CALENDARIO (DIM_CALENDARIO)
# =======================================================

# 1. Conexión a SQL Server
nombre_servidor = r'DESKTOP-QSCIA1E\SQLEXPRESS'
nombre_bd = 'ProyectoFenix_SOP'
string_conexion = f"mssql+pyodbc://@{nombre_servidor}/{nombre_bd}?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"
engine = create_engine(string_conexion)

print("Generando rango de fechas maestro...")
# 2. Definir el rango temporal que cubre todo el histórico (2021-08-01 a 2026-08-07)
fechas = pd.date_range(start='2021-08-01', end='2026-08-07', freq='D')

# 3. Construir el DataFrame con atributos de tiempo avanzados
df_calendario = pd.DataFrame({'Fecha': fechas})
df_calendario['Fecha_Key'] = df_calendario['Fecha'].dt.strftime('%Y%m%d').astype(int)
df_calendario['Año'] = df_calendario['Fecha'].dt.year
df_calendario['Mes'] = df_calendario['Fecha'].dt.month
df_calendario['Nombre_Mes'] = df_calendario['Fecha'].dt.strftime('%B')
df_calendario['Trimestre'] = 'Q' + df_calendario['Fecha'].dt.quarter.astype(str)
df_calendario['Semana_Anio'] = df_calendario['Fecha'].dt.isocalendar().week.astype(int)
df_calendario['Dia_Semana'] = df_calendario['Fecha'].dt.strftime('%A')
df_calendario['Es_Fin_Semana'] = df_calendario['Fecha'].dt.dayofweek.isin([5, 6]).map({True: 'Sí', False: 'No'})

# Formatear la fecha para SQL Server
df_calendario['Fecha'] = pd.to_datetime(df_calendario['Fecha']).dt.date

# Reordenar columnas para una estructura relacional limpia
columnas_finales = [
    'Fecha_Key', 'Fecha', 'Año', 'Mes', 'Nombre_Mes', 
    'Trimestre', 'Semana_Anio', 'Dia_Semana', 'Es_Fin_Semana'
]
df_calendario_final = df_calendario[columnas_finales].copy()

# 4. Inyección a SQL Server
print(f"Inyectando {len(df_calendario_final)} registros en la tabla 'Dim_Calendario'...")
try:
    df_calendario_final.to_sql('Dim_Calendario', con=engine, if_exists='replace', index=False)
    print("¡Éxito total! La tabla 'Dim_Calendario' está creada y lista en el servidor.")
    display(df_calendario_final.head())
except Exception as e:
    print(f"Error: {e}")

