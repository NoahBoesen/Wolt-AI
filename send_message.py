import os
from slack_sdk import WebClient

def send_order_message(restaurantName, order, notes, phone_number, channelName="#wolt-orders"):
    # Getting the token
    client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))

    response = client.chat_postMessage(
        channel=channelName,
        text='Ny ordre modtaget! 🍽️',
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Ny ordre modtaget!* 🍽️\n\nKære {restaurantName}\nI har lige modtaget en Bestilling fra Wolt igennem Wolt AI.\n\nBestilte retter: {order}\n\nKundens telefonnummer: {phone_number}\n\nBrugerens noter: {notes if notes else 'Kunden tilføjede ingen ekstra noter'}\n\nAccepter ordre?"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Accepter"
                        },
                        "style": "primary",
                        "value": "approve"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Afvis"
                        },
                        "style": "danger",
                        "value": "reject"
                    }
                ]
            }
        ]
    )
    
    return response
