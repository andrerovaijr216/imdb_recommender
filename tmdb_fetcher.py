import os
import requests
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Dicionário para armazenar em cache os resultados do TMDB (simples cache em memória)
# É melhor usar o @st.cache_data do Streamlit para isso, mas o fetcher pode usar um fallback.

def fetch_movie_videos(movie_id):
    """Busca os vídeos (trailers) de um filme."""
    videos_url = f"{TMDB_BASE_URL}/movie/{movie_id}/videos"
    videos_params = {'api_key': TMDB_API_KEY, 'language': 'en-US'} # Tentar em EN para ter mais resultados de trailer
    
    try:
        res_videos = requests.get(videos_url, params=videos_params).json()
        
        # Filtra por trailer, do YouTube, e pega a primeira chave
        trailer_key = next((
            video['key'] 
            for video in res_videos.get('results', []) 
            if video['site'] == 'YouTube' and 'Trailer' in video['type']
        ), None)
        
        if trailer_key:
            return f"https://www.youtube.com/watch?v={trailer_key}"
        return None
    except:
        return None

def search_movie_tmdb(title_en, year):
    """Busca a ID do filme pelo título e ano."""
    if not TMDB_API_KEY:
        print("Erro: TMDB_API_KEY não está configurada.")
        return None

    params = {
        'api_key': TMDB_API_KEY,
        'query': title_en,
        'year': year,
        'language': 'pt-BR'
    }
    
    try:
        response = requests.get(f"{TMDB_BASE_URL}/search/movie", params=params)
        response.raise_for_status()
        results = response.json().get('results', [])
        
        if results:
            return results[0].get('id')
        return None

    except requests.exceptions.RequestException as e:
        print(f"Erro de requisição TMDB: {e}")
        return None

def fetch_movie_details(movie_id):
    """Busca detalhes, créditos e vídeos do filme."""
    if not movie_id:
        return {}

    details_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    credits_url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits"
    
    details_params = {'api_key': TMDB_API_KEY, 'language': 'pt-BR'}
    credits_params = {'api_key': TMDB_API_KEY}

    details = {}
    
    # 1. Detalhes (Capa, Trailer, Orçamento/Receita)
    try:
        res_details = requests.get(details_url, params=details_params).json()
        details['poster_url'] = f"{TMDB_IMAGE_BASE_URL}{res_details.get('poster_path')}" if res_details.get('poster_path') else None
        details['budget'] = res_details.get('budget', 0)
        details['revenue'] = res_details.get('revenue', 0)
    except:
        pass

    # 2. Créditos (Diretor e Atores)
    try:
        res_credits = requests.get(credits_url, params=credits_params).json()
        director = next((crew['name'] for crew in res_credits.get('crew', []) if crew['job'] == 'Director'), 'N/A')
        details['director'] = director
        cast = [actor['name'] for actor in res_credits.get('cast', [])[:3]]
        details['cast'] = ', '.join(cast)
    except:
        details['director'] = 'N/A'
        details['cast'] = 'N/A'

    # 3. Vídeos (Trailer)
    details['trailer_url'] = fetch_movie_videos(movie_id)

    return details

def get_full_movie_data(title_en, year):
    """Função combinada para buscar todos os dados extras."""
    movie_id = search_movie_tmdb(title_en, year)
    if movie_id:
        return fetch_movie_details(movie_id)
    return {
        'poster_url': None, 
        'director': 'N/A', 
        'cast': 'N/A', 
        'budget': 0, 
        'revenue': 0,
        'trailer_url': None
    }

# Exemplo de uso (opcional)
if __name__ == '__main__':
    data = get_full_movie_data("Barbie", 2023)
    print(data)