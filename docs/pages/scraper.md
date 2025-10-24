## 1. Introdução

Este documento descreve o **webscraper** desenvolvido pela equipe, que atualmente coleta informações acadêmicas e administrativas nos sites da SAA, do DEG e do SEI da Universidade de Brasília (UnB). O scraper tem como objetivo disponibilizar dados estruturados e documentos PDF relacionados a monitorias, editais, resoluções e calendários acadêmicos, bem como outros serviços oferecidos aos alunos. Dessa forma, informações importantes ficam acessíveis para análise, processamento posterior e integração com o chatbot.

## 2. Funcionamento

O webscraper foi desenvolvido em Python, utilizando a biblioteca `BeautifulSoup` para realizar a extração e o processamento das informações contidas nas páginas da web. Atualmente, ele realiza a coleta de dados diretamente dos sites da SAA, DEG e SEI, capturando títulos, descrições, datas e links de documentos relevantes.

- **SAA**: coleta informações sobre serviços acadêmicos, calendários, editais e documentos institucionais.
- **DEG**: realiza filtragem por palavras-chave, como “monitoria”, retornando apenas informações pertinentes.
- **SEI**: coleta documentos relacionados à FCTE (Faculdade de Ciências e Tecnologias em Engenharia), incluindo resoluções e editais.

Sempre que encontra URLs de arquivos PDF, o scraper realiza o download automático para uma pasta local (`pdfs/`) e registra o caminho local correspondente no arquivo JSON, evitando downloads duplicados.

Todos os dados coletados são combinados em um arquivo `unb_data.json`, contendo tanto as informações textuais quanto os caminhos dos PDFs baixados. Durante a execução, todas as etapas são registradas em logs detalhados, garantindo rastreabilidade e permitindo análise de possíveis erros sem interromper o processo geral.

## 3. Conclusão

O webscraper automatiza a coleta e organização das informações acadêmicas da UnB, reunindo dados e documentos oficiais em formato JSON e PDF. Esses dados serão utilizados posteriormente para geração de embeddings e armazenamento no banco de dados vetorial (Qdrant), possibilitando buscas semânticas e integração com o chatbot.

<center>

## Histórico de Versão

</center>

<div style="margin: 0 auto; width: fit-content;">

| Data       | Versão | Descrição                  | Autores                                    |
| ---------- | ------ | -------------------------- | ------------------------------------------ |
| 13/10/2025 | `1.0`  | Criação do documento       | [Cássio Reis](https://github.com/csreis72) |
| 23/10/2025 | `1.1`  | Inclusão do scraper do SEI | [Cássio Reis](https://github.com/csreis72) |

</div>
