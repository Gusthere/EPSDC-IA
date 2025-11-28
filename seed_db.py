"""seed_db.py
Generador de datos sintéticos para poblar las tablas necesarias
para que la pipeline ETL y el dataset de entrenamiento puedan ejecutarse.

Tablas generadas / pobladas:
 - parroquia (id_parroquia, nombre)
 - almacen (id, parroquia, existencia, capacidad)
 - entrega (id, parroquia, fecha_entrega, cantidad)
 - solicitud (id, parroquia, fecha_solicitud, estado)
 - periodo (id, fecha_inicio, fecha_fin)

Uso:
 python seed_db.py --parroquias 200 --start-date 2024-01-01

Config: usa `DB_URI` desde `config.py`.
"""
from datetime import date, datetime, timedelta
import random
import argparse
try:
    from faker import Faker
except Exception:
    Faker = None

from sqlalchemy import create_engine, text

from config import DB_URI

if Faker is not None:
    fake = Faker('es_ES')
else:
    # Fallback mínimo si no está instalado Faker (evita dependencia para pruebas rápidas)
    import random

    class _UniqueWrapper:
        def __init__(self, parent):
            self.parent = parent
            self.seen = set()

        def city(self):
            v = self.parent.city()
            while v in self.seen:
                v = self.parent.city()
            self.seen.add(v)
            return v

    class MinimalFaker:
        def __init__(self):
            self._rnd = random
            self.unique = _UniqueWrapper(self)

        def city(self):
            return f"Ciudad{self._rnd.randint(1000,9999)}"

        def first_name(self):
            return f"Nombre{self._rnd.randint(1,9999)}"

        def last_name(self):
            return f"Apellido{self._rnd.randint(1,9999)}"

        def phone_number(self):
            return str(self._rnd.randint(4000000000, 5999999999))

    fake = MinimalFaker()

# Verificar que el driver de MySQL esté instalado (pymysql)
try:
    import pymysql  # noqa: F401
except ModuleNotFoundError:
    import sys
    print("ERROR: falta el paquete 'pymysql' requerido por SQLAlchemy para conectar a MySQL.")
    print("Instálalo con: python -m pip install pymysql")
    sys.exit(1)


def ensure_tables(engine):
    # Crear tablas mínimas si no existen (nombres/columnas coinciden con esquema del sistema)
    ddl = f"""
    CREATE TABLE IF NOT EXISTS almacen (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        parroquia INT NOT NULL,
        existencia DECIMAL(10,2) DEFAULT 0,
        capacidad DECIMAL(10,2) DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS entrega (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        parroquia INT NOT NULL,
        fecha_entrega DATE NOT NULL,
        cantidad DECIMAL(10,2) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS comunidad (
        id INT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        parroquia_id INT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS consejo_comunal (
        rif VARCHAR(20) PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        solicitud VARCHAR(20) DEFAULT 'DISPONIBLE',
        estado TINYINT DEFAULT 1,
        comunidad_id INT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS vocero_comunal (
        cedula VARCHAR(16) PRIMARY KEY,
        nombre VARCHAR(100),
        apellido VARCHAR(100),
        telefono VARCHAR(20),
        fecha_inicio DATE,
        fecha_final DATE DEFAULT NULL,
        estado TINYINT DEFAULT 1,
        consejo_comunal_rif VARCHAR(20)
    );

    CREATE TABLE IF NOT EXISTS solicitud (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        fecha DATE NOT NULL DEFAULT CURRENT_DATE,
        estado VARCHAR(50) NOT NULL DEFAULT 'PENDIENTE',
        vocero_comunal VARCHAR(16) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS periodo (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        fecha_inicio DATE NOT NULL,
        fecha_fin DATE DEFAULT NULL,
        parroquia_id INT DEFAULT NULL
    );
    """
    # Ejecutar cada sentencia DDL por separado para evitar errores de multi-statement
    with engine.connect() as conn:
        for stmt in ddl.split(';'):
            stmt = stmt.strip()
            if not stmt:
                continue
            conn.execute(text(stmt))
        conn.commit()


def seed_parroquias(engine, n):
    # Deprecated in this environment: parroquias ya existen en la base de datos.
    print("Omitido: no se crean parroquias (usar existentes)")


