-- =======================================================
-- INYECCIÓN S&OP: PREPARACIÓN PARA BUEN FIN / BLACK FRIDAY
-- TABLA: Fact_Produccion (Aceleración de Planta en Q3)
-- =======================================================

UPDATE [dbo].[Fact_Produccion]
SET 
    -- 1. Aumentamos las unidades producidas en un 40% para construir inventario
    Unidades_Producidas = ROUND(Unidades_Producidas * 1.40, 0),
    
    -- 2. Recalculamos el costo total multiplicando las nuevas unidades por el costo unitario
    Costo_Total_Produccion = ROUND((ROUND(Unidades_Producidas * 1.40, 0)) * Costo_Fabricacion_Unitario, 2)
WHERE 
    Mes IN (8, 9, 10);

PRINT '¡Producción de Q3 inflada correctamente para la temporada alta!';

-- =======================================================
-- INYECCIÓN S&OP: IMPACTO FINANCIERO DEL BUEN FIN (MES 11)
-- TABLA: Fact_Ventas 
-- =======================================================

WITH VentaCalculada AS (
    SELECT 
        v.ID_Venta,
        p.Estatus_PIPO,
        v.Precio_Lista,
        v.Unidades_Vendidas AS Unidades_Originales,
        v.[%_Descuento_Aplicado] AS Descuento_Original,
        v.Margen_Neto AS Margen_Original,
        -- Desciframos el Costo Unitario Operativo Original aislando el margen
        (((v.Precio_Lista * (1 - v.[%_Descuento_Aplicado])) * v.Unidades_Vendidas) - v.Margen_Neto) / v.Unidades_Vendidas AS Costo_Unitario
    FROM Fact_Ventas v
    INNER JOIN Dim_Producto p ON v.SKU = p.SKU
    WHERE v.Mes = 11
)
UPDATE v
SET 
    -- 1. EL TRUCO DEL DESCUENTO: Destrucción de margen para sacar lo viejo
    v.[%_Descuento_Aplicado] = CASE 
        WHEN c.Estatus_PIPO = 'Phase Out' THEN 0.50 -- Liquidación agresiva
        WHEN c.Estatus_PIPO = 'Regular' THEN 0.20   -- Descuento normal de temporada
        ELSE 0.00 -- Phase In no lleva descuento
    END,

    -- 2. VOLUMEN DE VENTAS: La locura comercial y el bloqueo en tiendas
    v.Unidades_Vendidas = CASE
        WHEN c.Estatus_PIPO = 'Phase Out' THEN ROUND(c.Unidades_Originales * 1.80, 0) -- Se dispara la venta
        WHEN c.Estatus_PIPO = 'Regular' THEN ROUND(c.Unidades_Originales * 1.30, 0)   -- Sube la venta normal
        WHEN c.Estatus_PIPO = 'Phase In' THEN ROUND(c.Unidades_Originales * 0.15, 0)  -- ¡Se bloquea la venta! Cae 85%
    END,

    -- 3. RECALCULO DE MARGEN NETO: Matemática financiera exacta
    -- Margen = (Precio_Lista * (1 - Nuevo_Descuento) * Nuevas_Unidades) - (Costo_Unitario * Nuevas_Unidades)
    v.Margen_Neto = ROUND(
        (c.Precio_Lista * 
        (1 - CASE 
                WHEN c.Estatus_PIPO = 'Phase Out' THEN 0.50 
                WHEN c.Estatus_PIPO = 'Regular' THEN 0.20 
                ELSE 0.00 END) * 
        (CASE
                WHEN c.Estatus_PIPO = 'Phase Out' THEN ROUND(c.Unidades_Originales * 1.80, 0)
                WHEN c.Estatus_PIPO = 'Regular' THEN ROUND(c.Unidades_Originales * 1.30, 0)
                WHEN c.Estatus_PIPO = 'Phase In' THEN ROUND(c.Unidades_Originales * 0.15, 0) END)) 
        - 
        (c.Costo_Unitario * CASE
                WHEN c.Estatus_PIPO = 'Phase Out' THEN ROUND(c.Unidades_Originales * 1.80, 0)
                WHEN c.Estatus_PIPO = 'Regular' THEN ROUND(c.Unidades_Originales * 1.30, 0)
                WHEN c.Estatus_PIPO = 'Phase In' THEN ROUND(c.Unidades_Originales * 0.15, 0) END), 
    2)
