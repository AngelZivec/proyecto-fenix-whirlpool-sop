📖 Diccionario de Medidas DAX: Auditoría Forense y Detección de Anomalías Financieras
A continuación, presento la documentación técnica y el racional de negocio del modelado DAX utilizado en el proyecto de auditoría de pagos duplicados. Este portafolio está diseñado para aislar vulnerabilidades, calcular el impacto a provisionar y priorizar la cobranza legal de manera dinámica.

📅 Bloque Fundacional: Inteligencia de Tiempo y Parámetros
📌 Modelado de Calendario y Dinamismo de Ejes

Dimensión Analítica = 
Row("Dimensión Analítica", BLANK(), "Dimensión Analítica Campos", BLANK(), "Dimensión Analítica Orden", BLANK())

Tasa de Recuperación Legal = 
// Tabla virtual generada para el simulador What-If (0% a 100% en pasos de 5%)
GENERATESERIES(0, 1, 0.05)

Calendario = 
// 1. Calculamos la fecha mínima real, ignorando cualquier error de captura (años 1900)
VAR FechaInicioReal = 
    CALCULATE(
        MIN('vw_Auditoria_Riesgo_Financiero'[fecha_inicio]), 
        YEAR('vw_Auditoria_Riesgo_Financiero'[fecha_inicio]) > 2000
    )

// 2. Calculamos la fecha máxima
VAR FechaFin = MAX('vw_Auditoria_Riesgo_Financiero'[fecha_inicio])

// 3. Generamos el calendario limpio
RETURN
ADDCOLUMNS(
    CALENDAR(FechaInicioReal, FechaFin),
    "Año", YEAR([Date]),
    "Mes Numero", MONTH([Date]),
    "Mes", FORMAT([Date], "MMMM"),
    "Año-Mes", FORMAT([Date], "YYYY-MM"),
    "Trimestre", "Q" & FORMAT([Date], "Q")
)

💡 Racional de Negocio: Una de las peores pesadillas en datos de facturación (ERP) son los "errores de dedo" al capturar fechas (ej. año 1900 en lugar de 2022). Diseñé este calendario dinámico anclando el inicio estrictamente a partir del año 2000. Esto asegura que la dimensión de tiempo sea compacta, el modelo pese menos y ninguna gráfica se rompa por culpa de fechas atípicas. Adicionalmente, integré parámetros de campo (Dimensión Analítica) y series generadas (Tasa de Recuperación Legal) para darle el control total al usuario sobre los ejes y simuladores del tablero.

💰 Bloque de Riesgo y Detección de Fugas (Diagnóstico)
📌 Cuantificación del Fraude y Volumetría Operativa

1.0 Monto Total Pagado = 
// Todo el dinero que salió del corporativo. Sumamos 0 para evitar blancos.
SUM('vw_Auditoria_Riesgo_Financiero'[monto_transaccion]) + 0

1.1 Monto en Riesgo = 
// Filtra exclusivamente el dinero que se pagó doble o múltiple gracias a la etiqueta que creamos en SQL.
VAR CalculoRiesgo = 
    CALCULATE(
        [1.0 Monto Total Pagado],
        'vw_Auditoria_Riesgo_Financiero'[clasificacion_riesgo] = "Fuga por Duplicidad"
    )
RETURN
    IF(CalculoRiesgo = 0, BLANK(), CalculoRiesgo)

1.2 % Fuga Financiera = 
// Qué porcentaje de nuestros pagos totales es dinero tirado a la basura. (Nuestro objetivo es que sea 0%).
DIVIDE([1.1 Monto en Riesgo], [1.0 Monto Total Pagado], 0)

1.6 Facturas en Riesgo = 
CALCULATE(
    COUNTROWS('vw_Auditoria_Riesgo_Financiero'),
    'vw_Auditoria_Riesgo_Financiero'[clasificacion_riesgo] = "Fuga por Duplicidad"
) + 0

2.1 Proveedores en Riesgo = 
CALCULATE(
    DISTINCTCOUNT('vw_Auditoria_Riesgo_Financiero'[proveedor]),
    'vw_Auditoria_Riesgo_Financiero'[clasificacion_riesgo] = "Fuga por Duplicidad"
) + 0

💡 Racional de Negocio: Este set de métricas separa la "operación sana" de la "operación fraudulenta". En lugar de auditar millones de registros a mano, aprovecho la clasificación previa hecha en SQL Server para aislar inmediatamente el capital fugado. El KPI % Fuga Financiera es crítico para la Dirección General, ya que dimensiona el tamaño del problema respecto a la facturación total. Por otro lado, contar las facturas y proveedores infractores me permite dimensionar el volumen de trabajo que tendrá el área legal.

