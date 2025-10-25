<center>

# Banco de Dados Vetorial

</center>

---

#### Utilidade do Banco de Dados em Vetores

<div align="justify">

&emsp;&emsp;
Enquanto bancos de dados tradicionais são excelentes para encontrar correspondências exatas, como clientes com um nome específico ou produtos de um determinado valor, a principal utilidade de um banco de dados vetorial é localizar itens que são semanticamente similares ou conceitualmente relacionados. Sua operação não se baseia em termos literais, mas sim na "proximidade de significado" entre os dados, permitindo que as aplicações entendam o contexto.

Isso possibilita, por exemplo, a implementação de uma busca semântica avançada, onde um sistema compreende a intenção de uma consulta e retorna resultados pertinentes, mesmo que não contenham as mesmas palavras. De forma semelhante, essa tecnologia é o fundamento de sistemas de recomendação, que encontram produtos ou conteúdos com características vetoriais parecidas para sugerir itens de interesse ao usuário. Uma de suas aplicações mais proeminentes atualmente é a Geração Aumentada por Recuperação (RAG), na qual assistentes de IA consultam documentos internos para fornecer respostas precisas e contextualizadas. O mesmo princípio se aplica à busca por similaridade de imagens ou áudios e à detecção de anomalias, como identificar uma transação financeira que desvia do padrão de um cliente, sinalizando uma possível fraude. Em resumo, sua função é mover a busca do campo das palavras-chave para o do significado, permitindo que a inteligência artificial opere com uma compreensão mais profunda da informação.
</div>

---

#### O Que é o Qdrant?

<div align="justify">

&emsp;&emsp;
O Qdrant é um banco de dados vetorial de código aberto projetado para armazenar, indexar e consultar vetores de alta dimensão de forma eficiente. Ele permite realizar buscas por similaridade com alto desempenho, utilizando algoritmos de indexação como o HNSW (Hierarchical Navigable Small World), que reduz significativamente o tempo necessário para encontrar vetores próximos entre milhões de registros.Além da performance, o Qdrant oferece recursos adicionais que o tornam ideal para aplicações reais, como filtros condicionais, suporte a payloads (dados associados aos vetores), autenticação, persistência em disco e API RESTful e gRPC fáceis de integrar. Com ele, é possível combinar buscas vetoriais com consultas tradicionais, por exemplo: encontrar documentos semanticamente semelhantes apenas dentro de uma determinada categoria.

  
O Qdrant é amplamente utilizado em aplicações de IA, como busca semântica, recomendação de conteúdo, chatbots com RAG (Retrieval-Augmented Generation), análise de similaridade e detecção de anomalias. Ele se integra facilmente com modelos de linguagem e ferramentas de embeddings, como os fornecidos pela OpenAI, Cohere, Sentence Transformers, entre outros.
</div>

---
#### O papel do Qdrant no sistema

<div align="justify">

O Qdrant é uma parte central do projeto, porque é ele que guarda e organiza as informações retiradas dos PDFs da UnB. Ele funciona como uma espécie de “memória” do sistema, permitindo que o chatbot encontre as respostas certas nos documentos.

A arquitetura usada é o modelo RAG (Retrieval-Augmented Generation). Nesse tipo de sistema, o Qdrant cuida da parte de busca das informações, enquanto o modelo de linguagem (neste caso, o Gemini) é responsável por gerar a resposta final. Dá para pensar no Gemini como alguém que sabe conversar e explicar as coisas, mas que não tem os documentos guardados com ele. Já o Qdrant é como uma biblioteca organizada, onde o sistema vai procurar os trechos que contêm a informação pedida pelo usuário.

O diferencial do Qdrant é que ele não procura por palavras exatas, como um banco de dados comum. Ele usa vetores que representam o sentido das frases. Isso significa que se um usuário perguntar "Como eu faço para falar com a reitoria?", o sistema pode localizar um documento que diga "Os canais de atendimento do gabinete do reitor são o e-mail X e o telefone Y", mesmo que as palavras exatas não sejam as mesmas, pois ele entende que "falar com" é semanticamente similar a "canais de atendimento".

No fim das contas, o Qdrant é o que faz a ligação entre a pergunta e o conhecimento real que está nos PDFs. Ele localiza os trechos mais relevantes e envia para o Gemini, que então monta uma resposta completa e coerente.
</div>

