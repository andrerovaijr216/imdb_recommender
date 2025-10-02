import streamlit as st
import pandas as pd
import numpy as np
import pickle
from random import sample
import os
from tmdb_fetcher import get_full_movie_data 

# --- Configurações e Carregamento de Dados/Modelo ---

CLUSTER_MODEL_PATH = 'kmeans_bert_model.pkl'
# MUDEI AQUI: Nome do arquivo final criado pelo train_model.py
CLUSTERED_DATA_PATH = 'all_movies_clustered_final.csv'
N_OPTIONS = 5  

# Verifica se os arquivos de dados e modelo existem
if not all(os.path.exists(p) for p in [CLUSTERED_DATA_PATH, CLUSTER_MODEL_PATH]):
    st.error("ERRO: Arquivos de modelo e/ou dados não encontrados. Execute 'python enrich_data.py' e 'python train_model.py' primeiro.")
    st.stop()

# Carregar o DataFrame com os clusters
df = pd.read_csv(CLUSTERED_DATA_PATH, sep=';')

# A sinopse de exibição e clusterização é a ENRIQUECIDA.
SYNOPSIS_COLUMN = 'sinopse_enriched'

# Função para carregar o modelo de clusterização (não essencial para este app)
try:
    with open(CLUSTER_MODEL_PATH, 'rb') as file:
        kmeans_model = pickle.load(file)
except:
    kmeans_model = None

# --- Funções de Lógica de Recomendação ---

def get_random_synopsis_options(n):
    """Seleciona N sinopses *enriquecidas* aleatórias, com seus IDs no DF."""
    indices = df.sample(n=n, random_state=np.random.randint(1, 1000)).index.tolist()
    # MUDEI AQUI: Usa a sinopse ENRIQUECIDA
    options = [{'id': idx, 'sinopse': df.loc[idx, SYNOPSIS_COLUMN]} for idx in indices]
    return options

def recommend_movies_from_cluster(chosen_id, cluster_id, n_recommendations=5):
    """
    Recomenda os melhores filmes do cluster (excluindo o filme escolhido).
    Critério: 
    1. Maior Rating.
    2. Mais Recente (Year).
    """
    # 1. Filtrar pelo cluster
    df_cluster = df[df['Cluster'] == cluster_id].copy()
    
    # 2. Excluir o filme que deu a origem (para não recomendar ele mesmo)
    df_cluster = df_cluster[df_cluster.index != chosen_id]
    
    # 3. Classificar por Rating (decrescente) e Ano (decrescente)
    df_cluster = df_cluster.sort_values(by=['rating', 'year'], ascending=[False, False])
    
    # 4. Selecionar os top N
    recommendations = df_cluster.head(n_recommendations).to_dict('records')
    
    return recommendations

# --- Componentes da Interface de Usuário ---

# Usando st.cache_data para cachear os resultados do TMDB
@st.cache_data(ttl=60*60*24)
def fetch_tmdb_data_cached(title_en, year):
    if pd.isna(title_en) or title_en is None or pd.isna(year) or year is None:
        return {}
    return get_full_movie_data(title_en, int(year))

