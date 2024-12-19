import os
import re
import json
import anthropic
from slack_sdk import WebClient
from send_message import send_order_message
import send_message


# Load API keys from environment variables
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')

# Initialize the clients
anthropic_client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
slack_client = WebClient(token=SLACK_BOT_TOKEN)

def extract_order_from_response(response_text):
    """
    Detect if the AI response contains an order confirmation 
    and extract the order details.
    """
    try:
        # Look for JSON-like content in the response
        match = re.search(r'\{.*?\}', response_text, re.DOTALL)
        if match:
            order_details = json.loads(match.group(0))
            if 'order_confirmation' in order_details:
                return order_details
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from AI response: {e}")
    return None


def parse_json_response(response_text):
    """
    Attempts to parse a string as JSON and returns the parsed object and a boolean indicating success
    """
    try:
        # Remove any leading/trailing whitespace and extra newline characters
        cleaned_text = response_text.strip().replace('\n', '').replace('\r', '')
        
        # Check if the text starts and ends with curly braces (basic JSON object check)
        if cleaned_text.startswith('{') and cleaned_text.endswith('}'):
            parsed_json = json.loads(cleaned_text)
            return parsed_json, True
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
    return response_text, False


def chat_with_ai(userInput=None, conversation_history=None, prompt=None):
    if userInput is None or prompt is None:
        # Return a plain text response for initial message
        return {
            "response": "Hej!<br> jeg er wolt AI, til at starte med skal jeg høre, hvor vil du bestille mad fra?",
        }
    
    # Initialize conversation history if None
    if conversation_history is None:
        conversation_history = []
    
    # Add user input to conversation history
    conversation_history.append({"role": "user", "content": userInput})
    
    # Convert conversation history to string format
    history_string = ""
    for message in conversation_history:
        role = "User" if message["role"] == "user" else "AI"
        history_string += f"{role}: {message['content']}\n"

    try:
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[
                {"role": "user", "content": prompt}
            ],
            system="You are a helpful AI assistant.",
            temperature=1,
            max_tokens=1000
        )
        ai_response = response.content[0].text
        
        # Add AI response to conversation history
        conversation_history.append({"role": "assistant", "content": ai_response})
        
        ai_response, isJson = parse_json_response(ai_response)

        
        if not isJson:
            #Just a normal response - Nothing else happening
            return {"response": ai_response, "history": conversation_history}
        else:
            #Now we handle if the response is in json format and give it the different categories
            if ai_response.get("navigation") and ai_response.get("message"):
                # Check for prompt transitions based on response content
                currentPrompt = "category"

                # Add the new prompt to the response if it changed
                return {
                    "response": ai_response.get("message"),
                    "history": conversation_history,
                    "redirectUrl": ai_response.get("navigation"),
                    "currentPrompt": currentPrompt
                }
            elif ai_response.get("restaurant"):
                # Send the message to Slack
                send_order_message(
                    restaurantName=ai_response.get("restaurant", ""),
                    order=ai_response.get("order_details", ""),
                    notes=ai_response.get("extra_notes", "")
                )
                return {
                    "response": ai_response.get("message", "Ordren er bestilt, tak for din bestilling!"),
                    "history": conversation_history
                }
            else:
                return {
                    "response": ai_response.get("message"),
                    "history": conversation_history
                }

    except Exception as e:
        return {"response": f"Error communicating with AI: {e}", "history": conversation_history}
