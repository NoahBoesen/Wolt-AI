const NGROK_URL = "https://e955-194-182-243-220.ngrok-free.app";

// Ensure the script runs only once
if (!document.getElementById('wolt-chat-circle')) {
    // Create the chat button
    const chatButton = document.createElement('button');
    chatButton.id = 'wolt-chat-circle';
    chatButton.className = 'fixed bottom-4 right-4 inline-flex items-center justify-center text-sm font-medium border rounded-full bg-black hover:bg-gray-700';
    chatButton.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            class="text-white block border-gray-200 align-middle">
            <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"></path>
        </svg>
    `;
    document.body.appendChild(chatButton);
  
    // Create the chat window
    const chatWindow = document.createElement('div');
    chatWindow.id = 'wolt-chat-window';
    chatWindow.style.display = 'none';
    
    const iframeUrl = NGROK_URL + "/woltAI";
    chatWindow.innerHTML = `
        <iframe 
            id="chat-iframe"
            src="${iframeUrl}" 
            style="width: 440px; height: 634px; border: none; border-radius: 10px;"
        ></iframe>
    `;
    document.body.appendChild(chatWindow);

    // Function to extract HTML from a specific div
    function extractHTMLFromDiv(selector) {
        const targetElement = document.querySelector(selector);
        return targetElement ? targetElement.outerHTML : '';
    }

    // Continuous HTML update function for multiple selectors
    function startContinuousHTMLUpdates(iframe) {
        setInterval(() => {
            let htmlContent = '';
            let menuContent = '';

            try {
                htmlContent = extractHTMLFromDiv('div[data-test-id="VenueVerticalListGrid"]');
            } catch (error) {
                console.error('Error extracting htmlContent:', error);
            }

            try {
                menuContent = extractHTMLFromDiv('div[class*="sfdszan"]');
            } catch (error) {
                console.error('Error extracting menuContent:', error);
            }

            console.log(`Sending both HTMLs: Restaurant Grid Length = ${htmlContent.length}, Menu Card Length = ${menuContent.length}`);

            iframe.contentWindow.postMessage({ 
                action: 'SEND_HTML', 
                html: htmlContent || '',
                menuCardHtml: menuContent || ''
            }, '*');
        }, 500); // Send both at the same time every 500ms
    }

    // Update iframe.onload handler
    const iframe = document.getElementById('chat-iframe');
    iframe.onload = () => {
        startContinuousHTMLUpdates(iframe);
    };
  
    // Toggle chat window visibility
    chatButton.addEventListener('click', () => {
      chatWindow.style.display = chatWindow.style.display === 'none' ? 'block' : 'none';
    });

    // Add message listener for the iframe
    window.addEventListener('message', function(event) {
        console.log("Received message:", event.data);
        if (event.data.type === 'NAVIGATE' && event.data.url) {
            console.log("Got redirect URL:", event.data.url);
            if (window.location.hostname.includes('wolt.com')) {
                const url = new URL(event.data.url);
                const newPath = url.pathname + url.search + url.hash;
                
                window.history.pushState({}, '', newPath);
                
                window.dispatchEvent(new Event('popstate'));
                
                const navigationEvent = new PopStateEvent('popstate', { state: {} });
                window.dispatchEvent(navigationEvent);
            }
        }
    });
}

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "clearChat") {
        const iframe = document.getElementById('chat-iframe');
        if (iframe) {
            iframe.contentWindow.postMessage({ action: 'clearChat' }, '*');
            iframe.src = iframe.src + '?clear=' + new Date().getTime();
        }
    }
});