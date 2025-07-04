document.addEventListener('DOMContentLoaded', () => {
    const youtubeUrlInput = document.getElementById('youtubeUrl');
    const queryInput = document.getElementById('queryInput');
    const askButton = document.getElementById('askButton');
    const getCurrentUrlButton = document.getElementById('getCurrentUrlButton');
    const answerOutput = document.getElementById('answerOutput');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorIndicator = document.getElementById('errorIndicator');
    const errorMessage = errorIndicator.querySelector('.error-message');

    // Function to display messages/status in the UI
    function displayMessage(type, content) {
        loadingIndicator.classList.add('hidden');
        errorIndicator.classList.add('hidden');
        answerOutput.innerHTML = ''; // Clear previous output

        if (type === 'loading') {
            loadingIndicator.classList.remove('hidden');
            answerOutput.innerHTML = `<p>${content}</p>`;
        } else if (type === 'error') {
            errorIndicator.classList.remove('hidden');
            errorMessage.textContent = content;
        } else { // type === 'answer'
            answerOutput.textContent = content;
        }
    }

    // Event listener for "Ask About Video" button
    askButton.addEventListener('click', () => {
        const youtubeUrl = youtubeUrlInput.value.trim();
        const query = queryInput.value.trim();

        if (!youtubeUrl || !query) {
            displayMessage('error', 'Please provide both a YouTube URL and a question.');
            return;
        }

        displayMessage('loading', 'Processing your request, please wait...');

        // Send message to background script to initiate the API call
        chrome.runtime.sendMessage({
            action: 'askYoutube',
            youtubeUrl: youtubeUrl,
            query: query
        });
    });

    // Event listener for "Get Current URL" button
    getCurrentUrlButton.addEventListener('click', () => {
        displayMessage('loading', 'Getting current YouTube URL...');
        chrome.runtime.sendMessage({ action: 'getCurrentYouTubeUrl' });
    });

    // Listen for messages from the background script
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.action === 'displayAnswer') {
            displayMessage('answer', message.answer); // Display the answer
        } else if (message.action === 'displayError') {
            displayMessage('error', message.error); // Display an error message
        } else if (message.action === 'setCurrentYouTubeUrl') {
            youtubeUrlInput.value = message.url; // Auto-fill the URL input
            displayMessage('answer', 'YouTube URL auto-filled.');
        }
    });

    // Request current URL when popup opens, if on a YouTube page
    chrome.runtime.sendMessage({ action: 'popupOpened' });
});