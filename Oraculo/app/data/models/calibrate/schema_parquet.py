import pandas as pd

# aponte para o seu arquivo .parquet
arquivo = "/home/roosevelth/project/Oraculo/app/data/models/calibrate/CICIDS2018_preprocessed_test.parquet"

# lê somente o esquema (sem carregar tudo na memória)
df = pd.read_parquet(arquivo, engine="pyarrow")

# exibe a lista de colunas
print(df.columns.tolist())

# schema_parquet.py
# import pyarrow.parquet as pq

# arquivo = "app/data/models/calibrate/CICIDS2018_preprocessed_test.parquet"
# pqfile = pq.ParquetFile(arquivo)

# # mostra todos os campos e tipos
# print(pqfile.schema)

# # só os nomes das colunas
# print(pqfile.schema.names)

