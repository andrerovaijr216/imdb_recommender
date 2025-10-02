import pandas as pd
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# Carrega as variáveis de ambiente
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("ERRO: A variável OPENAI_API_KEY não está configurada no arquivo .env.")
    exit()

# Inicializa o cliente da OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Configurações de arquivos
INPUT_FILE = 'all_movies.csv'
OUTPUT_FILE = 'all_movies_enriched.csv'
MODEL_NAME = 'gpt-4o-mini'

def get_enriched_synopsis(original_synopsis: str) -> str:
    """Chama o GPT-4o-mini para enriquecer uma sinopse em Português."""
    
    # Prompt de Sistema: Define o tom e o estilo.
    system_prompt = (
        "Você é um roteirista de Hollywood. Sua tarefa é pegar uma sinopse de filme curta e, "
        "sem alterar o enredo principal ou o final, reescrevê-la em Português para torná-la "
        "mais rica, dramática e envolvente, com uma linguagem de trailer. "
        "Mantenha o texto com até 4 frases. Retorne APENAS a sinopse reescrita, sem introduções ou comentários."
    )
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Sinopse original: {original_synopsis}"}
            ],
            temperature=0.7 # Adiciona criatividade para o enriquecimento
        )
        # Extrai a resposta do modelo
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Erro na API para sinopse: '{original_synopsis[:30]}...' Erro: {e}")
        return original_synopsis # Retorna a original em caso de falha

def enrich_data():
    """Processa o DataFrame e enriquece as sinopses."""
    if not os.path.exists(INPUT_FILE):
        print(f"Erro: Arquivo de entrada '{INPUT_FILE}' não encontrado.")
        return

    df = pd.read_csv(INPUT_FILE, sep=';')
    
    # Cria uma nova coluna para o enriquecimento
    df['sinopse_enriched'] = df['sinopse']
    
    print(f"Iniciando enriquecimento de {len(df)} sinopses com {MODEL_NAME}...")
    
    for index, row in df.iterrows():
        original_synopsis = row['sinopse']
        
        # Chama a função de enriquecimento
        enriched_synopsis = get_enriched_synopsis(original_synopsis)
        
        # Atualiza o DataFrame
        df.loc[index, 'sinopse_enriched'] = enriched_synopsis
        
        print(f"[{index+1}/{len(df)}] Enriquecida: '{original_synopsis[:30]}...' -> '{enriched_synopsis[:30]}...'")
        
        # Pausa para evitar rate limiting (1 segundo é conservador e seguro)
        time.sleep(1)

    # Salva o novo arquivo
    df.to_csv(OUTPUT_FILE, index=False, sep=';')
    print("\n--- Processo Concluído ---")
    print(f"Novo arquivo de dados salvo em: {OUTPUT_FILE}")
    print("Próximo passo: Atualize 'train_model.py' e 'streamlit_app.py' para usarem este novo arquivo.")

if __name__ == '__main__':
    enrich_data()