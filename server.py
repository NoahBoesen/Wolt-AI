from fastapi import FastAPI, Request
import json
from fastapi.middleware.cors import CORSMiddleware
import anthropic
import os
from send_message import send_order_message
from fastapi.responses import HTMLResponse
from controller import *
from functions import *
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()  # Add this at the top of your file



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
anthropic_client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

# Initialize Twilio client
twilio_client = Client(account_sid, auth_token)


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    # Get the message and history from the request
    userInput = data['message']
    conversation_history = data.get('history', [])  # Get history or empty list if not provided
    current_url = data.get('currentUrl', '')  # Get current URL from request
    current_prompt = data.get('currentPrompt', '')  # Default to 'food' if not provided
    html = data.get('html', '')  # Get the Restaurant Grid HTML
    menuCardHtml = data.get('menuCardHtml', '')  # Get the Menu Card HTML (correct key name)

    restaurants_formatted_text = None
    menuCard_formatted_text = None

    #Html sorting
    if html:
        restaurants_formatted_text = htmlSorter(html)
    
    if menuCardHtml:
        menuCard_formatted_text = menuCardSorter(menuCardHtml)
        # Ensure menuCard_formatted_text is a string and add prefix
        if menuCard_formatted_text:
            menuCard_formatted_text = "Du har adgang til restaurantens menukort og alt relevant sideindhold, når brugeren kigger på restauranter eller madkategorier. Denne adgang giver dig mulighed for at finde og præsentere retter samt madmuligheder fra de tilgængelige restauranters menukort. Du skal aktivt og proaktivt bruge denne viden til at hjælpe brugeren med at lave deres ordre. Det betyder, at du skal foreslå relevante retter og måltider, som brugeren kunne tilføje til deres bestilling, baseret på brugerens kontekst og præferencer. Når du nævner eller foreslår restauranter eller retter, må du kun henvise til dem, der fremgår af menukortet. Hvis brugeren nævner en restaurant eller ret, der ikke findes på listen, skal du tydeligt informere dem om, at det ikke er en tilgængelig mulighed. Her er restaurantens menukort:" + str(menuCard_formatted_text)

    
    prompt = prompts(userInput, conversation_history, current_prompt, restaurants_formatted_text, menuCard_formatted_text)
    
    # Call chat_with_ai with both message and history
    result = chat_with_ai(userInput, conversation_history, prompt)

    response_obj = {
        "response": result["response"],
        "history": result["history"]
    }
    # Add new prompt to response if it changed
    if "currentUrl" in result:
        response_obj["currentUrl"] = result["currentUrl"]
    if "currentPrompt" in result:
        response_obj["currentPrompt"] = result["currentPrompt"]

    if "redirectUrl" in result and result["redirectUrl"]:
        response_obj["redirectUrl"] = result["redirectUrl"]

    return response_obj



@app.post("/slack/interactivity")
async def handle_interaction(request: Request):
    payload = await request.form()
    print("Payload: ", payload)
    action = json.loads(payload.get('payload'))
    
    # Extract the original message text from blocks instead of message text
    original_message = action['message']['blocks'][0]['text']['text']
    # Initialize phone_number with a default value
    phone_number = None
    
    # Extract phone number using string manipulation
    # Looking for the line that contains "Kundens telefonnummer: "
    restaurant_name = None
    for line in original_message.split('\n'):
        if "Kære" in line:
            restaurant_name = line.split("Kære")[1].strip()
        if "Kundens telefonnummer:" in line:
            phone_number = line.split("Kundens telefonnummer:")[1].strip()
            #Send a message to the phone number
            break
    # Check if phone number was found
    if phone_number is None:
        print("Error: Could not find phone number in message")


    # Send message
    def send_sms(from_number, to_number, message):
        try:
            message = twilio_client.messages.create(
                from_=from_number,
                to=to_number,
                body=message,
                shorten_urls=True
            )
            return {"status": "success", "message_sid": message.sid}
        except Exception as e:
            return {"status": "error", "message": str(e)}

                
    button_clicked = action['actions'][0]['value']
    if button_clicked == 'approve':
        print("Trykket på ✅")
        if restaurant_name:
            sms = f"Din ordre fra {restaurant_name} blev godkendt :)"
        else:
            sms = "Din ordre blev godkendt :)"
        send_sms("+16203372653", phone_number, sms)
        print(f"Approved order for customer with phone: {phone_number}")
    elif button_clicked == 'reject':
        print("Trykket på ❌")
        if restaurant_name:
            sms = f"Din ordre fra {restaurant_name} blev ikke godkendt :("
        else:
            sms = "Din ordre blev ikke godkendt :("
        send_sms("+16203372653", phone_number, sms)
        print(f"Rejected order for customer with phone: {phone_number}")

    return {"text": "Thanks for your response!"}

