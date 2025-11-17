Seeds para EPSDC-IA
====================

Este directorio contiene herramientas para poblar la base de datos con datos sintéticos
útiles para probar la pipeline ETL y el entrenamiento/inferencia de la IA.

Archivo principal
- `seed_db.py`: script que crea tablas mínimas y genera registros sintéticos.

Dependencias
- Ejecutar `pip install -r requirements.txt` (se añadió `Faker`).

Uso rápido
1. Configura tu `.env` con `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`.
2. Nota importante: el script **no** crea parroquias. Usa las parroquias existentes en la base; el seed sólo trabajará con las parroquias cuyo `municipio_id = 147`.
3. Ejecuta:

```powershell
python seed_db.py --start-date 2024-01-01
```

3. Ejecuta el ETL para rellenar `features_parroquia_daily`:

```powershell
python etl_features_parroquia_daily.py
```

Notas
- El script intenta no duplicar parroquias si ya existen.
- Ajusta parámetros `--avg-weekly` y `--solicitud-prob` para controlar densidad de datos.