def seed_almacenes(engine, parroquias):
    def get_table_columns(conn, table_name: str):
        res = conn.execute(text(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t"
        ), {"t": table_name})
        return [r[0] for r in res.fetchall()]

    with engine.connect() as conn:
        cols = get_table_columns(conn, 'almacen')
        cols_set = set(cols)

        # Case A: table has a parroquia/parroquia_id column -> keep per-parroquia almacen rows
        if 'parroquia' in cols_set or 'parroquia_id' in cols_set:
            col = 'parroquia' if 'parroquia' in cols_set else 'parroquia_id'
            for pid in parroquias:
                capacidad = random.randint(500, 5000)
                existencia = round(random.uniform(0, capacidad), 2)
                stmt = text(f"INSERT INTO almacen ({col}, existencia, capacidad) VALUES (:p, :e, :c)")
                conn.execute(stmt, {"p": pid, "e": existencia, "c": capacidad})
            conn.commit()
            print(f"Inserted almacen rows using column '{col}'")
            return

        # Case B: legacy schema (like dump) with litraje_movido / litraje_total
        if 'litraje_movido' in cols_set and 'litraje_total' in cols_set:
            # insert a small number of almacenes entries (global snapshots) tied to dates
            for i, pid in enumerate(parroquias):
                # create one entry per parroquia as a dated snapshot (no parroquia link in this schema)
                litraje_total = random.randint(500, 5000)
                litraje_movido = random.randint(0, litraje_total)
                fecha = (date.today() - timedelta(days=random.randint(0, 30))).isoformat()
                # insert depending on whether 'fecha' column exists
                if 'fecha' in cols_set:
                    conn.execute(text(
                        "INSERT INTO almacen (fecha, litraje_movido, litraje_total) VALUES (:f, :m, :t)"
                    ), {"f": fecha, "m": litraje_movido, "t": litraje_total})
                else:
                    conn.execute(text(
                        "INSERT INTO almacen (litraje_movido, litraje_total) VALUES (:m, :t)"
                    ), {"m": litraje_movido, "t": litraje_total})
            conn.commit()
            print("Inserted almacen rows using litraje_movido/litraje_total schema (no parroquia link)")
            return

        # Unknown schema -> warn and skip to avoid raising SQL errors
        print("WARNING: esquema de tabla 'almacen' no reconocido. Saltando inserciones en 'almacen'. Columnas encontradas:", cols)


def seed_entregas(engine, parroquias, start_date: date, end_date: date, avg_weekly_events=2):
    def get_table_columns(conn, table_name: str):
        res = conn.execute(text(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t"
        ), {"t": table_name})
        return [r[0] for r in res.fetchall()]

    with engine.connect() as conn:
        cols = get_table_columns(conn, 'entrega')
        cols_set = set(cols)

        # Only proceed if expected columns exist
        if {'parroquia', 'fecha_entrega', 'cantidad'}.issubset(cols_set):
            curr = start_date
            inserts = []
            while curr <= end_date:
                for pid in parroquias:
                    # cada semana crear algunas entregas distribuidas aleatoriamente
                    if random.random() < (avg_weekly_events / 7.0):
                        cantidad = round(random.uniform(50, 500), 2)
                        inserts.append({"p": pid, "f": curr.isoformat(), "c": cantidad})
                curr += timedelta(days=1)

            # Bulk insert
            for row in inserts:
                conn.execute(text(
                    "INSERT INTO entrega (parroquia, fecha_entrega, cantidad) VALUES (:p, :f, :c)"
                ), row)
            conn.commit()
            print("Inserted entrega rows using parroquia/fecha_entrega/cantidad schema")
            return

        # If schema doesn't match expected, warn and skip to avoid runtime errors
        print("WARNING: esquema de tabla 'entrega' no contiene columnas esperadas (parroquia/fecha_entrega/cantidad). Columnas encontradas:", cols)


def seed_solicitudes_for_voceros(engine, voceros_cedulas):
    # Solo generar solicitudes para los voceros creados en esta ejecución
    with engine.connect() as conn:
        for cedula in voceros_cedulas:
            # crear entre 0 y 3 solicitudes por vocero para aumentar probabilidad de pendientes
            n = random.choices([0,1,2,3], weights=[0.4,0.4,0.15,0.05])[0]
            for _ in range(n):
                # evitar duplicar innecesariamente: limitamos inserciones por vocero si ya existen muchas
                exists = conn.execute(text("SELECT COUNT(*) FROM solicitud WHERE vocero_comunal = :c"), {"c": cedula}).scalar()
                if exists and exists > 5:
                    break
                # aumentar la probabilidad de estado 'PENDIENTE' para generar entregas pendientes
                estado = random.choices(["PENDIENTE", "POR PAGAR", "VALIDANDO", "FINALIZADA"], weights=[0.6,0.2,0.15,0.05])[0]
                conn.execute(text(
                    "INSERT INTO solicitud (fecha, estado, vocero_comunal) VALUES (CURDATE(), :estado, :cedula)"
                ), {"estado": estado, "cedula": cedula})
        conn.commit()


