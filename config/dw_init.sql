-- Criação das tabelas no Data Warehouse
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- Tabelas de staging (estrutura idêntica às fontes)
CREATE TABLE IF NOT EXISTS staging.transacoes (
    cod_transacao BIGINT,
    num_conta BIGINT,
    data_transacao TIMESTAMP,
    nome_transacao VARCHAR(255),
    valor_transacao DECIMAL(15,2)
);

CREATE TABLE IF NOT EXISTS staging.agencias (
    cod_agencia INTEGER,
    nome VARCHAR(255),
    endereco TEXT,
    cidade VARCHAR(255),
    uf CHAR(2),
    data_abertura DATE,
    tipo_agencia VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS staging.clientes (
    cod_cliente INTEGER,
    primeiro_nome VARCHAR(255),
    ultimo_nome VARCHAR(255),
    email VARCHAR(255),
    tipo_cliente VARCHAR(20),
    data_inclusao TIMESTAMP WITH TIME ZONE,
    cpfcnpj VARCHAR(18),
    data_nascimento DATE,
    endereco TEXT,
    cep VARCHAR(9)
);

CREATE TABLE IF NOT EXISTS staging.colaboradores (
    cod_colaborador INTEGER,
    primeiro_nome VARCHAR(255),
    ultimo_nome VARCHAR(255),
    email VARCHAR(255),
    cpf VARCHAR(14),
    data_nascimento DATE,
    endereco TEXT,
    cep VARCHAR(9)
);

CREATE TABLE IF NOT EXISTS staging.colaborador_agencia (
    cod_colaborador INTEGER,
    cod_agencia INTEGER
);

CREATE TABLE IF NOT EXISTS staging.contas (
    num_conta BIGINT,
    cod_cliente INTEGER,
    cod_agencia INTEGER,
    cod_colaborador INTEGER,
    tipo_conta VARCHAR(20),
    data_abertura TIMESTAMP WITH TIME ZONE,
    saldo_total DECIMAL(15,2),
    saldo_disponivel DECIMAL(15,2),
    data_ultimo_lancamento TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS staging.propostas_credito (
    cod_proposta INTEGER,
    cod_cliente INTEGER,
    cod_colaborador INTEGER,
    data_entrada_proposta TIMESTAMP WITH TIME ZONE,
    taxa_juros_mensal DECIMAL(5,4),
    valor_proposta DECIMAL(15,2),
    valor_financiamento DECIMAL(15,2),
    valor_entrada DECIMAL(15,2),
    valor_prestacao DECIMAL(15,2),
    quantidade_parcelas INTEGER,
    carencia INTEGER,
    status_proposta VARCHAR(50)
);

-- Tabela de controle de execuções
CREATE TABLE IF NOT EXISTS staging.etl_execucoes (
    id SERIAL PRIMARY KEY,
    dag_id VARCHAR(255),
    task_id VARCHAR(255),
    data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    registros_processados INTEGER,
    origem VARCHAR(100),
    destino VARCHAR(100)
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_transacoes_data ON staging.transacoes(data_transacao);
CREATE INDEX IF NOT EXISTS idx_transacoes_conta ON staging.transacoes(num_conta);
CREATE INDEX IF NOT EXISTS idx_contas_cliente ON staging.contas(cod_cliente);
CREATE INDEX IF NOT EXISTS idx_clientes_cod ON staging.clientes(cod_cliente);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA staging TO dw_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA marts TO dw_user;
GRANT ALL PRIVILEGES ON SCHEMA staging TO dw_user;
GRANT ALL PRIVILEGES ON SCHEMA marts TO dw_user;
