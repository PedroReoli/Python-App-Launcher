import pandas as pd

# Caminho do arquivo de entrada
arquivo_entrada = "nomes.xlsx"  

# Lê o arquivo sem cabeçalho
df = pd.read_excel(arquivo_entrada, header=None)

# Seleciona a coluna B (índice 1), remove espaços, duplicatas e ordena
nomes = df[1].dropna()                     
nomes = nomes.astype(str).str.strip()      
nomes = sorted(set(nomes))                 # Remove duplicatas 

# Cria um novo DataFrame com os nomes processados
df_resultado = pd.DataFrame(nomes, columns=["Nome"])

# Salva o resultado em um novo arquivo Excel
df_resultado.to_excel("nomes_ordenados.xlsx", index=False)

print("Arquivo salvo com sucesso como 'nomes_ordenados.xlsx'")
