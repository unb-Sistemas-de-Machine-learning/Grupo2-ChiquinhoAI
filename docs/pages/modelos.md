# Modelos de Machine Learning

## 1. Modelos de Inteligência Artificial Utilizados

Para construir um sistema capaz de responder perguntas sobre os documentos da UnB, utilizamos dois tipos principais de modelos de inteligência artificial. Essa combinação segue uma arquitetura chamada **RAG (Retrieval-Augmented Generation)**, que integra busca semântica e geração de texto para fornecer respostas precisas e contextualizadas.

### 1.1. Modelo de Geração (LLM)

O modelo de geração é responsável por compreender a pergunta do usuário e produzir uma resposta em linguagem natural.

- Modelo utilizado: Gemini, acessado por meio da API do Google.  
- O modelo não é treinado diretamente com os documentos da UnB. Ao receber uma pergunta, o sistema envia um prompt ao Gemini com os trechos de texto mais relevantes extraídos dos PDFs, e o modelo gera a resposta de forma contextualizada.  
- Flexibilidade: É possível substituir o modelo de linguagem por outros, como GPT-4o (OpenAI), Claude 3 (Anthropic) ou Llama 3 (open-source), sem alterar o restante da arquitetura.

### 1.2. Modelo de Embedding

O modelo de embedding é fundamental para a busca semântica do sistema.

- Função: Converte trechos de texto em vetores numéricos que representam o significado semântico do conteúdo.  
- Uso na ingestão: Cada trecho de PDF é convertido em vetor e armazenado no Qdrant, junto com metadados.  
- Uso na busca: A pergunta do usuário também é convertida em vetor, e o Qdrant retorna os trechos mais próximos semanticamente.  
- Exemplos de modelos: text-embedding-004 (Google), text-embedding-3-small (OpenAI), all-MiniLM-L6-v2 (open-source).

---

## 2. Fluxos de Funcionamento

### 2.1. Ingestão de Dados (ETL)

O processo de ingestão dos documentos ocorre de forma automática:

1. O WebScraper baixa periodicamente os PDFs da UnB.  
2. Os arquivos são salvos localmente em uma pasta específica.  
3. O conteúdo dos PDFs é enviado ao backend por meio do controller.  
4. O service divide o texto em chunks menores para facilitar a busca semântica.  
5. Cada chunk é transformado em vetor pelo modelo de embedding.  
6. O repository salva no Qdrant o vetor, o texto e metadados básicos (nome do arquivo, página e caminho local).

---

### 2.2. Resposta ao Usuário (RAG)

Quando o usuário envia uma pergunta, o fluxo é o seguinte:

1. A pergunta chega via API.Telegram e é repassada ao controller do backend.  
2. O service transforma a pergunta em vetor com o mesmo modelo de embedding utilizado nos chunks.  
3. O Qdrant retorna os trechos mais semanticamente próximos (normalmente os cinco mais relevantes).  
4. O service monta o prompt final:
    ```
    Contexto: [Chunk 1], [Chunk 2], ...
    Pergunta: [Pergunta do usuário].
    Responda com base apenas no contexto fornecido.
    ```  
5. O prompt é enviado ao LLM provider, que encaminha ao Gemini.  
6. O Gemini gera a resposta, que percorre o caminho de volta: service → controller → API.Telegram → usuário.

---


## 3. Abordagem de Dados e Engenharia

### 3.1. Coleta e armazenamento de dados

- Os PDFs são coletados automaticamente pelo WebScraper e salvos em uma pasta localS.  
- O Qdrant armazena os vetores, trechos de texto e metadados (nome do arquivo, página e caminho local).  
- Essa estrutura permite consultas rápidas sem armazenar os arquivos binários no banco de dados.

---

### 3.2. Amostragem de dados

- Nenhuma amostragem foi aplicada, garantindo que todo o conteúdo disponível seja indexado.

---

### 3.3. Rotulação de dados

- Não houve necessidade de rotulação manual.  
- Os embeddings permitem identificar automaticamente os trechos mais relevantes para cada pergunta.

---

### 3.4. Balanceamento de classes

- Não se aplica, pois o sistema não realiza tarefas de classificação.  
- A distribuição desigual de documentos reflete apenas o acervo real da UnB.

---

### 3.5. Falta de dados e estratégias de expansão

- Se algum tema estiver pouco representado, a solução é melhorar a coleta de dados e identificar novas fontes de PDFs.

---

### 3.6. Feature Engineering

- Missing values: PDFs corrompidos ou páginas em branco são descartados.  
- Outliers: Trechos irrelevantes ou muito curtos são filtrados.  
- Enriquecimento: Cada ponto no Qdrant inclui vetor, texto e metadados (arquivo, página, caminho, data de coleta):
    ```json
    {
      "texto": "O prazo para trancamento é dia 10...",
      "vetor": [0.12, 0.45, ...],
      "metadados": {
          "arquivo": "calendario_academico_2025.pdf",
          "pagina": 4,
          "caminho": "media/pdf/calendario_academico_2025.pdf",
          "data_coleta": "2025-10-18"
      }
    }
    ```
- Remoção de informações irrelevantes: Cabeçalhos, rodapés e padrões repetitivos são eliminados.  
- Normalização e padronização: Texto limpo e vetores normalizados.  
- One-hot encoding: Não utilizado; embeddings representam significado e relações entre palavras.

---

### 3.7. Dados de treinamento e avaliação

- A ingestão dos PDFs funciona como “treinamento” do sistema.  
- Para avaliação, um conjunto de teste com pares `(Pergunta, Resposta Esperada)` é utilizado.  
- Um script compara respostas reais com as esperadas, permitindo ajustes nos parâmetros.

**Exemplo de teste:**  
- Pergunta: “Qual o prazo para trancar disciplina?”  
- Resposta esperada: “O prazo é dia 10 de novembro, conforme o Calendário Acadêmico.”
