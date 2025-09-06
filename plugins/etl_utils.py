import os
from typing import Dict
import pandas as pd
import sqlalchemy as sa

class ETLUtils:
    def __init__(self):
        self.source_conn = "postgresql+psycopg2://data_engineer:v3rysecur%26pas5w0rd@source-db:5432/banvic"
        self.dw_conn = "postgresql+psycopg2://dw_user:dw_password@data-warehouse:5432/dw_banvic"
    
    def create_output_directory(self, date_str: str, source: str) -> str:
        output_dir = os.path.join("/opt/airflow/data", date_str, source)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def extract_csv_data(self, execution_date: str) -> str:
        output_dir = self.create_output_directory(execution_date, "csv")
        source_file = "/opt/airflow/data/transacoes.csv"
        
        if not os.path.exists(source_file):
            raise FileNotFoundError(f"Arquivo fonte não encontrado: {source_file}")
        
        df = pd.read_csv(source_file)
        df['data_transacao'] = pd.to_datetime(df['data_transacao'], errors='coerce')
        df['valor_transacao'] = pd.to_numeric(df['valor_transacao'], errors='coerce')
        
        output_file = os.path.join(output_dir, "transacoes.csv")
        df.to_csv(output_file, index=False)
        return output_file
    
    def extract_sql_data(self, execution_date: str) -> Dict[str, str]:
        output_dir = self.create_output_directory(execution_date, "sql")
        tables = ['agencias', 'clientes', 'colaboradores', 'colaborador_agencia', 'contas', 'propostas_credito']
        engine = sa.create_engine(self.source_conn)
        extracted_files = {}
        
        try:
            for table in tables:
                df = pd.read_sql_table(table, engine, schema='public')
                output_file = os.path.join(output_dir, f"{table}.csv")
                df.to_csv(output_file, index=False)
                extracted_files[table] = output_file
            return extracted_files
        finally:
            engine.dispose()
    
    def load_csv_to_warehouse(self, csv_file_path: str) -> int:
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {csv_file_path}")
        
        engine = sa.create_engine(self.dw_conn)
        df = pd.read_csv(csv_file_path)
        
        try:
            with engine.begin() as conn:
                conn.execute(sa.text("DELETE FROM staging.transacoes"))
                df.to_sql('transacoes', conn, schema='staging', if_exists='append', index=False)
            return len(df)
        finally:
            engine.dispose()
    
    def load_sql_to_warehouse(self, extracted_files: Dict[str, str]) -> Dict[str, int]:
        engine = sa.create_engine(self.dw_conn)
        loaded_records = {}
        
        try:
            for table_name, file_path in extracted_files.items():
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
                
                df = pd.read_csv(file_path)
                
                with engine.begin() as conn:
                    conn.execute(sa.text(f"DELETE FROM staging.{table_name}"))
                    df.to_sql(table_name, conn, schema='staging', if_exists='append', index=False)
                
                loaded_records[table_name] = len(df)
            
            return loaded_records
        finally:
            engine.dispose()
    
    def validate_data_quality(self) -> bool:
        engine = sa.create_engine(self.dw_conn)
        tables = ['transacoes', 'clientes', 'contas', 'agencias']
        with engine.connect() as conn:
            for table in tables:
                result = conn.execute(sa.text(f"SELECT COUNT(*) FROM staging.{table}"))
                if result.fetchone()[0] == 0:
                    return False
        engine.dispose()
        return True
