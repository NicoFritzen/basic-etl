FROM apache/airflow:2.10.2-python3.11

USER root

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Instalar dependências Python
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copiar DAGs e plugins
COPY dags/ /opt/airflow/dags/
COPY plugins/ /opt/airflow/plugins/
