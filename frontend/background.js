// chrome-extension/background.js

const FLASK_BACKEND_URL = "http://127.0.0.1:5000/ask-youtube";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'askYoutube') {
        const { youtubeUrl, query } = message;
        console.log('Background script received askYoutube:', youtubeUrl, query);

        fetch(FLASK_BACKEND_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                youtube_url: youtubeUrl,
                query: query
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }).catch(() => {
                    throw new Error(`HTTP error! status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Response from Flask backend:', data);
            if (data.answer) {
                chrome.runtime.sendMessage({ action: 'displayAnswer', answer: data.answer });
            } else if (data.error) {
                chrome.runtime.sendMessage({ action: 'displayError', error: data.error });
            } else {
                chrome.runtime.sendMessage({ action: 'displayError', error: 'Unexpected response format from backend.' });
            }
        })
        .catch(error => {
            console.error('Error in background script (API call):', error);
            chrome.runtime.sendMessage({ action: 'displayError', error: `Failed to connect to backend or process request: ${error.message}` });
        });

        return true;
    } else if (message.action === 'popupOpened' || message.action === 'getCurrentYouTubeUrl') {
        // Find the active tab
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0] && tabs[0].url && tabs[0].url.includes('https://www.youtube.com/watch?v=maFV-fZA6To&pp=0gcJCdgAo7VqN5tD9')) {
                // Send a message to the content script in the active tab
                chrome.tabs.sendMessage(tabs[0].id, { action: 'getYouTubeUrlFromPage' }, (response) => {
                    if (chrome.runtime.lastError) {
                        // Handle error if content script is not injected or fails
                        console.error("Error sending message to content script:", chrome.runtime.lastError.message);
                        chrome.runtime.sendMessage({ action: 'displayError', error: 'Could not get URL. Ensure you are on a YouTube video page and reload the tab.' });
                        return;
                    }
                    if (response && response.url) {
                        chrome.runtime.sendMessage({ action: 'setCurrentYouTubeUrl', url: response.url });
                    } else if (response && response.error) {
                        chrome.runtime.sendMessage({ action: 'displayError', error: response.error });
                    } else {
                        chrome.runtime.sendMessage({ action: 'displayError', error: 'Not on a YouTube video page or URL not found.' });
                    }
                });
            } else {
                chrome.runtime.sendMessage({ action: 'displayError', error: 'Not on a YouTube video page.' });
            }
        });
        return true;
    }
});

// No need for getYouTubeVideoUrlFunction here if content.js handles it.