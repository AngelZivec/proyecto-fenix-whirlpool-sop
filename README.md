# Sistema de Auditoría Forense: Detección de Pagos Duplicados y Fugas de Capital 🔎💰

Este repositorio contiene la arquitectura de datos, scripts de procesamiento y el modelo semántico utilizados para desarrollar un centro de mando End-to-End de auditoría financiera, diseñado para los departamentos de Cuentas por Pagar, Tesorería y Legal.

## 🎯 Objetivo del Proyecto

Automatizar la fiscalización y detección de fugas de capital (pagos duplicados, fraccionados o alterados) derivadas de vulnerabilidades de control interno o *Dirty Data*. Además, fungir como una herramienta táctica para proyectar metas de recuperación financiera y aislar de inmediato las facturas infractoras para cobranza jurídica.

## 🛠️ Stack Tecnológico

* **Extracción y Transformación (ETL):** Python (Pandas)
* **Almacenamiento y Auditoría Visual:** SQL Server
* **Modelado Semántico y Visualización:** Power BI (DAX Avanzado, Algoritmos iterativos SUMX, What-If Parameters)

## 🏗️ Arquitectura de Datos End-to-End

* **Extracción (Fase 1):** Recopilación de registros históricos de expedientes, órdenes de pago y facturas emitidas desde portales gubernamentales (Compranet).
* **Transformación (Fase 2):** Depuración estructural, limpieza de ruido espacial (Trim) y homologación de diccionarios para mapear tipografías corruptas del ERP hacia categorías limpias usando scripts de Python.
* **Almacenamiento (Fase 3):** Consolidación en SQL Server para consultas de auditoría y creación de vistas maestras de riesgo financiero.
* **Visualización (Fase 4):** Despliegue en Power BI de la Matriz Transaccional Legal y simuladores financieros.
*(Puedes visualizar el diagrama de flujo detallado en el archivo PDF adjunto en la carpeta `docs/` de este repositorio).*

## 📈 Impacto Proyectado (Caso de Negocio)

Visibilidad 360° estructurada en 3 ejes tácticos:
1.  **Priorización Estratégica (Regla 80/20):** Implementación de un modelo de Pareto en DAX para aislar al grupo reducido de proveedores que concentran el mayor impacto monetario.
2.  **Acción Legal Inmediata (Patrón Maestro-Detalle):** Traducción de gráficas agregadas a una matriz transaccional que filtra y exhibe el detalle granular probatorio para un litigio (fecha, folio exacto, proveedor y divisa).
3.  **Proyección de Flujo de Caja:** Uso de simuladores dinámicos (*What-If*) para calcular en tiempo real la tasa de recuperación legal estimada vs. la pérdida neta irrecuperable a provisionar en libros contables.

## 📁 Estructura del Repositorio

* `data/`: Muestras de catálogos y diccionarios de mapeo.
* `src/python/`: Scripts de limpieza, homologación de texto y estructuración ETL.
* `src/sql/`: Consultas de validación y almacenamiento.
* `docs/`: Manual de Operación, Diccionario de métricas DAX y Diagrama del Pipeline.

## 🔗 Enlaces

* [Ver Portafolio Interactivo y Dashboard Completo]
* https://zivec.framer.website/
* https://zivec.framer.website/proyecto-whirpool-merch-phase-out-and-phase-in