@app.get("/woltAI", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Chat Window</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; }
                .chat-container { height: 100vh; display: flex; flex-direction: column; }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div style="box-shadow: 0 0 #0000, 0 0 #0000, 0 1px 2px 0 rgb(0 0 0 / 0.05);"
                    class="bg-white p-6 rounded-lg border border-[#e5e7eb] w-[440px] h-[634px] flex flex-col">

                    <!-- Fixed Header -->
                    <div class="flex-none">
                        <div class="flex flex-col space-y-1.5 pb-6">
                            <h2 class="font-semibold text-lg tracking-tight">Wolt AI</h2>
                            <p class="text-sm text-[#6b7280] leading-3">fremtidens mad levering</p>
                        </div>
                    </div>

                    <!-- Scrollable Messages Container -->
                    <div id="messages" class="flex-1 overflow-y-auto pr-4" style="min-width: 100%;">
                        <!-- Messages will be added here -->
                    </div>

                    <!-- Fixed Input Box -->
                    <div class="flex-none pt-6">
                        <form id="chat-form" class="flex items-center justify-center w-full space-x-2">
                            <input
                                id="message-input"
                                class="flex h-10 w-full rounded-md border border-[#e5e7eb] px-3 py-2 text-sm placeholder-[#6b7280] focus:outline-none focus:ring-2 focus:ring-[#9ca3af] disabled:cursor-not-allowed disabled:opacity-50 text-[#030712] focus-visible:ring-offset-2"
                                placeholder="Skriv din besked"
                                autocomplete="off">
                            <button type="submit"
                                class="inline-flex items-center justify-center rounded-md text-sm font-medium text-[#f9fafb] disabled:pointer-events-none disabled:opacity-50 bg-black hover:bg-[#111827E6] h-10 px-4 py-2">
                                Send
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <script>
                const messagesContainer = document.getElementById('messages');
                const chatForm = document.getElementById('chat-form');
                const messageInput = document.getElementById('message-input');
                
                // Initialize conversation history from localStorage
                let conversationHistory = JSON.parse(localStorage.getItem('chatHistory') || '[]');

                // Add this after the conversation history initialization
                let currentPrompt = localStorage.getItem('currentPrompt') || 'location';
                
                let extractedRestaurantGridHTML = '';
                let extractedMenuCardHTML = '';

                window.addEventListener('message', (event) => {
                    if (event.data.action === 'SEND_HTML') {
                        extractedRestaurantGridHTML = event.data.html || ''; 
                        extractedMenuCardHTML = event.data.menuCardHtml || ''; 

                        console.log('Restaurant Grid HTML length:', extractedRestaurantGridHTML.length);
                        console.log('Menu Card HTML length:', extractedMenuCardHTML.length);
                    }
                });

                // Function to load chat history
                function loadChatHistory() {
                    messagesContainer.innerHTML = ''; // Clear existing messages
                    
                    // If no history, show initial AI message
                    if (conversationHistory.length === 0) {
                        const initialMessage = 'Hej!👋<br>Jeg er en chatbot udviklet af Wolt, til at hjælpe dig med at bestille mad. Til at starte med skal jeg høre, hvor vil du bestille mad fra?';
                        addMessage('AI', initialMessage);
                        // Add to conversation history
                        conversationHistory.push({
                            role: 'assistant',
                            content: initialMessage
                        });
                        localStorage.setItem('chatHistory', JSON.stringify(conversationHistory));
                    } else {
                        // Load all messages from history
                        conversationHistory.forEach(msg => {
                            addMessage(msg.role === 'user' ? 'Dig' : 'AI', msg.content);
                        });
                    }
                }

                // Load chat history when page loads
                loadChatHistory();

                chatForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const message = messageInput.value.trim();
                    if (!message) return;

                    addMessage('Dig', message);
                    messageInput.value = '';

                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 
                            message,
                            history: conversationHistory,
                            currentPrompt: currentPrompt,
                            html: extractedRestaurantGridHTML,  // Send restaurant grid as 'html'
                            menuCardHtml: extractedMenuCardHTML  // Send menu card as 'menuCardHtml'
                        })
                    });

                    const data = await response.json();
                    console.log('Server response:', data);
                    addMessage('AI', data.response);
                    
                    // Send redirect URL to parent window using postMessage
                    if (data.redirectUrl) {
                        window.parent.postMessage({
                            type: 'NAVIGATE',
                            url: data.redirectUrl
                        }, '*');
                    }
                    
                    // Update conversation history and save to localStorage
                    conversationHistory = data.history;
                    localStorage.setItem('chatHistory', JSON.stringify(conversationHistory));

                    // Add after the data response handling
                    if (data.currentPrompt) {
                        currentPrompt = data.currentPrompt;
                    } 
                    localStorage.setItem('currentPrompt', currentPrompt);

                });

                function addMessage(role, content) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'flex gap-3 my-4 text-gray-600 text-sm flex-1';
                    
                    const icon = role === 'AI' 
                        ? '<svg stroke="none" fill="black" stroke-width="1.5" viewBox="0 0 24 24" aria-hidden="true" height="20" width="20" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"></path></svg>'
                        : '<svg stroke="none" fill="black" stroke-width="0" viewBox="0 0 16 16" height="20" width="20" xmlns="http://www.w3.org/2000/svg"><path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0Zm4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4Zm-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10Z"></path></svg>';

                    messageDiv.innerHTML = `
                        <span class="relative flex shrink-0 overflow-hidden rounded-full w-8 h-8">
                            <div class="rounded-full bg-gray-100 border p-1">${icon}</div>
                        </span>
                        <p class="leading-relaxed"><span class="block font-bold text-gray-700">${role}</span>${content}</p>
                    `;
                    
                    messagesContainer.appendChild(messageDiv);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }

                function clearChat() {
                    // Clear localStorage
                    localStorage.removeItem('chatHistory');
                    localStorage.removeItem('currentPrompt');
                    // Reset conversation history
                    conversationHistory = [];
                    // Clear messages container
                    messagesContainer.innerHTML = '';
                    // Add initial AI message
                    addMessage('AI', 'Hej!👋<br>Jeg er en chatbot udviklet af Wolt, til at hjælpe dig med at bestille mad. Til at starte med skal jeg høre, hvor vil du bestille mad fra?');
                }

                // Listen for messages from the parent window
                window.addEventListener('message', function(event) {
                    if (event.data && event.data.action === 'clearChat') {
                        clearChat();
                    }
                });

            </script>
        </body>
    </html>
    """

