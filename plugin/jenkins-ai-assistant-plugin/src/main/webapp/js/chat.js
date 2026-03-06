/**
 * Jenkins AI Assistant — Chat Frontend Script
 *
 * Handles user input, sends requests to the Jenkins plugin proxy,
 * and renders chat messages.
 */
(function () {
    'use strict';

    var messagesContainer = document.getElementById('ai-chat-messages');
    var inputField = document.getElementById('ai-chat-input');
    var sendButton = document.getElementById('ai-chat-send');
    var isLoading = false;

    // Crumb for Jenkins CSRF protection
    var crumbField = document.querySelector('[name=".crumb"]');
    var crumbValue = crumbField ? crumbField.value : '';
    var crumbHeader = 'Jenkins-Crumb';

    // Try to get crumb from meta tag
    var crumbMeta = document.querySelector('meta[name="crumb.value"]');
    if (crumbMeta) {
        crumbValue = crumbMeta.getAttribute('content') || '';
    }
    var crumbFieldMeta = document.querySelector('meta[name="crumb.fieldName"]');
    if (crumbFieldMeta) {
        crumbHeader = crumbFieldMeta.getAttribute('content') || 'Jenkins-Crumb';
    }

    function addMessage(role, content) {
        // Remove welcome message if present
        var welcome = messagesContainer.querySelector('.welcome-message');
        if (welcome) welcome.remove();

        var bubble = document.createElement('div');
        bubble.className = 'chat-bubble ' + role;

        var label = document.createElement('div');
        label.className = 'chat-label';
        label.textContent = role === 'user' ? '👤 You' : '🤖 Jenkins AI';

        var text = document.createElement('div');
        text.textContent = content;

        bubble.appendChild(label);
        bubble.appendChild(text);
        messagesContainer.appendChild(bubble);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function showTyping() {
        var bubble = document.createElement('div');
        bubble.className = 'chat-bubble assistant';
        bubble.id = 'typing-indicator';

        var label = document.createElement('div');
        label.className = 'chat-label';
        label.textContent = '🤖 Jenkins AI';

        var dots = document.createElement('div');
        dots.className = 'typing-dots';
        dots.innerHTML = '<span></span><span></span><span></span>';

        bubble.appendChild(label);
        bubble.appendChild(dots);
        messagesContainer.appendChild(bubble);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function hideTyping() {
        var typing = document.getElementById('typing-indicator');
        if (typing) typing.remove();
    }

    function sendMessage() {
        var question = inputField.value.trim();
        if (!question || isLoading) return;

        addMessage('user', question);
        inputField.value = '';
        inputField.style.height = 'auto';

        isLoading = true;
        sendButton.disabled = true;
        showTyping();

        var rootURL = document.head.querySelector('[name="rootURL"]');
        var baseUrl = rootURL ? rootURL.getAttribute('content') : '';
        var url = baseUrl + '/ai-assistant/ask';

        var xhr = new XMLHttpRequest();
        xhr.open('POST', url, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        if (crumbValue) {
            xhr.setRequestHeader(crumbHeader, crumbValue);
        }

        xhr.onload = function () {
            hideTyping();
            isLoading = false;
            sendButton.disabled = false;

            try {
                var data = JSON.parse(xhr.responseText);
                addMessage('assistant', data.answer || 'No response received.');
            } catch (e) {
                addMessage('assistant', 'Error parsing response.');
            }
        };

        xhr.onerror = function () {
            hideTyping();
            isLoading = false;
            sendButton.disabled = false;
            addMessage('assistant', 'Network error. Is the AI backend running?');
        };

        xhr.send(JSON.stringify({ question: question }));
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);

    inputField.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    inputField.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
})();
