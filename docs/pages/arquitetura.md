<center>

# Arquitetura do Projeto

</center>

---


<div align="justify">

&emsp;&emsp;
A arquitetura segue o modelo RAG, Retrieval-Augmented Generation, que combina recuperação de informações com geração de texto para fornecer respostas precisas e contextuais. Sendo assim, podemos dividir a aplicação em três componentes principais: o banco de dados vetorial, os modelos de machine learning e a API, conforme ilustrado na Figura 1 desta página.
</div>


<center>

**Figura 1**: Representação arquitetural do sistema.

</center>

<center>
    <img src="assets/arquitetura.png" alt="Arquitetura" style="width:100%; max-width: 800px;"/>
</center>

<center>

**Fonte**: Carvalho, Ginuino (2025).

</center>

---

#### Tecnologias Utilizadas

* **Banco de Dados Vetorial**: Qdrant
* **Modelos de Machine Learning**: Gemini Pro - Google Cloud
* **API**: Telegram Bot API - Python
* **Web Scraper**: BeautifulSoup - Python

---

#### Justificativas

- **Qdrant** — Utilizado para o armazenamento e tratamento de dados em bancos vetoriais, possibilitando consultas semânticas e operações de similaridade entre embeddings.
- **Gemini Pro** — Modelo de linguagem (LLM) disponibilizado gratuitamente para estudantes, oferecendo alto desempenho em tarefas de processamento de linguagem natural e integração simples com outras ferramentas.
- **Telegram Bot API** — Facilita a interação com os usuários por meio de um bot no Telegram, permitindo chamadas simplificadas e desacoplando o sistema de um frontend dedicado.
- **BeautifulSoup (Python)** — Biblioteca utilizada para web scraping e manipulação de páginas HTML. Após a captura do código HTML bruto, o BeautifulSoup possibilita o tratamento dinâmico do conteúdo, facilitando a busca e extração de arquivos (como PDFs).
- **Backend (Python 3.12)** — Escolhido pela fácil integração com o Qdrant, o web scraper e a API do Telegram. A linguagem Python oferece ampla compatibilidade, legibilidade e suporte a bibliotecas voltadas a automação e análise de dados, tornando-a ideal para este projeto.


---

<center>

## Histórico de Versão

</center>

<div style="margin: 0 auto; width: fit-content;">

| Data       | Versão | Descrição            | Autores                                   |
|------------|--------|----------------------|-------------------------------------------|
| 06/10/2025 | `1.0`  | Criação do documento | [João Ginuino](https://github.com/i-JSS) |

</div>