FROM Fact_Ventas v
INNER JOIN VentaCalculada c ON v.ID_Venta = c.ID_Venta;

PRINT '¡Hemorragia financiera y bloqueo comercial del Buen Fin inyectados con éxito en el Mes 11!';

-- =======================================================
-- INYECCIÓN S&OP: EL CUELLO DE BOTELLA LOGÍSTICO (MESES 11 y 12)
-- TABLA: Fact_Inventario 
-- =======================================================

WITH ValoresInventario AS (
    SELECT 
        i.ID_Corte,
        p.Estatus_PIPO,
        i.Unidades_Fisicas AS Unidades_Originales,
        i.Valor_Total_Inventario,
        -- Desciframos el costo base unitario para no perder la matemática
        (i.Valor_Total_Inventario / NULLIF(i.Unidades_Fisicas, 0)) AS Costo_Base_Unitario
    FROM [dbo].[Fact_Inventario] i
    INNER JOIN [dbo].[Dim_Producto] p ON i.SKU = p.SKU
    WHERE i.Mes IN (11, 12)
)
UPDATE i
SET 
    -- 1. Modificamos el volumen físico
    i.Unidades_Fisicas = CASE 
        WHEN c.Estatus_PIPO = 'Phase In' THEN ROUND(c.Unidades_Originales * 3.5, 0) -- Se estanca masivamente (+250%)
        WHEN c.Estatus_PIPO = 'Phase Out' THEN ROUND(c.Unidades_Originales * 0.15, 0) -- Se vacía casi por completo (Queda 15%)
        ELSE c.Unidades_Originales 
    END,

    -- 2. Recalculamos el capital inmovilizado con las nuevas unidades
    i.Valor_Total_Inventario = ROUND(
        (CASE 
            WHEN c.Estatus_PIPO = 'Phase In' THEN ROUND(c.Unidades_Originales * 3.5, 0)
            WHEN c.Estatus_PIPO = 'Phase Out' THEN ROUND(c.Unidades_Originales * 0.15, 0)
            ELSE c.Unidades_Originales 
        END) * c.Costo_Base_Unitario, 2)
FROM [dbo].[Fact_Inventario] i
INNER JOIN ValoresInventario c ON i.ID_Corte = c.ID_Corte;

PRINT '¡Paso 3 completado! Cuello de botella inyectado exitosamente en Fact_Inventario.';

-- =======================================================
-- INYECCIÓN S&OP: EL CAOS EN PISO DE VENTA (MES 11)
-- TABLA: Staging_Captura_Excel 
-- =======================================================

UPDATE s
SET 
    -- 1. Destruimos el precio público al máximo para sacar el producto viejo
    s.[%_Descuento_Aplicado] = CASE 
        WHEN s.Estatus_PIPO = 'Phase Out' THEN 0.55 -- Descuento tope de Buen Fin
        ELSE s.[%_Descuento_Aplicado] 
    END,
    
    -- 2. Simulamos la locura de ventas en piso (Sell-Out)
    s.Unidades_Sell_Out = CASE 
        WHEN s.Estatus_PIPO = 'Phase Out' THEN ROUND(s.Unidades_Sell_Out * 2.5, 0) -- Se llevan todo lo viejo
        WHEN s.Estatus_PIPO = 'Phase In' THEN 0 -- Cero ventas reales al consumidor
        ELSE ROUND(s.Unidades_Sell_Out * 1.5, 0) 
    END,
    
    -- 3. Vaciamos los pasillos de lo viejo
    s.Inventario_Piso_Venta = CASE
        WHEN s.Estatus_PIPO = 'Phase Out' THEN 0 -- "Agotado" en piso de tienda
        ELSE s.Inventario_Piso_Venta 
    END,
    
    -- 4. El Bloqueo Corporativo: Las cajas registradoras no leen el producto nuevo
    s.Codificacion_Activa = CASE 
        WHEN s.Estatus_PIPO = 'Phase In' THEN 'No' -- Bloqueo crítico en el mes más importante
        ELSE s.Codificacion_Activa 
    END
FROM [dbo].[Staging_Captura_Excel] s
WHERE MONTH(s.Fecha_Reporte) = 11;

PRINT '¡Clímax comercial de Noviembre inyectado con éxito en Staging!';
