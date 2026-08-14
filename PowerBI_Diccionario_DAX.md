📖 Diccionario de Medidas DAX: Sistema S&OP y Auditoría Forense (Proyecto Fénix) Whirpool

A continuación, documento la arquitectura semántica que diseñé para este proyecto. Agrupé las medidas en bloques lógicos para facilitar su lectura y justifiqué cada una con el Racional de Negocio, explicando cómo estas fórmulas resuelven los problemas operativos y financieros de la compañía.

📊 Bloque 1: Desempeño Comercial y Tendencias (YoY & Macro)
Este bloque establece la línea base de la facturación y mide el ritmo de absorción del mercado.

1 - Total Unidades Producidas = SUM(Fact_Produccion[Unidades_Producidas]) + 0

1 - Total Unidades Vendidas = SUM(Fact_Ventas[Unidades_Vendidas]) + 0

1.1 - Ingreso Bruto = SUMX(Fact_Ventas, Fact_Ventas[Precio_Lista] * Fact_Ventas[Unidades_Vendidas]) + 0

1.2 - Margen Neto Total = SUM(Fact_Ventas[Margen_Neto]) + 0

💡 Racional de Negocio: Estas son las medidas base (Core) del modelo. La suma simple está fortificada con un + 0. Esto es una práctica de diseño de UI que utilizo para garantizar que las matrices y gráficos en Power BI jamás muestren espacios en blanco (blanks) si una categoría no tiene ventas, manteniendo la estructura visual limpia y corporativa.

1.3 - Promedio Mensual Ventas = 
AVERAGEX(
    VALUES(Dim_Calendario[Mes]), 
    [1 - Total Unidades Vendidas]
)

1.8 - Promedio Mensual Ventas AA = 
CALCULATE(
    [1.3 - Promedio Mensual Ventas],
    SAMEPERIODLASTYEAR(Dim_Calendario[Fecha])
)

💡 Racional de Negocio: Comparar totales a veces es engañoso. Diseñé estas medidas usando AVERAGEX para calcular el "Run-Rate" (velocidad de venta mensual). Nos indica el ritmo de crucero de la demanda comercial para compararlo de forma equilibrada contra el desempeño del año anterior (AA).

1.4 - Ventas AA = 
CALCULATE(
    [1 - Total Unidades Vendidas], 
    SAMEPERIODLASTYEAR(Dim_Calendario[Fecha])
) + 0

1.5 - Gap de Ventas = [1 - Total Unidades Vendidas] - [1.4 - Ventas AA]

1.6 - % Crecimiento Ventas YoY = 
DIVIDE(
    [1.5 - Gap de Ventas], 
    [1.4 - Ventas AA], 
    0
)

💡 Racional de Negocio: Inteligencia de tiempo estandarizada. Calcula el crecimiento o contracción orgánica de la empresa Year-over-Year (YoY). El uso de DIVIDE asegura que el modelo no se rompa con errores de división entre cero.

1.7 - Rolling Year Ventas = 
CALCULATE(
    [1 - Total Unidades Vendidas], 
    DATESINPERIOD(
        Dim_Calendario[Fecha], 
        MAX(Dim_Calendario[Fecha]), 
        -12, 
        MONTH
    )
)

1.9 - Ventas Macro (Sin Filtros) = 
CALCULATE(
    [1 - Total Unidades Vendidas],
    REMOVEFILTERS(Dim_Producto),
    REMOVEFILTERS(Fact_Ventas[Canal_Venta]),
    REMOVEFILTERS(Fact_Ventas[Key_Account])
)

💡 Racional de Negocio: El Rolling Year aísla por completo la estacionalidad (ej. picos del Buen Fin), dándonos una curva de tendencia limpia de los últimos 12 meses continuos. Por su parte, Ventas Macro utiliza REMOVEFILTERS para forzar al sistema a calcular el universo total de ventas ignorando los segmentadores, lo cual es vital para calcular posteriormente las cuotas de mercado o participación.

⚙️ Bloque 2: Sincronía S&OP y Saturación Logística
Este bloque audita el balance entre lo que sale de la fábrica (Inflow) y lo que se factura (Outflow).

