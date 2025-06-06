document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userMessage');
    const chatHistory = document.getElementById('chatHistory');
    const useRagCheckbox = document.getElementById('useRag');
    
    console.log('DOM loaded for chatbot.js');
    console.log('Chat form found:', chatForm ? 'Yes' : 'No');
    console.log('Chat history found:', chatHistory ? 'Yes' : 'No');
    console.log('User input found:', userInput ? 'Yes' : 'No');
    console.log('Use RAG checkbox found:', useRagCheckbox ? 'Yes' : 'No');
    
    // Initialize chat if the form exists
    if (chatForm) {
        console.log('Chat form found and event listener attached');
        
        chatForm.addEventListener('submit', function(e) {
            // Make sure to prevent default at the beginning
            e.preventDefault();
            
            // Add this console log to verify the handler is being called
            console.log('Chat form submitted');
            
            const message = userInput.value.trim();
            if (!message) {
                console.log('Empty message, not submitting');
                return;
            }
            
            console.log('Message to send:', message);
            
            // Add user message to chat
            addMessageToChat('user', message);
            
            // Clear input
            userInput.value = '';
            
            // Show loading indicator
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'chat-message assistant-message';
            loadingDiv.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"></div> Thinking...';
            loadingDiv.id = 'loading-message';
            chatHistory.appendChild(loadingDiv);
            
            // Get response from server
            const useRag = useRagCheckbox ? useRagCheckbox.checked : true;
            console.log('Sending request to /chat with useRag:', useRag);
            
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    use_rag: useRag
                })
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                // Remove loading indicator
                const loadingMessage = document.getElementById('loading-message');
                if (loadingMessage) {
                    loadingMessage.remove();
                }
                
                // Add assistant message to chat
                if (data.error) {
                    addMessageToChat('assistant', 'Error: ' + data.error);
                } else {
                    addMessageToChat('assistant', data.response);
                }
            })
            .catch(error => {
                // Remove loading indicator
                const loadingMessage = document.getElementById('loading-message');
                if (loadingMessage) {
                    loadingMessage.remove();
                }
                
                console.error('Error:', error);
                addMessageToChat('assistant', 'Sorry, there was an error processing your request.');
            });
        });
    } else {
        console.error('Chat form not found');
    }
    
    // Function to add a message to the chat history
    function addMessageToChat(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}-message`;
        
        let messageContent = '';
        if (role === 'user') {
            messageContent = `<strong>You:</strong> ${content}`;
        } else {
            // Process markdown in assistant messages
            messageContent = `<strong>AI Music Teacher:</strong> ${content}`;
        }
        
        messageDiv.innerHTML = messageContent;
        chatHistory.appendChild(messageDiv);
        
        // Scroll to bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});