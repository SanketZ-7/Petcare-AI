const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const typingIndicator = document.getElementById('typing-indicator');

// Auto-scroll to bottom
function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Enable/Disable send button based on input
userInput.addEventListener('input', () => {
    sendBtn.disabled = !userInput.value.trim();
});

// Add a message to the chat
function addMessage(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    
    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar');
    
    if (sender === 'bot') {
        avatarDiv.innerHTML = '<i class="fa-solid fa-robot"></i>';
    } else {
        avatarDiv.innerHTML = '<i class="fa-solid fa-user"></i>';
    }
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.classList.add('bubble');
    
    if (sender === 'bot') {
        // Parse Markdown for bot messages
        bubbleDiv.innerHTML = marked.parse(content);
    } else {
        bubbleDiv.textContent = content;
    }
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(bubbleDiv);
    
    chatBox.appendChild(messageDiv);
    scrollToBottom();
}

// Handle form submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = userInput.value.trim();
    if (!question) return;

    // Add User Message
    addMessage(question, 'user');
    userInput.value = '';
    sendBtn.disabled = true;

    // Show Typing Indicator
    typingIndicator.classList.add('active');
    scrollToBottom();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question }),
        });

        const data = await response.json();
        
        // Hide Typing Indicator
        typingIndicator.classList.remove('active');

        if (response.ok) {
            addMessage(data.answer, 'bot');
        } else {
            addMessage("Sorry, I encountered an error. Please try again.", 'bot');
            console.error('Error:', data);
        }

    } catch (error) {
        typingIndicator.classList.remove('active');
        addMessage("Sorry, check your internet connection.", 'bot');
        console.error('Fetch error:', error);
    }
});