---

#### Embeddings: O Que São?

<div align="justify">

&emsp;&emsp;
Os embeddings são representações numéricas de dados — como textos, imagens, áudios ou vídeos — em um espaço vetorial. Em termos simples, um embedding transforma uma informação complexa (por exemplo, uma frase) em um vetor de números reais, que captura o significado e as relações semânticas entre os elementos.
  
Isso é alcançado através de modelos de Machine Learning, como BERT ou CLIP, que foram treinados com vastos conjuntos de dados para entender essas relações. Ao receber uma entrada, como uma frase, o modelo a processa e converte em um vetor composto por centenas de números. O resultado fundamental é que dados com significados semelhantes geram vetores numericamente próximos em um espaço multidimensional. 
</div>

---

#### Como Identificar Dados Próximos?

<div align="justify">

&emsp;&emsp;
A identificação de dados próximos é feita comparando vetores, que são representações numéricas do texto. Cada documento, frase ou trecho é transformado em um vetor que mostra o significado daquele conteúdo. Isso é feito por modelos chamados embeddings, que convertem o texto em números para que o sistema consiga medir o quanto dois conteúdos são parecidos.
</div>

---

#### Convertendo PDF em Vetor

<div align="justify">

&emsp;&emsp;
A conversão de arquivos PDF em vetores é uma etapa essencial no processo de indexação semântica. Primeiramente, o conteúdo textual é extraído do documento, removendo metadados, elementos gráficos e formatações desnecessárias. Em seguida, o texto é segmentado em blocos menores, como parágrafos ou frases, para otimizar o desempenho na recuperação de informações.

&emsp;&emsp;
Esses blocos são enviados a um modelo de embeddings, que cria um vetor numérico que representa o significado de cada trecho. Esses vetores são armazenados em um banco de dados vetorial (como o Qdrant), permitindo que o sistema faça buscas semânticas rápidas e precisas, com base na proximidade entre os vetores, e não apenas em correspondências exatas de palavras.
</div>

---

#### Criando Prompts com Dados de Vetores

<div align="justify">

&emsp;&emsp;
Após a transformação dos textos em vetores, o sistema utiliza mecanismos de busca semântica para encontrar os documentos mais relevantes a partir de uma consulta do usuário. Essa etapa é conhecida como <strong>retrieval</strong>, e seu resultado consiste nos vetores mais similares à pergunta feita.

&emsp;&emsp;
Em seguida, os textos originais correspondentes a esses vetores são reunidos e integrados em um prompt contextual, que é enviado ao modelo de linguagem. Esse prompt combina a pergunta do usuário com os dados recuperados, permitindo que o modelo forneça uma resposta mais precisa e fundamentada nas informações encontradas.
</div>

Por exemplo:

````txt
Você é um assistente virtual especializado em fornecer informações acadêmicas sobre a Universidade de Brasília (UnB). Utilize os documentos oficiais da UnB para responder às perguntas dos usuários de forma clara e objetiva.
Pergunta do Usuário: "Quais são os requisitos para me inscrever em um curso de pós-graduação na UnB?"
Documentos Relevantes Recuperados:
1. "Para se inscrever em um curso de pós-graduação na UnB....
2. "Os requisitos incluem ter um diploma de graduação reconhecido..."
3. "Além disso, é necessário apresentar um projeto de pesquisa..."
````

Sendo assim, o fluxo de dados pode ser resumido na seguinte sequência:
1. O usuário faz uma pergunta.
2. O sistema converte a pergunta em um vetor.
3. O sistema busca no banco de dados os vetores mais próximos.
4. O sistema recupera os textos originais associados a esses vetores.
5. O sistema cria um prompt que inclui a pergunta do usuário e os textos recuperados.
6. O prompt é enviado ao modelo de linguagem para gerar uma resposta.

---

<center>

## Histórico de Versão

</center>

<div style="margin: 0 auto; width: fit-content;">

| Data       | Versão | Descrição            | Autores                                                   |
|------------|--------|----------------------|-----------------------------------------------------------|
| 06/10/2025 | `1.0`  | Criação do documento | [Pablo Serra](https://github.com/Pabloserrapxx), [João Ginuino](https://github.com/i-JSS) |

</div>