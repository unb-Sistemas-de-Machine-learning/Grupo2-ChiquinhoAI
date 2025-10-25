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

## 3. Estratégia de Testes e Avaliação

Para garantir que o chatbot forneça respostas precisas e confiáveis, nossa estratégia de testes é dividida para avaliar os dois componentes centrais da arquitetura RAG: a *Recuperação* (se encontramos os documentos corretos) e a *Geração* (se a resposta gerada é boa), além de um teste completo de ponta-a-ponta.


### 3.1. Avaliação da Recuperação (Retrieval)

O primeiro passo da avaliação é garantir que o sistema realmente encontre os trechos de texto corretos nos documentos. Se essa parte falhar, toda a resposta do chatbot será comprometida.

* **Objetivo:** Verificar se o modelo de embedding e o Qdrant estão funcionando bem, ou seja, se o sistema consegue identificar os trechos de texto mais relevantes para cada pergunta.
* **Como foi feito:** Criamos um pequeno conjunto de testes (chamado *Golden Set*) com pares de pergunta e o contexto esperado. Esse contexto esperado não é o texto em si, mas os metadados do trecho onde a resposta está (por exemplo, `arquivo: "calendario_academico.pdf"`).
* **Execução:** Um script automatizado envia as perguntas para o sistema, recupera os cinco trechos mais próximos e verifica se o contexto esperado aparece entre eles.
* **Métricas usadas:**
    * **Taxa de acerto (Hit Rate @5):** Mede quantas vezes o trecho correto apareceu entre os cinco resultados retornados.
    * **MRR (Mean Reciprocal Rank):** Avalia a posição em que o trecho certo aparece — quanto mais no topo, melhor.

### 3.2. Avaliação da Geração (Generation)

Depois de garantir que o sistema está encontrando os trechos certos, o próximo passo é ver se o modelo de linguagem (Gemini) está usando bem essas informações para responder corretamente.

* **Objetivo:** Verificar se o Gemini consegue gerar respostas coerentes e fiéis, baseando-se apenas no contexto que recebeu.
* **Como foi feito:** Usamos um conjunto de perguntas com os contextos corretos e analisamos as respostas geradas.
* **Critérios avaliados:**
    * **Fidelidade:** A resposta está realmente baseada no texto fornecido, sem inventar informações?
    * **Relevância:** A resposta atende diretamente ao que foi perguntado?

### 3.3. Avaliação de Ponta a Ponta (End-to-End)

Por fim, realizamos um teste completo, simulando a experiência real do usuário — desde a pergunta no Telegram até a resposta final do sistema.

* **Objetivo:** Avaliar o desempenho do sistema como um todo, verificando se a resposta final é correta e útil.
* **Como foi feito:** Criamos pares de pergunta e resposta esperada. O script envia as perguntas ao bot e compara as respostas obtidas com as esperadas.
* **Métricas utilizadas:**
    * **Similaridade semântica:** Como o modelo pode usar palavras diferentes, não comparamos os textos de forma exata. Transformamos as respostas (a esperada e a real) em vetores e calculamos a similaridade de cosseno entre eles. Se for alta (por exemplo, acima de 0.9), o teste é considerado bem-sucedido.
    * **LLM como avaliador:** Para uma análise mais refinada, usamos um modelo de linguagem (como o Gemini 1.5 Pro) para comparar as respostas e decidir se a resposta gerada é satisfatória.
