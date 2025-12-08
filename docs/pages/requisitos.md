### **Introdução**

O presente documento estabelece a fundação para o desenvolvimento do Assistente Virtual sob a ótica do produto e da experiência do usuário. O foco destes requisitos é garantir que a aplicação final seja funcional, intuitiva e confiável para a comunidade acadêmica. Eles descrevem a interação direta com o usuário através da plataforma Telegram, as funcionalidades visíveis, e as características de qualidade globais do sistema, como desempenho, disponibilidade e segurança. Em resumo, este documento define o que o produto faz e quão bem ele deve fazer do ponto de vista de quem o utiliza.

#### **Requisitos Funcionais (RF)**

* **RF01: Conexão com a Plataforma Telegram**: O sistema deve se integrar com a API do Telegram para receber mensagens de usuários e enviar respostas.

* **RF02: Citação de Fontes**: Para cada resposta fornecida, o sistema deve incluir uma referência ou link direto para o(s) documento(s) oficial(is) de onde a informação foi extraída.
* **RF03: Tratamento de Perguntas Fora de Escopo**: Quando uma pergunta não puder ser respondida, o sistema deve retornar uma mensagem clara e amigável informando que não encontrou a resposta.
* **RF04: Coleta de Feedback do Usuário**: O sistema deve apresentar ao usuário uma forma de avaliar a qualidade da resposta, como botões de "gostei" e "não gostei".
* **RF05: Comando de Ajuda e Boas-Vindas**: O sistema deve responder a um comando `/start` ou `/ajuda` com uma mensagem de boas-vindas que explique seu propósito e como utilizá-lo.
* **RF06: Perguntas Frequentes**: O sistema deve forcer perguntas pré-definidas que ocorrem com mais frequência.
* **RF07: Persistência de Histórico**: O usuário deve ter acesso ao histórico de sua conversa com o chatbot na interface do Telegram.
* **RF08: Mensagens de Status do Sistema**: O sistema deve informar ao usuário caso haja instabilidades conhecidas ou manutenções programadas.
* **RF19: Autenticação**: O sistema deve validar o usuário através do número de matrícula.

#### **Requisitos Não Funcionais (RNF)**

* **RNF01: Desempenho (Latência)**: O tempo de resposta para uma pergunta do usuário não deve exceder 5 segundos em 90% das requisições.

* **RNF02: Disponibilidade**: O serviço do chatbot deve estar disponível para os usuários 99,5% do tempo.
* **RNF03: Usabilidade**: A linguagem e a interface do bot devem ser intuitivas, claras e de fácil compreensão para o público-alvo.
* **RNF04: Privacidade**: O sistema deve estar em conformidade com a LGPD.
* **RNF05: Escalabilidade**: A arquitetura deve suportar um aumento de 10x no número de usuários simultâneos sem degradação do desempenho.
* **RNF06: Manutenibilidade**: O processo para adicionar novas fontes de dados ou ajustar comandos do bot deve ser simples e bem documentado.
* **RNF07: Compatibilidade**: O chatbot deve funcionar corretamente nas versões mais recentes dos clientes oficiais do Telegram.
* **RNF08: Acessibilidade**: O texto e a estrutura das respostas devem seguir boas práticas de acessibilidade, sendo compatíveis com leitores de tela.
* **RNF09: Identidade e Tom de Voz**: O chatbot deve manter um tom de voz consistente (prestativo, formal, mas claro) em todas as suas interações.
* **RNF10: Usabilidade**: O retorno da resposta não pode ter mais do que 10 linhas.

---

<center>

## Histórico de Versão

</center>

<div style="margin: 0 auto; width: fit-content;">

| Data       | Versão | Descrição            | Autores                                   |
|------------|--------|----------------------|-------------------------------------------|
| 24/09/2025 | `1.0`  | Criação do documento | [Cássio Reis](https://github.com/csreis72) |
| 07/10/2025 | `1.1`  | Atualização dos requisitos | [Vinicius Santos](https://github.com/ViniciussdeOliveira) |
| 07/10/2025 | `1.1`  | Atualização dos requisitos não funcionais (01 e 10) | [Vinicius Santos](https://github.com/ViniciussdeOliveira) |

</div>

---