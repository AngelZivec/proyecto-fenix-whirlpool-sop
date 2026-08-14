USE Auditoria_Pagos;
GO

-- Creamos (o actualizamos) nuestra Vista Maestra para Power BI
CREATE OR ALTER VIEW vw_Auditoria_Riesgo_Financiero AS

WITH Analisis_Frecuencia AS (
    -- Paso 1: Agrupamos y escaneamos la base
    SELECT 
        num_factura,
        num_orden_compra,
        proveedor,
        titulo_contrato,
        detalle_transaccion,
        categoria_gasto,
        id_categoria_trabajo,
        modalidad_contratacion,
        proceso_adjudicacion,
        monto_transaccion,
        divisa,
        fecha_inicio,
        -- LA MAGIA MEJORADA: Limpiamos los textos al vuelo para cazar "Errores de Captura"
        COUNT(*) OVER(
            PARTITION BY 
                REPLACE(num_factura, '-', ''),         -- Ignora guiones en la factura
                REPLACE(UPPER(proveedor), ' ', ''),    -- Ignora mayúsculas/minúsculas y espacios en el proveedor
                monto_transaccion, 
                fecha_inicio
        ) AS frecuencia_pago
    FROM Transacciones_Historicas
    WHERE monto_transaccion > 0 
      AND num_factura IS NOT NULL 
      AND proveedor != 'Sin Dato'
      AND fecha_inicio IS NOT NULL 
      AND YEAR(fecha_inicio) >= 2000
)
-- Paso 2: Etiquetamos los datos
SELECT 
    *,
    CASE 
        WHEN frecuencia_pago = 1 THEN 'Pago Íntegro'
        WHEN frecuencia_pago > 1 THEN 'Fuga por Duplicidad'
    END AS clasificacion_riesgo
FROM Analisis_Frecuencia;
GO


USE Auditoria_Pagos;
GO

-- Consulta optimizada para detectar Pagos Duplicados Exactos
SELECT 
    num_factura,
    proveedor,
    monto_transaccion,
    fecha_inicio,
    COUNT(*) AS Total_Duplicados,
    SUM(monto_transaccion) AS Monto_En_Riesgo
FROM Transacciones_Historicas
GROUP BY num_factura, proveedor, monto_transaccion, fecha_inicio
HAVING COUNT(*) > 1
ORDER BY Total_Duplicados DESC;
GO