def create_comunidades_consejos_voceros(engine, parroquias, comunidades_por_parroquia=2, consejos_por_comunidad=1):
    voceros_creados = []
    with engine.connect() as conn:
        for pid in parroquias:
            for ci in range(random.randint(1, comunidades_por_parroquia)):
                # calcular id manual para comunidad (resiliente ante dumps sin AI)
                next_id = conn.execute(text("SELECT IFNULL(MAX(id),0)+1 FROM comunidad")).scalar()
                nombre_com = f"{fake.city()} {pid}-{ci}"
                # asegurar nombre único (algunos dumps tienen índice único sobre nombre)
                tries = 0
                base_nombre = nombre_com
                while True:
                    exists_cnt = conn.execute(text("SELECT COUNT(*) FROM comunidad WHERE nombre = :nombre"), {"nombre": nombre_com}).scalar()
                    if not exists_cnt:
                        break
                    tries += 1
                    nombre_com = f"{base_nombre}-{random.randint(1000,9999)}"
                    if tries > 5:
                        # fallback: usar id como sufijo
                        nombre_com = f"{base_nombre}-{next_id}"
                        break
                conn.execute(text("INSERT INTO comunidad (id, nombre, parroquia_id) VALUES (:id, :nombre, :p)"), {"id": next_id, "nombre": nombre_com, "p": pid})
                comunidad_id = next_id

                for cj in range(random.randint(1, consejos_por_comunidad)):
                    rif = f"R{random.randint(10000000,99999999)}{random.randint(10,99)}"
                    nombre_consejo = f"Consejo {fake.last_name()} {pid}-{ci}-{cj}"
                    conn.execute(text("INSERT INTO consejo_comunal (rif, nombre, solicitud, estado, comunidad_id) VALUES (:rif, :nombre, 'DISPONIBLE', 1, :comid)"), {"rif": rif, "nombre": nombre_consejo, "comid": comunidad_id})

                    # crear un vocero activo por consejo
                    cedula = f"{random.randint(10000000,99999999)}"
                    nombre = fake.first_name()
                    apellido = fake.last_name()
                    telefono = fake.phone_number()
                    fecha_inicio = (date.today() - timedelta(days=random.randint(0, 365))).isoformat()
                    conn.execute(text(
                        "INSERT INTO vocero_comunal (cedula, nombre, apellido, telefono, fecha_inicio, fecha_final, estado, consejo_comunal_rif) VALUES (:cedula, :nombre, :apellido, :telefono, :fini, NULL, 1, :rif)"
                    ), {"cedula": cedula, "nombre": nombre, "apellido": apellido, "telefono": telefono, "fini": fecha_inicio, "rif": rif})
                    voceros_creados.append(cedula)
        conn.commit()
    return voceros_creados


