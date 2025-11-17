# SEEDS — Cómo usar los seeders para EPSDC-IA

Este archivo documenta cómo ejecutar los scripts de seed que generan datos sintéticos para pruebas locales, las opciones disponibles y recomendaciones para balancear la etiqueta `abrir` en el dataset de entrenamiento.

## Objetivo

- Poblar tablas necesarias (comunidades, consejos, voceros, solicitudes, periodos, almacenes, entregas) para ejecutar la pipeline ETL y el entrenamiento de modelos.
- Proveer parámetros para controlar cuántos periodos "abiertos" (periodos que inician hoy) se crean y cuántas solicitudes pendientes se generan.

> Nota importante: Los scripts de seed **NO** crean nuevas parroquias. Usan las parroquias existentes en la base de datos filtrando por `municipio_id = 147` (conforme a la restricción del proyecto).

## Archivos relevantes

- `seed_db.py` — generador principal. Detecta esquema y adapta inserciones. Parámetros CLI disponibles.
- `etl_features_parroquia_daily.py` — ETL que crea/actualiza `features_parroquia_daily` usando SQL en `features_diarias.sql`.
- `dataset_entrenamiento.py` — lee la vista `dataset_entrenamiento` desde la DB y exporta `dataset_entrenamiento.csv`.
- `entrenar_modelo_cart.py` — entrena el modelo usando `dataset_entrenamiento.csv` o la vista directa.

## Cómo ejecutar (recomendado: entorno virtual)

Ejemplo paso a paso en PowerShell (desde la raíz `EPSDC-IA`):

```powershell
cd 'C:\xampp\htdocs\EPSDC-IA'
# Ejecutar seed: generar más periodos que inician hoy (50%)
C:/xampp/htdocs/EPSDC-IA/.venv/Scripts/python.exe .\seed_db.py --open-pct 0.50 --close-pct 0.05

# Ejecutar ETL
C:/xampp/htdocs/EPSDC-IA/.venv/Scripts/python.exe .\etl_features_parroquia_daily.py

# Generar dataset CSV
C:/xampp/htdocs/EPSDC-IA/.venv/Scripts/python.exe .\dataset_entrenamiento.py

# Entrenar modelo
C:/xampp/htdocs/EPSDC-IA/.venv/Scripts/python.exe .\entrenar_modelo_cart.py
```

## Parámetros principales de `seed_db.py`

- `--open-pct`: fracción de parroquias que recibirán un `periodo` con `fecha_inicio = hoy`. Ej.: `0.30` = 30%.
- `--close-pct`: fracción de parroquias con un `periodo` que termina hoy.
- `--start-date` / `--end-date`: rango para generar entregas históricas.
- `--avg-weekly`: controla frecuencia de entregas (promedio semanal en la lógica actual).

Recomendaciones:
- Para pruebas de balance de la etiqueta minoritaria (`abrir`) usa `--open-pct` entre `0.1` y `0.5`.
- No uses valores extremos (>= 0.8) en entornos compartidos porque generan muchos registros.

## Por qué esto afecta la etiqueta `abrir`

- El pipeline etiqueta como `abrir` si hay un `periodo` que empieza hoy o señales parecidas (dependiendo de la definición en la vista `dataset_entrenamiento`). Crear más `periodos` con `fecha_inicio = hoy` aumentará los ejemplos `abrir`.
- Además, `seed_db.py` ahora crea 0–3 solicitudes por vocero con mayor probabilidad de `PENDIENTE`, lo que incrementa la señal `entregas_pendientes` que también puede afectar la etiqueta.

## Notas sobre `dataset_entrenamiento.csv` y reproducción

- `dataset_entrenamiento.py` lee la vista `dataset_entrenamiento` desde la DB y exporta un CSV. Si ves un CSV con sólo cabecera es posible que el script haya sido ejecutado parcialmente o que otro paso sobrescriba el archivo después. Recomendación: siempre ejecutar `dataset_entrenamiento.py` y comprobar su tamaño:

```powershell
Get-Item .\dataset_entrenamiento.csv | Format-List Name,Length,LastWriteTime
```

- Si el tamaño es pequeño, relanza `dataset_entrenamiento.py` o usa el helper `from dataset_entrenamiento import cargar_dataset` en Python para confirmar que la vista devuelve filas.

## Artefactos y .gitignore

- No subas al repositorio los artefactos generados: `*.joblib`, `dataset_entrenamiento.csv`, logs (`*.log`), imágenes (`*.png`) ni el entorno virtual. Se añadió un `.gitignore` con reglas para estos archivos.

## Deshacer / limpieza

- Estos seeds insertan filas directamente en la base de datos. No existe actualmente un rollback automático. Si necesitas revertir los cambios en un entorno de pruebas, restaura la copia de seguridad del esquema o borra las filas manualmente (consultar con el DBA).

## Ejemplos rápidos

- Generar pocos ejemplos `abrir` (10%):
  - `python .\seed_db.py --open-pct 0.10 --close-pct 0.02`

- Generar muchos ejemplos `abrir` para pruebas (50%):
  - `python .\seed_db.py --open-pct 0.50 --close-pct 0.05`

## Contacto / seguimiento

Si quieres que automatice un test que valide que `dataset_entrenamiento.csv` contiene al menos N ejemplos `abrir`, puedo añadir un pequeño script `tests/smoke_seed.py` que haga eso y lo ejecute en local o en CI.