📉 Bloque de Tendencias (YoY) y Comportamiento Histórico
📌 Comparativas de Rendimiento de Control Interno

1.3 Monto en Riesgo AA = 
CALCULATE(
    [1.1 Monto en Riesgo],
    SAMEPERIODLASTYEAR('Calendario'[Date])
) + 0

1.4 Gap de Riesgo (Monto) = 
[1.1 Monto en Riesgo] - [1.3 Monto en Riesgo AA]

1.5 % Variacion Riesgo YoY = 
DIVIDE(
    [1.4 Gap de Riesgo (Monto)], 
    [1.3 Monto en Riesgo AA], 
    0
)

1.7 Promedio Fuga Mensual = 
AVERAGEX(
    VALUES('Calendario'[Mes]),
    [1.1 Monto en Riesgo]
)

[Formato Condicional DAX para UI]
1.4.1 Color Gap Riesgo = 
SWITCH(
    TRUE(),
    [1.4 Gap de Riesgo (Monto)] < 0, "#00B050",   // Verde (El riesgo bajó)
    [1.4 Gap de Riesgo (Monto)] = 0, "#000000",   // Negro
    "#FF0000"                                     // Rojo (El riesgo subió)
)

1.5.1 Color % Variacion Riesgo YoY = 
SWITCH(
    TRUE(),
    [1.5 % Variacion Riesgo YoY] < 0, "#00B050",   
    [1.5 % Variacion Riesgo YoY] = 0, "#000000",   
    "#FF0000"                                     
)

💡 Racional de Negocio: Saber que perdimos 10 millones no sirve de mucho si no sabemos si estamos mejorando o empeorando frente al año pasado. Estas medidas YoY (Year-over-Year) le dicen a Cuentas por Pagar si los nuevos controles implementados están funcionando. Además, programé el código hexadecimal de los colores directamente en DAX (SWITCH TRUE); esto centraliza las reglas de negocio visuales, asegurando que si la fuga aumenta, las tarjetas y gráficas reaccionen automáticamente en color rojo sin tener que configurar el panel de formato de Power BI gráfico por gráfico.

⚖️ Bloque de Estrategia Legal y Simulación (S&OP)
📌 Proyección de Recuperación, Provisiones y Pareto Estratégico
3.1 Proyeccion de Recuperacion = 
// Calcula el dinero que regresará al banco según la meta del slider
[1.1 Monto en Riesgo] * [Valor de Tasa de Recuperación Legal]

3.2 Perdida Neta Irrecuperable = 
// Calcula el dinero que damos por perdido definitivamente y debe provisionarse
[1.1 Monto en Riesgo] - [3.1 Proyeccion de Recuperacion]

3.3 % Acumulado Pareto = 
// 1. Capturamos el valor del proveedor actual
VAR ValorActual = [3.1 Proyeccion de Recuperacion]

// 2. Tabla virtual ultrarrápida (solo evalúa a los que cometieron fraude)
VAR ProveedoresConFraude = 
    FILTER(
        ALLSELECTED('vw_Auditoria_Riesgo_Financiero'[proveedor]),
        [1.1 Monto en Riesgo] > 0
    )
    
// 3. Cálculo matemático aislado
VAR TotalRecuperacion = 
    CALCULATE([3.1 Proyeccion de Recuperacion], ProveedoresConFraude)
        
VAR SumaAcumulada = 
    SUMX(
        FILTER(
            ProveedoresConFraude,
            [3.1 Proyeccion de Recuperacion] >= ValorActual
        ),
        [3.1 Proyeccion de Recuperacion]
    )
        
// 4. SEGURO DE VIDA y Resultado Final
RETURN
    IF(
        ISBLANK(ValorActual) || ValorActual <= 0, 
        BLANK(), 
        DIVIDE(SumaAcumulada, TotalRecuperacion, BLANK())
    )

💡 Racional de Negocio: Este es el motor táctico del proyecto. Las medidas 3.1 y 3.2 conectan el riesgo bruto con el simulador What-If del usuario. Si los abogados dicen "Solo podemos ganar el 35% de las demandas", el tablero calcula instantáneamente la pérdida exacta que Finanzas debe reportar en sus libros (Perdida Neta Irrecuperable).

Por último, el % Acumulado Pareto es la joya de la corona operativa. Para no saturar el rendimiento del reporte, diseñé esta métrica utilizando una tabla virtual (ProveedoresConFraude) que descarta de inmediato a los proveedores sanos, calculando la regla 80/20 exclusivamente sobre los infractores. Esto le permite al bufete legal dirigir todo su tiempo y recursos operativos hacia los 3 o 4 proveedores que concentran el mayor impacto, maximizando el ROI de la cobranza y evitando litigios incosteables por facturas mínimas.

























