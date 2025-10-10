## 🚀 Sistema de Recomendação de Filmes IMDB (CheckPoint #2)

Este projeto implementa um sistema de recomendação de filmes baseado em **Clusterização Semântica** das sinopses. Utilizando técnicas avançadas de Processamento de Linguagem Natural (NLP) e um modelo de aprendizado de máquina, o sistema agrupa filmes com enredos e temas similares, oferecendo aos usuários recomendações mais relevantes e coerentes.

O projeto foi desenvolvido como parte do Checkpoint #2 do curso, abrangendo a extração, enriquecimento de dados por IA Generativa, treinamento de modelo e implantação do WebApp.

### 👥 Integrantes do Grupo

| RM | Nome Completo |
| :--- | :--- |
| 555762 | Ana Carolina Martins |
| 555848 | Andre Rovai Jr |
| 554707 | Lancelot Chagas Rodrigues |
| 555082 | Kauan Alves |

---

### 🌟 Funcionalidades e Escolhas Técnicas

#### 1. Enriquecimento de Dados (Bônus de IA Generativa)

*   **Fonte:** API do OpenAI (GPT-4o-mini).
*   **Processo:** O script `enrich_data.py` reescreveu a coluna `sinopse` original para criar a coluna `sinopse_enriched`, utilizando um prompt de "roteirista de Hollywood" para gerar descrições mais ricas, dramáticas e engajadoras.
*   **Valor:** A nova sinopse enriquecida foi usada como entrada para o modelo de clusterização, melhorando a qualidade semântica dos agrupamentos.

#### 2. Armazenamento e Integração de Dados

*   **Estrutura Final:** Um arquivo CSV centralizado (`all_movies_clustered_final.csv`) foi criado, combinando os dados originais, a sinopse enriquecida por IA e a coluna final de `Cluster`.
*   **Dados Extras:** O script `tmdb_fetcher.py` integrou informações relevantes do TMDB (The Movie Database), como **Diretor, Elenco, Capa, Trailer, Orçamento e Bilheteria**, que são exibidas no WebApp para enriquecer a experiência do usuário.

#### 3. Modelo de Clusterização e Justificativa

*   **Modelo Escolhido:** **K-Means (Sklearn)** treinado sobre **Embeddings BERT** (utilizando `sentence-transformers`).
*   **Justificativa Técnica:**
    *   O **K-Means** é robusto e eficiente para a criação de "n" clusters bem definidos (no caso, 5 clusters, escolhidos para uma boa diversidade de temas).
    *   O uso de **Embeddings BERT** (em vez de TF-IDF simples) é crucial. Enquanto TF-IDF mede a frequência de palavras, o BERT captura o **significado contextual e a semântica** das frases. Isso significa que filmes com sinopses que usam palavras diferentes, mas com temas semelhantes (ex: "inteligência artificial" vs. "máquina que pensa"), serão agrupados corretamente.

#### 4. WebApp e Sistema de Recomendação (Método 1)

*   **Plataforma:** Streamlit (`streamlit_app.py`).
*   **Método Implementado:** **Método 1 (Escolha por Sinopse Oculta):**
    1.  Apresenta ao usuário **5 sinopses enriquecidas** aleatórias, sem revelar o título.
    2.  O filme escolhido é identificado e seu `Cluster` (gerado pelo modelo BERT/K-Means) é determinado.
    3.  **Critério de Recomendação:** O sistema recomenda os **5 melhores filmes** do mesmo cluster, utilizando o seguinte critério:
        *   **Critério Principal:** Maior `rating` (nota IMDb).
        *   **Critério de Desempate:** Ano de lançamento (`year`) mais recente.
*   **Apresentação do Resultado:** Os filmes recomendados são exibidos em "cards" ricos em detalhes, incluindo trailer (via embed do YouTube), imagem da capa, diretor, elenco, orçamento e bilheteria.

---

### 🔗 Links e Entregáveis

| Entregável | Link |
| :--- | :--- |
| **Repositório GitHub** | `https://github.com/andrerovaijr216/imdb_recommender.git` |
| **Web App (Deploy Streamlit)** | `(https://imdbrecommender-5qmowd85hdmvjt6xecm5bv.streamlit.app/)` |

---

### ⚙️ Instruções de Instalação e Execução Local

1.  **Clone o Repositório e Configure o Ambiente Virtual:**
    ```bash
    git clone [[LINK DO REPOSITÓRIO](https://github.com/andrerovaijr216/imdb_recommender.g)]
    cd imdb_recommender
    python3.11 -m venv .venv
    .venv\Scripts\activate # ou source .venv/bin/activate
    ```

2.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure o `.env`:**
    Crie o arquivo `.env` na raiz do projeto com suas chaves de API:
    ```
    OPENAI_API_KEY="SUA_CHAVE_OPENAI"
    TMDB_API_KEY="SUA_CHAVE_TMDB"
    ```

4.  **Execute os Scripts de Preparação e Treinamento:**
    ```bash
    # 1. Enriquecimento de Sinopses (GPT-4o-mini)
    python enrich_data.py
    
    # 2. Treinamento do Modelo (BERT + KMeans)
    python train_model.py
    ```

5.  **Inicie o Streamlit App:**
    ```bash
    streamlit run streamlit_app.py
    ```