def seed_periodos(engine, parroquias=None, open_pct=0.05, close_pct=0.02):
    """
    Insert periodos with some fraction of parroquias starting or ending today.
    - open_pct: fraction of parroquias to receive a periodo with fecha_inicio = today
    - close_pct: fraction of parroquias to receive a periodo with fecha_final = today
    """
    today = date.today()
    with engine.connect() as conn:
        # detectar columnas reales en la tabla periodo
        res = conn.execute(text(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'periodo'"
        ))
        cols = [r[0] for r in res.fetchall()]
        final_col = 'fecha_fin' if 'fecha_fin' in cols else ('fecha_final' if 'fecha_final' in cols else None)
        parroquia_col = 'parroquia_id' if 'parroquia_id' in cols else ('parroquia' if 'parroquia' in cols else None)

        # si la tabla requiere parroquia y no nos pasaron una lista, intentar obtener algunas
        if parroquia_col and not parroquias:
            parroquias = [r[0] for r in conn.execute(text("SELECT id FROM parroquia LIMIT 50")).fetchall()]

        def insert_period(inicio_date, fin_date=None, parroquia_val=None):
            params = {"inicio": inicio_date.isoformat()}
            cols_sql = ['fecha_inicio']
            if final_col and fin_date is not None:
                cols_sql.append(final_col)
                params['fin'] = fin_date.isoformat()

            if parroquia_col:
                cols_sql.append(parroquia_col)
                params['p'] = parroquia_val

            cols_fragment = ", ".join(cols_sql)
            vals_fragment = ", ".join([f":{ 'fin' if c in (final_col,) else ('p' if c==parroquia_col else 'inicio') }" for c in cols_sql])
            stmt = text(f"INSERT INTO periodo ({cols_fragment}) VALUES ({vals_fragment})")
            conn.execute(stmt, params)

        # Create periodos that start today for a configurable fraction of parroquias
        if parroquia_col and parroquias:
            k_open = max(1, int(len(parroquias) * open_pct))
            selected_open = random.sample(parroquias, min(k_open, len(parroquias)))
            for pid in selected_open:
                insert_period(today, today + timedelta(days=7), pid)

            # Create periodos that end today for another fraction
            k_close = int(len(parroquias) * close_pct)
            if k_close > 0:
                selected_close = random.sample(parroquias, min(k_close, len(parroquias)))
                for pid in selected_close:
                    # create a period that ends today (started sometime earlier)
                    inicio = today - timedelta(days=random.randint(7, 60))
                    insert_period(inicio, today, pid)

        # Añadir algunos periodos antiguos para diversidad
        for i in range(1, 6):
            inicio = today - timedelta(days=30 * i)
            fin = inicio + timedelta(days=5)
            parroquia_val = random.choice(parroquias) if parroquia_col and parroquias else None
            insert_period(inicio, fin, parroquia_val)

        conn.commit()


def main(args):
    engine = create_engine(DB_URI)
    print(f"Conectando a: {DB_URI}")

    ensure_tables(engine)

    # obtener parroquias del municipio 147
    with engine.connect() as conn:
        parroquias = [r[0] for r in conn.execute(text("SELECT id FROM parroquia WHERE municipio_id = 147")).fetchall()]

    if not parroquias:
        print("No se encontraron parroquias con municipio_id = 147. Abortando.")
        return

    print(f"Usando {len(parroquias)} parroquias del municipio 147")

    print("Poblando almacenes para las parroquias seleccionadas...")
    seed_almacenes(engine, parroquias)

    print("Poblando entregas para las parroquias seleccionadas (esto puede tardar)...")
    seed_entregas(engine, parroquias, args.start_date, args.end_date, avg_weekly_events=args.avg_weekly)

    print("Creando comunidades, consejos comunales y voceros para estas parroquias...")
    voceros = create_comunidades_consejos_voceros(engine, parroquias, comunidades_por_parroquia=2, consejos_por_comunidad=1)

    print(f"Creando solicitudes para {len(voceros)} voceros creados...")
    seed_solicitudes_for_voceros(engine, voceros)

    print("Poblando periodos (se añaden periodos de ejemplo)...")
    seed_periodos(engine, parroquias=parroquias, open_pct=args.open_pct, close_pct=args.close_pct)

    print("Seed completado. Ejecuta el ETL: python etl_features_parroquia_daily.py")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seed DB con datos sintéticos para EPSDC-IA')
    parser.add_argument('--parroquias', type=int, default=200, help='Número de parroquias a generar')
    parser.add_argument('--start-date', type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(), default=(date.today() - timedelta(days=365)), help='Fecha inicio de generación de entregas (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(), default=date.today(), help='Fecha fin de generación de entregas (YYYY-MM-DD)')
    parser.add_argument('--avg-weekly', type=float, default=2.0, help='Promedio diario de eventos por semana (controla frecuencia de entregas)')
    parser.add_argument('--solicitud-prob', dest='solicitud_prob', type=float, default=0.02, help='Probabilidad diaria de solicitud por parroquia')
    parser.add_argument('--open-pct', dest='open_pct', type=float, default=0.05, help='Fracción de parroquias que reciben un periodo que inicia hoy (ej. 0.1 = 10%%)')
    parser.add_argument('--close-pct', dest='close_pct', type=float, default=0.02, help='Fracción de parroquias que reciben un periodo que finaliza hoy')
    args = parser.parse_args()
    main(args)
