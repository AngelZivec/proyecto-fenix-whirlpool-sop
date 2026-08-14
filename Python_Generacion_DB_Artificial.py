import pandas as pd

# ==========================================
# FASE 1: EXTRACCIÓN Y LIMPIEZA BASE
# ==========================================

# 1. Lectura y Codificación
ruta_archivo = r"G:\Mi unidad\Portafolio de Analisis\Proyectos\3\1- Informacion\compranet_historico.csv"
df = pd.read_csv(ruta_archivo, encoding='utf-8')

# 2. Limpieza de Fechas (Eliminamos las columnas redundantes)
df = df.drop(columns=['fecha_inicio', 'fecha_fin'])

# 3. Transformación de Fechas 
df['ff_fecha_inicio'] = pd.to_datetime(df['ff_fecha_inicio'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')
df['ff_fecha_fin'] = pd.to_datetime(df['ff_fecha_fin'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

# 4. Limpieza de Espacios Invisibles (Trim masivo)
# Buscamos todas las columnas que sean de texto ('object') y les quitamos los espacios extra
columnas_texto = df.select_dtypes(include=['object']).columns
for col in columnas_texto:
    df[col] = df[col].str.strip()

# Mostramos las primeras 5 filas para validar
print(df[['tipo_expediente', 'ff_fecha_inicio', 'ff_fecha_fin']].head())

# ==========================================
# FASE 2: ESTANDARIZACIÓN DE DICCIONARIOS
# ==========================================

# 1. Diccionario para limpiar 'contract_type'
# Usamos las palabras con acentos reales (Pública, Inversión) porque en la Fase 1 ya corregimos la codificación.
diccionario_contract = {
    "ADQUISICIONES_0": "1.Adquisiciones",
    "ADQUISICIONES_1": "1.Adquisiciones",
    "1109231.Adquisiciones": "1.Adquisiciones",
    "1109232.Arrendamientos": "2.Arrendamientos",
    "ARRENDAMIENTOS_1": "2.Arrendamientos",
    "ARRENDAMIENTOS_0": "2.Arrendamientos",
    "SERVICIOS-OP_0": "3.Servicios",
    "SERVICIOS_0": "3.Servicios",
    "SERVICIOS_1": "3.Servicios",
    "1109233.Servicios": "3.Servicios",
    "SERVICIOS-OP_1": "3.Servicios",
    "OBRA-PUBLICA_0": "4.Obra Publica",
    "4.Obra Pública 09012017": "4.Obra Publica",
    "1109234.Obra Pública": "4.Obra Publica",
    "OBRA-PUBLICA_1": "4.Obra Publica",
    "4.Obra Pública": "4.Obra Publica",
    "5.Servicios relacionados con la obra pública 09012017": "5.Servicios relacionados con la obra publica",
    "1109235.Servicios relacionados con la obra pública": "5.Servicios relacionados con la obra publica",
    "5.Servicios relacionados con la obra pública": "5.Servicios relacionados con la obra publica",
    "6. Programas y Proyectos de Inversión - Obra Pública": "6. Programas y Proyectos de Inversion - Obra Publica",
    "6. Programas y Proyectos de Inversión - Obra Pública_24042020": "6. Programas y Proyectos de Inversion - Obra Publica"
}

# Aplicamos el reemplazo directo a la columna completa
df['contract_type'] = df['contract_type'].replace(diccionario_contract)

# 2. Diccionario para condicionar 'tipo_contratacion' 
# Se basa estrictamente en los valores limpios que acabamos de generar arriba.
diccionario_tipo = {
    "1.Adquisiciones": "Adquisiciones",
    "2.Arrendamientos": "Arrendamientos",
    "3.Servicios": "Servicios",
    "4.Obra Publica": "Obra Publica",
    "5.Servicios relacionados con la obra publica": "Servicios relacionados con la obra publica",
    "6. Programas y Proyectos de Inversion - Obra Publica": "Programas y Proyectos de Inversion - Obra Publica"
}

# Usamos .map() para condicionar la columna 2 basándonos en la columna 1. 
# El .fillna() asegura que si hay un dato raro, no se borre lo que ya tenía.
df['tipo_contratacion'] = df['contract_type'].map(diccionario_tipo).fillna(df['tipo_contratacion'])

# 3. Validación Técnica (Auditoría visual)
# Usamos value_counts() para imprimir un conteo rápido y confirmar que todo se agrupó perfectamente.
print("--- Auditoría: Clasificaciones Finales de contract_type ---")
print(df['contract_type'].value_counts())


# ==========================================
# FASE 3: INYECCIÓN DE ANOMALÍAS Y EXPORTACIÓN
# ==========================================

# 1. Aseguramos que el importe sea numérico para poder aplicar reglas matemáticas (fraccionarlo)
df['importe'] = pd.to_numeric(df['importe'], errors='coerce').fillna(0)

# 2. Duplicados Exactos (Error de Sistema)
# Tomamos una muestra aleatoria del 1% y la copiamos tal cual.
df_exact = df.sample(frac=0.01, random_state=42).copy()

# 3. Duplicados Parciales (Error Humano / Dedo)
# Tomamos otro 1%. 
df_partial = df.sample(frac=0.01, random_state=123).copy()
# Le agregamos un guión al número de factura (codigo_contrato) para que el ERP no lo detecte.
df_partial['codigo_contrato'] = df_partial['codigo_contrato'].astype(str) + '-'
# Alteramos el nombre del proveedor poniéndolo todo junto y en mayúsculas (ej. "LimpiezaCego" vs "Limpieza Cego")
df_partial['proveedor'] = df_partial['proveedor'].str.upper().str.replace(' ', '')

# 4. Pagos Fraccionados (Evasión de Políticas de Aprobación)
# Tomamos un 1% y lo dividimos en dos registros idénticos pero con la mitad del dinero cada uno.
df_split_1 = df.sample(frac=0.01, random_state=99).copy()
df_split_2 = df_split_1.copy()
df_split_1['importe'] = df_split_1['importe'] / 2
df_split_2['importe'] = df_split_2['importe'] / 2

# 5. Consolidación de la Base de Datos
# Unimos la base limpia original con todas nuestras anomalías
df_final = pd.concat([df, df_exact, df_partial, df_split_1, df_split_2], ignore_index=True)

# Revolvemos los datos (shuffle) para que los fraudes no queden todos juntos al final de la tabla
df_final = df_final.sample(frac=1, random_state=1).reset_index(drop=True)

# 6. EXPORTACIÓN A TU GOOGLE DRIVE
ruta_salida = r"G:\Mi unidad\Portafolio de Analisis\Proyectos\3\1- Informacion\compranet_infectado.csv"
df_final.to_csv(ruta_salida, index=False, encoding='utf-8')

# Resumen de Auditoría
print("--- FASE 3 COMPLETADA ---")
print(f"Registros originales limpios: {len(df)}")
print(f"Registros totales (incluyendo fraudes): {len(df_final)}")
print(f"¡El archivo final ha sido exportado a tu carpeta con éxito!")