2 - Balance Neto S&OP = 
[1 - Total Unidades Producidas] - [1 - Total Unidades Vendidas]

2.1 - Indice de Alineacion = 
DIVIDE(
    [1 - Total Unidades Vendidas], 
    [1 - Total Unidades Producidas], 
    0
)

💡 Racional de Negocio: Este es el "Termómetro de Operaciones". El Índice de Alineación mide si la planta está corriendo a la par del mercado (ideal 100%). Un índice desplomado y un Balance Neto alto alertan sobreproducción, demostrando con datos si el origen de la crisis es que Manufactura no frena o Comercial no vende.

2.2 - Unidades en Inventario (Cierre) = 
CALCULATE(
    SUM(Fact_Inventario[Unidades_Fisicas]),
    Fact_Inventario[Fecha_Corte_Semanal] = MAX(Fact_Inventario[Fecha_Corte_Semanal])
) + 0

2.3 - Capital Inmovilizado (Cierre) = 
CALCULATE(
    SUM(Fact_Inventario[Valor_Total_Inventario]),
    Fact_Inventario[Fecha_Corte_Semanal] = MAX(Fact_Inventario[Fecha_Corte_Semanal])
) + 0

💡 Racional de Negocio: Estas son medidas semi-aditivas. A diferencia de las ventas, el inventario no se puede sumar mes con mes (es el mismo producto arrastrándose). Utilicé CALCULATE buscando el último día de la semana (MAX) para obtener una "fotografía exacta" de las unidades atascadas y los dólares que representan en capital de trabajo.

2.4 - Saturacion Volumetrica CBM = 
CALCULATE(
    SUMX(
        Fact_Inventario,
        Fact_Inventario[Unidades_Fisicas] * 
        SWITCH(RELATED(Dim_Producto[Categoria]), 
            "Refrigeración", 1.8, 
            "Lavado", 1.2, 
            "Cocción", 0.9, 
            1.0
        )
    ),
    Fact_Inventario[Fecha_Corte_Semanal] = MAX(Fact_Inventario[Fecha_Corte_Semanal])
) + 0

💡 Racional de Negocio: Esta es una de las medidas más sofisticadas. Transforma las cajas físicas atascadas en su equivalente tridimensional en metros cúbicos (CBM). Utilicé SUMX con un SWITCH para asignarle un peso volumétrico distinto a cada línea de producto. Esto alerta la "Asfixia Logística" previniendo a la Dirección cuándo se saturarán las bodegas.  

📉 Bloque 3: Auditoría Forense y Ejecución Comercial
Este bloque identifica las fugas de rentabilidad y los cuellos de botella en el punto de venta.

3 - Perdida por Descuentos = 
SUMX(
    Fact_Ventas, 
    Fact_Ventas[Precio_Lista] * Fact_Ventas[%_Descuento_Aplicado] * Fact_Ventas[Unidades_Vendidas]
) + 0

3.1 - % Margen Evaporado = 
DIVIDE(
    [3 - Perdida por Descuentos], 
    [1.1 - Ingreso Bruto], 
    0
)

3.2 - Run-Rate Perdida Mensual = 
AVERAGEX(
    VALUES(Dim_Calendario[Mes]), 
    [3 - Perdida por Descuentos]
) + 0

Fragmento de código
3 - Perdida por Descuentos = 
SUMX(
    Fact_Ventas, 
    Fact_Ventas[Precio_Lista] * Fact_Ventas[%_Descuento_Aplicado] * Fact_Ventas[Unidades_Vendidas]
) + 0

3.1 - % Margen Evaporado = 
DIVIDE(
    [3 - Perdida por Descuentos], 
    [1.1 - Ingreso Bruto], 
    0
)

3.2 - Run-Rate Perdida Mensual = 
AVERAGEX(
    VALUES(Dim_Calendario[Mes]), 
    [3 - Perdida por Descuentos]
) + 0

💡 Racional de Negocio: Este es el "Estado de Resultados Forense". Calcula con precisión quirúrgica, transacción por transacción (SUMX), cuántos dólares está sangrando la compañía para empujar el producto viejo (Phase Out) mediante remates. Mide el costo financiero real de una mala planeación.

