import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import pickle
import os

# --- Configurações ---
N_CLUSTERS = 5 
MODEL_PATH = 'kmeans_bert_model.pkl'
# MUDEI AQUI: Nome do arquivo de entrada do treinamento.
INPUT_DATA_PATH = 'all_movies_enriched.csv' 
CLUSTERED_DATA_PATH = 'all_movies_clustered_final.csv' # Novo nome para o arquivo de saída final
SENTENCE_TRANSFORMER_MODEL = 'all-MiniLM-L6-v2' 

def train_and_save_model(df):
    """Calcula os embeddings, treina o modelo KMeans e salva os resultados."""
    print("1. Carregando o modelo Sentence Transformer...")
    try:
        model_st = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
    except Exception as e:
        print(f"Erro ao carregar o modelo ST. Tentando o fallback 'bert-base-nli-mean-tokens'. Erro: {e}")
        model_st = SentenceTransformer('bert-base-nli-mean-tokens')

    print("2. Gerando embeddings para as sinopses enriquecidas (pode demorar)...")
    
    # MUDEI AQUI: O modelo agora usa a coluna enriquecida para gerar os embeddings!
    sinopses = df['sinopse_enriched'].tolist() 
    
    # Geração dos embeddings
    embeddings = model_st.encode(sinopses, show_progress_bar=True)

    print(f"3. Treinando o modelo K-Means com {N_CLUSTERS} clusters...")
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
    
    # Treinando diretamente nos embeddings
    kmeans.fit(embeddings)
    df['Cluster'] = kmeans.labels_

    # Salvar o modelo
    with open(MODEL_PATH, 'wb') as file:
        pickle.dump(kmeans, file)
    
    print(f"Modelo KMeans salvo em: {MODEL_PATH}")
    
    # Salvar o DataFrame com os clusters
    df.to_csv(CLUSTERED_DATA_PATH, index=False, sep=';')
    print(f"Dados com clusters salvos em: {CLUSTERED_DATA_PATH}")

    print("\nTreinamento concluído. O modelo usou as sinopses enriquecidas.")


if __name__ == '__main__':
    try:
        # MUDEI AQUI: Lendo o arquivo enriquecido.
        df = pd.read_csv(INPUT_DATA_PATH, sep=';') 
        
        # Correção do problema de nome de coluna do seu CSV (removendo prefixo de ranking)
        df['title_en'] = df['title_en'].str.replace(r'^\d+\.\s*', '', regex=True)

        train_and_save_model(df.copy())
        
        # Exemplo de verificação de clusters
        df_clustered = pd.read_csv(CLUSTERED_DATA_PATH, sep=';')
        print("\nContagem de filmes por cluster:")
        print(df_clustered['Cluster'].value_counts().sort_index())

    except FileNotFoundError:
        print(f"Erro: O arquivo '{INPUT_DATA_PATH}' não foi encontrado. Execute 'python enrich_data.py' primeiro.")