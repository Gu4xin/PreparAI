document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("chatInput");
    const sendBtn = document.getElementById("sendBtn");
    const messagesContainer = document.getElementById("chatMessages");

    // Função para adicionar mensagens na tela
    function addMessage(text, sender = "user") {
        const msg = document.createElement("div");
        msg.classList.add("message", sender);
        msg.textContent = text;
        messagesContainer.appendChild(msg);

        // Scroll sempre para o final
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Função para enviar a mensagem ao back-end
    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;

        addMessage(text, "user");
        input.value = "";

        try {
            const response = await fetch("http://localhost:5000/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();

            addMessage(data.reply || "Erro ao processar resposta.", "bot");

        } catch (error) {
            addMessage("Erro ao conectar com o servidor.", "bot");
        }
    }

    // Enviar ao clicar
    sendBtn.addEventListener("click", sendMessage);

    // Enviar ao apertar Enter
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            sendMessage();
        }
    });
});