3.3 - Gap Capital Inmovilizado = 
[2.3 - Capital Inmovilizado (Cierre)] - 
CALCULATE(
    [2.3 - Capital Inmovilizado (Cierre)], 
    SAMEPERIODLASTYEAR(Dim_Calendario[Fecha])
)

3.4 - Tasa de Bloqueo en Cajas = 
DIVIDE(
    CALCULATE(
        COUNTROWS(Staging_Captura_Excel), 
        Staging_Captura_Excel[Codificacion_Activa] = "No"
    ), 
    COUNTROWS(Staging_Captura_Excel), 
    0
)

💡 Racional de Negocio: La Tasa de Bloqueo audita la calidad de la ejecución en las Key Accounts. Detecta el porcentaje exacto de ocasiones en que el producto de innovación (Phase In) intentó venderse pero fue rechazado en caja porque los ejecutivos no codificaron los SKUs en los sistemas de las tiendas departamentales.

🎮 Bloque 4: Simuladores Tácticos y Plan de Ejecución (What-If)
Este bloque le da vida al tablero, permitiendo a los directores estresar el modelo y simular acciones en tiempo real.

Descuento Autorizado = GENERATESERIES(0, 1, 0.05)

Dimensión de Mercado = {
    ("Categoria", NAMEOF('Dim_Producto'[Categoria]), 0),
    ("Estatus_PIPO", NAMEOF('Dim_Producto'[Estatus_PIPO]), 1),
    ("Marca", NAMEOF('Dim_Producto'[Marca]), 2),
    ("Canal_Venta", NAMEOF('Fact_Ventas'[Canal_Venta]), 3)
}

💡 Racional de Negocio: Parámetros de arquitectura visual interactiva. Dimensión de Mercado utiliza "Field Parameters" para que el usuario pueda cambiar dinámicamente los ejes de las gráficas (ahorrando espacio de lienzo). Descuento Autorizado genera la escala numérica de estrés que controla todos los KPIs predictivos del tablero.

4.1 - Ingreso Proyectado (Meta) = 
[2.3 - Capital Inmovilizado (Cierre)] * (1 - 'Descuento Autorizado'[Valor de Descuento Autorizado])

4.2 - Castigo a Resultados (Perdida) = 
[2.3 - Capital Inmovilizado (Cierre)] * 'Descuento Autorizado'[Valor de Descuento Autorizado]

4.3 - Dias de Inventario (DOH) = 
VAR VentasDiariasPromedio = DIVIDE([1.3 - Promedio Mensual Ventas], 30, 0)
RETURN 
DIVIDE([2.2 - Unidades en Inventario (Cierre)], VentasDiariasPromedio, 0)

💡 Racional de Negocio: El motor de planeación predictiva. Al mover el simulador de descuento, estas métricas re-calculan instantáneamente cuánto capital se recuperará, la provisión de pérdida contable a realizar y los Días de Inventario Proyectados (el tiempo exacto que tardaremos en limpiar las bodegas si aplicamos ese remate).  

4.4 - % Acumulado Pareto = 
VAR TotalCapital = CALCULATE([2.3 - Capital Inmovilizado (Cierre)], ALLSELECTED(Dim_Producto[SKU]))
VAR CapitalActual = [2.3 - Capital Inmovilizado (Cierre)]
VAR CapitalAcumulado = 
    SUMX(
        FILTER(
            ALLSELECTED(Dim_Producto[SKU]),
            [2.3 - Capital Inmovilizado (Cierre)] >= CapitalActual
        ),
        [2.3 - Capital Inmovilizado (Cierre)]
    )
RETURN 
DIVIDE(CapitalAcumulado, TotalCapital, 0)

💡 Racional de Negocio: La medida más táctica del ecosistema logístico. Evalúa el peso de cada SKU iterando sobre el catálogo (FILTER sobre ALLSELECTED). Esto construye matemáticamente la curva 80/20 de Pareto. Garantiza que la gerencia direccione los esfuerzos de venta hacia el minoritario porcentaje de modelos que acaparan la inmensa mayoría del capital inmovilizado, optimizando los recursos del equipo comercial.


