## 1. Introdução

Este documento descreve o **webscraper** desenvolvido pela equipe, que atualmente coleta informações acadêmicas e administrativas nos sites da SAA e do DEG da Universidade de Brasília (UnB). O scraper tem como objetivo disponibilizar dados estruturados e documentos PDF relacionados a monitorias, editais, calendários acadêmicos e outros serviços oferecidos aos alunos. Dessa forma, informações importantes ficam acessíveis para análise, processamento posterior e integração com o chatbot.

## 2. Funcionamento

Atualmente, o scraper realiza a coleta de dados diretamente das páginas da SAA e do DEG, capturando títulos, descrições, datas e links de documentos relevantes. No site da SAA, ele coleta informações sobre serviços acadêmicos, calendários, editais e documentos institucionais. No DEG, ele filtra por palavras-chave, como “monitoria”, retornando apenas informações pertinentes. Sempre que encontra URLs de arquivos PDF, o scraper realiza o download para uma pasta local (`pdfs/`) e registra o caminho local correspondente no arquivo JSON, evitando downloads duplicados.

Todos os dados coletados são combinados em um arquivo `unb_data.json`, contendo tanto as informações textuais quanto os caminhos dos PDFs baixados. Durante a execução, todas as etapas são registradas em logs detalhados, garantindo rastreabilidade e permitindo análise de possíveis erros sem interromper o processo geral.

<center>

## Histórico de Versão

</center>

<div style="margin: 0 auto; width: fit-content;">

| Data       | Versão | Descrição            | Autores                                   |
|------------|--------|----------------------|-------------------------------------------|
| 13/10/2025 | `1.0`  | Criação do documento | [Cássio Reis](https://github.com/csreis72) |

</div>