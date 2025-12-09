document.addEventListener("DOMContentLoaded", () => {
    const chatContainer = document.getElementById("chat-container");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");

    async function handleSend() {
        const pergunta = userInput.value.trim();

        if (pergunta === "") {
            return;
        }

        displayMessage(pergunta, 'user');

        userInput.value = "";

            try {
                displayTypingIndicator();

                const isProduction = window.APP_ENV.IS_PROD === 'true';

                const API_BASE = isProduction ? "/api" : "http://localhost:55555";
                const url = `${API_BASE}/response?pergunta=` + encodeURIComponent(pergunta);
                const resposta = await fetch(url);
            
            if (!resposta.ok) {
                throw new Error(`Erro na rede: ${resposta.statusText}`);
            }

            const dados = await resposta.json();
            
            removeTypingIndicator();

            displayMessage(dados.resposta, 'ai');

        } catch (erro) {
            console.error("Erro ao buscar resposta:", erro);
            removeTypingIndicator();
            displayMessage("Desculpe, ocorreu um erro ao tentar obter a resposta.", 'ai');
        }
    }

    function displayMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        messageElement.innerText = text;
        
        chatContainer.appendChild(messageElement);

        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function displayTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.id = 'typing-indicator';
        typingElement.classList.add('message', 'ai-message');
        typingElement.innerText = 'Digitando...';
        
        chatContainer.appendChild(typingElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            chatContainer.removeChild(indicator);
        }
    }

    sendButton.addEventListener("click", handleSend);

    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            handleSend();
        }
    });
});