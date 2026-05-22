(function () {
    const form = document.getElementById("chatForm");
    const input = document.getElementById("preguntaInput");
    const messages = document.getElementById("chatMessages");
    const enviarBtn = document.getElementById("enviarBtn");

    function addMessage(text, tipo) {
        const div = document.createElement("div");
        div.className = `message ${tipo}`;
        div.innerHTML = `<div class="message-content">${escapeHtml(text)}</div>`;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    function showTyping() {
        const div = document.createElement("div");
        div.className = "message bot";
        div.id = "typingIndicator";
        div.innerHTML = `<div class="message-content"><div class="typing-indicator"><span></span><span></span><span></span></div></div>`;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    }

    function removeTyping() {
        const el = document.getElementById("typingIndicator");
        if (el) el.remove();
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        const pregunta = input.value.trim();
        if (!pregunta) return;

        addMessage(pregunta, "user");
        input.value = "";
        enviarBtn.disabled = true;
        showTyping();

        try {
            const response = await fetch("/chat/enviar/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ pregunta: pregunta }),
            });

            removeTyping();

            if (!response.ok) {
                const errData = await response.json();
                addMessage(errData.error || "Error del servidor", "error");
                return;
            }

            const data = await response.json();
            addMessage(data.respuesta, data.valida ? "bot" : "error");

        } catch (err) {
            removeTyping();
            addMessage("Error de conexión. Intenta de nuevo.", "error");
        } finally {
            enviarBtn.disabled = false;
            input.focus();
        }
    });
})();
