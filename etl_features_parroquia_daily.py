# V1.0

# # etl_features_parroquia_daily.py
# import pandas as pd
# from sqlalchemy import create_engine, text
# from datetime import datetime
# import logging

# # --- CONFIGURACIÓN ---
# DB_URI = "mysql+pymysql://user:password@localhost/epsdc_principal"
# QUERY_FILE = "features_diarias.sql"
# LOG_FILE = "etl_features.log"

# logging.basicConfig(filename=LOG_FILE,
#                     level=logging.INFO,
#                     format="%(asctime)s [%(levelname)s] %(message)s")

# def run_etl():
#     logging.info("Inicio de ETL de features_parroquia_daily")
#     engine = create_engine(DB_URI)

#     with engine.connect() as conn:
#         with open(QUERY_FILE, "r", encoding="utf-8") as f:
#             sql = text(f.read())

#         conn.execute(sql)
#         conn.commit()

#     logging.info(f"ETL completado correctamente para {datetime.now().date()}")

# if __name__ == "__main__":
#     try:
#         run_etl()
#     except Exception as e:
#         logging.error(f"Error en ETL: {str(e)}")
#         print("❌ Error durante la ejecución del ETL, revisa etl_features.log")
#     else:
#         print("✅ ETL ejecutado correctamente")

# V2.0

# etl_features_parroquia_daily.py
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import logging

# Usar configuración desde config.py (variables de entorno)
from config import DB_URI, LOG_FILE
from pathlib import Path

QUERY_FILE = "features_diarias.sql"

logging.basicConfig(filename=LOG_FILE,
                    level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

def run_etl():
    logging.info("Inicio de ETL de features_parroquia_daily")
    engine = create_engine(DB_URI)

    # Resolve query file relative to this script to avoid CWD confusion
    query_path = Path(__file__).resolve().parent.joinpath(QUERY_FILE)
    logging.info(f"Usando archivo SQL: {str(query_path)}")

    if not query_path.exists():
        raise FileNotFoundError(f"Query file not found: {str(query_path)}")

    with engine.connect() as conn:
        with open(query_path, "r", encoding="utf-8") as f:
            sql_text = f.read()
        logging.info(f"Longitud SQL leido: {len(sql_text)} chars")
        sql = text(sql_text)
        conn.execute(sql)
        conn.commit()

    logging.info(f"ETL completado correctamente para {datetime.now().date()}")

if __name__ == "__main__":
    try:
        run_etl()
        print("✅ ETL ejecutado correctamente")
    except Exception as e:
        logging.error(f"Error en ETL: {str(e)}")
        print("❌ Error durante la ejecución del ETL, revisa etl_features.log")
