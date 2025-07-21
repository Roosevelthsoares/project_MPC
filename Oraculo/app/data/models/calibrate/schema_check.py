import pandas as pd

# Caminhos dos arquivos
csv_path = "/home/roosevelth/project/CICFlowMeter/flows/teste_ether.pcap_Flow.csv"
parquet_path = "/home/roosevelth/project/Oraculo/app/data/models/calibrate/CICIDS2018_preprocessed_test.parquet"

# Leitura dos headers
csv_columns = list(pd.read_csv(csv_path, nrows=0).columns)
parquet_columns = list(pd.read_parquet(parquet_path).columns)

# Ajustar tamanho das listas para terem o mesmo comprimento
max_len = max(len(csv_columns), len(parquet_columns))
csv_columns += [''] * (max_len - len(csv_columns))
parquet_columns += [''] * (max_len - len(parquet_columns))

# Criar DataFrame de comparação
df = pd.DataFrame({
    "CSV Columns": csv_columns,
    "Parquet Columns": parquet_columns
})

# Caminho de saída
output_path = "schema_comparison.csv"

# Salvar
df.to_csv(output_path, index=False)
print(f"Comparação de schemas salva em: {output_path}")