def display_movie_card(movie_data):
    """Exibe um card detalhado do filme, incluindo o trailer e a sinopse enriquecida."""
    st.markdown("---")
    
    # Colunas para Capa (1) e Trailer (2)
    col_poster, col_video = st.columns([1, 2])
    
    # Colunas para os detalhes (sem imagem e vídeo)
    col_details, _ = st.columns([4, 1])

    # 1. Busca de dados adicionais do TMDB (usando a função cacheada)
    tmdb_data = fetch_tmdb_data_cached(movie_data['title_en'], movie_data['year'])

    # 2. COLUNA POSTER: Capa
    with col_poster:
        if tmdb_data.get('poster_url'):
            st.image(tmdb_data['poster_url'], caption=f"{movie_data['title_pt']}", use_container_width=True) 
        else:
            st.write("*(Capa indisponível)*")
    
    # 3. COLUNA VÍDEO: Trailer
    with col_video:
        if tmdb_data.get('trailer_url'):
            st.video(tmdb_data['trailer_url'])
        else:
            st.write("*(Trailer indisponível)*")

    # 4. COLUNA DETALHES
    with col_details:
        st.subheader(f"🎬 {movie_data['title_pt']} ({movie_data['year']})")
        
        # Detalhes principais
        st.markdown(f"**Gênero:** {movie_data['genre']} | **IMDb:** {movie_data['rating']} ⭐")
        st.markdown(f"**Diretor:** {tmdb_data.get('director', 'N/A')}")
        st.markdown(f"**Elenco:** {tmdb_data.get('cast', 'N/A')}")

        # Sinopse
        st.markdown("##### Sinopse (Enriquecida por IA):")
        # MUDEI AQUI: Exibe a sinopse ENRIQUECIDA
        st.write(movie_data[SYNOPSIS_COLUMN]) 

        # Detalhes financeiros
        budget = tmdb_data.get('budget', 0)
        revenue = tmdb_data.get('revenue', 0)
        
        budget_display = f"Orçamento: ${budget:,.0f}" if budget > 0 else "Orçamento: N/A"
        revenue_display = f"Bilheteria: ${revenue:,.0f}" if revenue > 0 else "Bilheteria: N/A"
        
        st.markdown(f"💸 *{budget_display}* | *{revenue_display}*")


# --- Layout Principal do Streamlit ---

st.set_page_config(
    page_title="IMDb Cluster Recommender",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Sistema de Recomendação de Filmes por Sinopse (IA Generativa)")
st.markdown("Recomendação baseada em clustering semântico das **Sinopses Enriquecidas** (BERT/K-Means).")

if 'options' not in st.session_state:
    st.session_state.options = get_random_synopsis_options(N_OPTIONS)
    st.session_state.chosen_id = None
    st.session_state.recommendations = None

# --- Início da Sessão: Escolha da Sinopse ---
st.header("Passo 1: Escolha uma Sinopse")
st.info("Selecione a sinopse **enriquecida** que mais lhe agrada. **Não mostraremos o título do filme.**")

options = st.session_state.options
# O mapa usa a sinopse ENRIQUECIDA para o rádio button
sinopse_map = {f"Opção {i+1}": opt['sinopse'] for i, opt in enumerate(options)}
choice_labels = list(sinopse_map.keys())

# O usuário seleciona a sinopse
selected_label = st.radio(
    "Escolha uma das opções:", 
    choice_labels,
    index=None,
    format_func=lambda x: f"{x}: {sinopse_map[x][:80]}..."
)

# Botão de reset
if st.button("🔄 Gerar Novas Opções"):
    st.session_state.options = get_random_synopsis_options(N_OPTIONS)
    st.session_state.chosen_id = None
    st.session_state.recommendations = None
    st.rerun()

if selected_label:
    # Identificar o ID do filme escolhido a partir da sinopse (agora sinopse enriquecida)
    selected_synopsis_enriched = sinopse_map[selected_label]
    
    # Encontra o ID original no DataFrame (que é o index)
    # MUDEI AQUI: Busca o ID baseado na sinopse ENRIQUECIDA
    try:
        chosen_id = df[df[SYNOPSIS_COLUMN] == selected_synopsis_enriched].index.tolist()[0] 
        chosen_movie = df.loc[chosen_id].to_dict()
        cluster_id = chosen_movie['Cluster']
        
        st.session_state.chosen_id = chosen_id
        st.session_state.recommendations = recommend_movies_from_cluster(chosen_id, cluster_id, 5)

        st.success(f"Filme escolhido! Pertence ao Cluster **{cluster_id}**.")
    except IndexError:
        st.error("Erro ao encontrar o filme no dataset. Tente gerar novas opções.")

# --- Exibição dos Resultados ---
if st.session_state.chosen_id is not None:
    
    # Garante que o chosen_movie usa o index correto do DataFrame
    chosen_movie = df.loc[st.session_state.chosen_id].to_dict()
    cluster_id = chosen_movie['Cluster'] 
    
    st.header(f"Seu Filme Escolhido (Chave para o Cluster {cluster_id})")
    display_movie_card(chosen_movie)
    
    st.header(f"Top 5 Recomendações do Cluster {cluster_id}")
    st.markdown("*(Classificados por maior nota (rating) e ano mais recente)*")
    
    for rec in st.session_state.recommendations:
        display_movie_card(rec)