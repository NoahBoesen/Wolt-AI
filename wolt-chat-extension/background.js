// Create context menu when extension is installed
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "clearChat",
        title: "Clear Chat History",
        contexts: ["action"]  // "action" means the extension icon
    });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "clearChat") {
        // Clear localStorage
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {action: "clearChat"});
        });
    }
});

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "clearChat") {
        // Get the iframe
        const iframe = document.getElementById('chat-iframe');
        if (iframe) {
            // Clear the iframe's localStorage and reload it
            iframe.contentWindow.postMessage({ action: 'clearChat' }, '*');
            
            // Force reload the iframe
            iframe.src = iframe.src + '?clear=' + new Date().getTime();
        }
    }
});
