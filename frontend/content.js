// Base URL for your local Flask backend
const FLASK_BACKEND_URL = "http://127.0.0.1:5000/ask-youtube";

// Listen for messages from the popup or content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'askYoutube') {
        const { youtubeUrl, query } = message;
        console.log('Background script received askYoutube:', youtubeUrl, query);

        // Make the HTTP POST request to your local Python Flask server
        fetch(FLASK_BACKEND_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // CORS is handled by Flask-CORS on the backend, but good to set header
            },
            body: JSON.stringify({ // Send data as JSON string
                youtube_url: youtubeUrl,
                query: query
            })
        })
        .then(response => {
            // Check if the HTTP response itself was successful (status 2xx)
            if (!response.ok) {
                // If not OK, try to parse the error message from the JSON response body
                return response.json().then(errorData => {
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }).catch(() => {
                    // Fallback if response body is not valid JSON
                    throw new Error(`HTTP error! status: ${response.status}`);
                });
            }
            // If response is OK, parse the JSON body
            return response.json();
        })
        .then(data => {
            console.log('Response from Flask backend:', data);
            // Flask backend sends JSON like {"answer": "..."} or {"error": "..."}
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
            // Send general error message back to the popup
            chrome.runtime.sendMessage({ action: 'displayError', error: `Failed to connect to backend or process request: ${error.message}` });
        });

        // Return true to indicate that you will send a response asynchronously
        return true;
    } else if (message.action === 'popupOpened' || message.action === 'getCurrentYouTubeUrl') {
        // Handle requests for the current YouTube URL from the active tab
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0] && tabs[0].url && tabs[0].url.includes('https://www.youtube.com/watch?v=maFV-fZA6To&pp=0gcJCdgAo7VqN5tD9')) {
                // Execute content.js to get the video URL from the page
                chrome.scripting.executeScript({
                    target: { tabId: tabs[0].id },
                    function: getYouTubeVideoUrlFunction // Function to inject
                }, (results) => {
                    if (results && results[0] && results[0].result) {
                        chrome.runtime.sendMessage({ action: 'setCurrentYouTubeUrl', url: results[0].result });
                    } else {
                        chrome.runtime.sendMessage({ action: 'displayError', error: 'Not on a YouTube video page or URL not found.' });
                    }
                });
            } else {
                chrome.runtime.sendMessage({ action: 'displayError', error: 'Not on a YouTube video page.' });
            }
        });
        return true; // Asynchronous response
    }
});

// Function to be injected and executed in the content script context
// This function must be self-contained and not rely on global variables from background.js
function getYouTubeVideoUrlFunction() {
    return window.location.href;
}