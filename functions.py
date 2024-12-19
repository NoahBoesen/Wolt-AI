import os
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

current_time = datetime.now(pytz.timezone('Europe/Copenhagen')).strftime("%H:%M")



by_urls = """
"/da/dnk/aabenraa","Aabenraa",
"/da/dnk/aabybro","Aabybro",
"/da/dnk/aalborg","Aalborg",
"/da/dnk/aarhus","Aarhus",
"/da/dnk/alleroed","Allerød",
"/da/dnk/ballerup-herlev","Ballerup-Herlev",
"/da/dnk/birkeroed-farum","Birkerød-Farum",
"/da/dnk/brande","Brande",
"/da/dnk/broenderslev","Brønderslev",
"/da/dnk/esbjerg","Esbjerg",
"/da/dnk/fredensborg","Fredensborg",
"/da/dnk/fredericia-middelfart","Fredericia-Middelfart",
"/da/dnk/frederikshavn","Frederikshavn",
"/da/dnk/frederikssund","Frederikssund",
"/da/dnk/frederiksvaerk","Frederiksværk",
"/da/dnk/grena","Grenå",
"/da/dnk/grasten","Gråsten",
"/da/dnk/haderslev","Haderslev",
"/da/dnk/hedehusene","Hedehusene",
"/da/dnk/helsingoer","Helsingør",
"/da/dnk/herning","Herning",
"/da/dnk/hilleroed","Hillerød",
"/da/dnk/hjoerring","Hjørring",
"/da/dnk/hobro","Hobro",
"/da/dnk/holbaek","Holbæk",
"/da/dnk/holstebro","Holstebro",
"/da/dnk/hornbaek","Hornbæk",
"/da/dnk/horsens","Horsens",
"/da/dnk/hvide-sande","Hvide Sande",
"/da/dnk/hoersholm-rungsted","Hørsholm-Rungsted",
"/da/dnk/ikast","Ikast",
"/da/dnk/kalundborg1","Kalundborg",
"/da/dnk/kolding","Kolding",
"/da/dnk/korsoer","Korsør",
"/da/dnk/copenhagen","København",
"/da/dnk/lyngby-gentofte","Lyngby-Gentofte",
"/da/dnk/maribo","Maribo",
"/da/dnk/nyborg","Nyborg",
"/da/dnk/nykoebing-falster","Nykøbing Falster",
"/da/dnk/nykoebing-mors","Nykøbing Mors",
"/da/dnk/naestved","Næstved",
"/da/dnk/odder","Odder",
"/da/dnk/odense","Odense",
"/da/dnk/ribe","Ribe",
"/da/dnk/ringkoebing","Ringkøbing",
"/da/dnk/ringsted","Ringsted",
"/da/dnk/roskilde","Roskilde",
"/da/dnk/roedby","Rødby",
"/da/dnk/silkeborg","Silkeborg",
"/da/dnk/skanderborg","Skanderborg",
"/da/dnk/skive","Skive",
"/da/dnk/skjern","Skjern",
"/da/dnk/slagelse","Slagelse",
"/da/dnk/solroed-koege","Solrød-Køge",
"/da/dnk/soroe","Sorø",
"/da/dnk/store-heddinge","Store Heddinge",
"/da/dnk/struer","Struer",
"/da/dnk/svendborg","Svendborg",
"/da/dnk/saeby","Sæby",
"/da/dnk/soenderborg","Sønderborg",
"/da/dnk/thisted","Thisted",
"/da/dnk/varde","Varde",
"/da/dnk/vejen","Vejen",
"/da/dnk/vejle","Vejle",
"/da/dnk/vestegnen","Vestegnen",
"/da/dnk/viborg","Viborg",
"/da/dnk/vordingborg","Vordingborg",
"/da/dnk/randers","Randers",
"""

mad_type_urls = """
Sushi: "/category/sushi",
Pizza: "/category/pizza",
Burger: "/category/burgers",
Sandwich: "/category/sandwich",
Kebab: "/category/kebab",
Pasta: "/category/pasta",
Salat: "/category/salad",
Italiensk: "/category/italian",
Thai: "/category/thai",
Japansk: "/category/japanese",
Morgenmad: "/category/breakfast",
Café: "/category/cafe",
Vegetarisk: "/category/vegetarian",
Indisk: "/category/indian",
Amerikansk: "/category/american",
Vegansk: "/category/vegan",
Asiatisk: "/category/asian",
Mexikansk: "/category/mexican",
Healthy: "/category/healthy",
Bowl: "/category/bowl",
Middelhavskøkken: "/category/mediterranean",
Kinesisk: "/category/chinese",
# Bagel: "/category/bagel",
Dansk Mad: "/category/danish",
Vietnamesisk: "/category/vietnamese",
"""



def generate_restaurant_text(restaurant):
    """
    Generate a compact, AI-readable text about a restaurant based on the provided variables.
    
    Args:
        restaurant (dict): A dictionary containing restaurant details with the following keys:
            - name (str): The name of the restaurant.
            - status (str): The status of the restaurant (e.g., 'Lukket' if closed).
            - opening_time (str): The time when the restaurant will open (if it is currently closed).
            - price_range (str): The price range represented by dollar signs (e.g., '$$', '$$$', etc.).
            - delivery_time_value (int/float): The estimated delivery time value.
            - delivery_time_unit (str): The unit of time for delivery (e.g., 'minutes', 'hours').
            - rating (float): The rating of the restaurant (out of 10).
            - tagline (str): The tagline or under-title for the restaurant.
            - link (str): A link to the restaurant's page.
    
    Returns:
        str: A compact, AI-readable text describing the restaurant.
    """
    
    text_parts = []
    
    # Add restaurant name
    if restaurant.get('name'):
        text_parts.append(f"Navn:{restaurant['name']}")
    
    # Add tagline
    if restaurant.get('tagline'):
        text_parts.append(f"Under titel: {restaurant['tagline']}")
    
    # Add restaurant status and opening time if closed
    if restaurant.get('status') == 'Lukket':
        text_parts.append("Lige nu er restauranten lukket")
        if restaurant.get('opening_time'):
            text_parts.append(f" - Men den åbner kl. {restaurant['opening_time']}")
    # Add price range
    if restaurant.get('price_range'):
        text_parts.append(f"Prisniveau hvor at 4 dollartegn($) er dyreste: {restaurant['price_range']}")
    
    # Add delivery time
    if restaurant.get('delivery_time_value') and restaurant.get('delivery_time_unit'):
        text_parts.append(f"Leveringstid: {restaurant['delivery_time_value']} {restaurant['delivery_time_unit']}")
    
    # Add rating
    if restaurant.get('rating') is not None:
        text_parts.append(f"Bedømmelse ud af 10: {restaurant['rating']}/10")
    
    # Add link
    if restaurant.get('link'):
        text_parts.append(f"Link til restauranten: {restaurant['link']}")
    
    # Join all parts into a single compact sentence
    return ' | '.join(text_parts)



def htmlSorter(html: str):
    """
    Extracts information about each restaurant from the provided HTML string.
    
    Args:
        html (str): The HTML string containing information about one or more restaurants.
    
    Returns:
        list: A list of dictionaries where each dictionary represents a restaurant and contains key information.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all restaurant containers
    restaurant_containers = soup.find_all('div', {'data-variant': 'dense'})
    
    restaurant_data = []
    
    for restaurant in restaurant_containers:
        # Extract the name of the restaurant
        name_tag = restaurant.find('a', {'data-test-id': True})
        name = name_tag.text.strip() if name_tag else 'N/A'
        
        # Extract the image URL
        image_tag = restaurant.find('img', src=True)
        image_url = image_tag['src'] if image_tag else 'N/A'
        
        # Extract the status (like "Forudbestil" or "Lukket")
        status_tag = restaurant.find('div', {'class': 'brxwfi6'})
        status = status_tag.text.strip() if status_tag else 'N/A'

        # Extract the opening time if the restaurant is closed
        opening_time_tag = restaurant.find('div', {'class': 'fu09vh0'})
        opening_time = opening_time_tag.text.strip() if opening_time_tag else 'N/A'
        
        # Extract the price range (like "$$$")
        price_tag = restaurant.find('span', {'class': 'v1ad8h3f'})
        price_range = price_tag.text.strip() if price_tag else 'N/A'
        # Convert price range to number of missing $ signs
        if price_tag and price_tag.text.strip():
            dollar_signs = len(price_tag.text.strip())  # Count existing $ signs
            price_range = '$' * (4 - dollar_signs)  # Convert to missing $ signs
        
        # Extract the delivery fee (like "0,00 kr.")
        delivery_fee_tag = restaurant.find('span', {'class': 'f1v0c64o'})
        delivery_fee = delivery_fee_tag.text.strip() if delivery_fee_tag else 'N/A'
        

        # Extract the rating (like "7.2")
        rating = 'N/A'
        rating_tags = restaurant.find_all('span', {'class': 'fhkxgqi'})
        if len(rating_tags) >= 3:  # Ensuring we are accessing the third span correctly
            try:
                rating = float(rating_tags[2].text.strip())  # Extract the text from the third span
            except ValueError:
                rating = 'N/A'

        # Extract the delivery time (like "30-40" and "min.")
        delivery_time_value_tag = restaurant.find('div', {'class': 'b15bvov8'})
        delivery_time_unit_tag = restaurant.find('div', {'class': 'brxwfi6'})
        delivery_time_value = delivery_time_value_tag.text.strip() if delivery_time_value_tag else 'N/A'
        delivery_time_unit = delivery_time_unit_tag.text.strip() if delivery_time_unit_tag else 'N/A'

        
        # Extract the tagline (like "Tid til pizza!")
        tagline_tag = restaurant.find('p', {'class': 'd14x35kv'})
        tagline = tagline_tag.text.strip() if tagline_tag else 'N/A'
        
        # Extract the link to the restaurant's page
        link_tag = restaurant.find('a', href=True)
        link = link_tag['href'] if link_tag else 'N/A'

       # Format the extracted data into a dictionary
        restaurant_info = {
            'name': name,
            'image_url': image_url,
            'status': status,
            'opening_time': opening_time,
            'price_range': price_range,
            'delivery_fee': delivery_fee,
            'rating': rating,
            'delivery_time_value': delivery_time_value,
            'delivery_time_unit': delivery_time_unit,
            'tagline': tagline,
            'link': link
        }

        # Generate and add the formatted restaurant text
        restaurant_info['formatted_text'] = generate_restaurant_text(restaurant_info)
        
        restaurant_data.append(restaurant_info)

    restaurant_text = [restaurant.get('formatted_text') for restaurant in restaurant_data if 'formatted_text' in restaurant]
    formatted_output = '\n'.join(restaurant_text)

    return formatted_output





def menuCardSorter(html):
    """
    Extracts all visible text from the specified target div and its sub-elements.
    
    Args:
        html (str): The HTML string to parse.
        target_div_class (str): The class name of the target div to extract text from.
    
    Returns:
        str: The concatenated text content from the target div.
    """
    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    target_div_class = "sfdszan"
    
    # Find the target div by class name
    target_div = soup.find('div', class_=target_div_class)
    if not target_div:
        return ""  # Return empty string if the target div is not found
    
    # Extract all text from the target div and its child elements
    extracted_text = target_div.get_text(separator=' ', strip=True)
    print("Extracted text type: ")
    print(type(extracted_text))
    
    return extracted_text




def prompts(userInput, conversation_history, current_prompt, restaurants_html, menuCard_html):
    current_time = datetime.now(pytz.timezone('Europe/Copenhagen')).strftime("%H:%M")


    prompt = f"""
# ROLLE
Du er en venlig, effektiv og hjælpsom AI-assistent udviklet af madleveringsvirksomheden Wolt.com kaldet "Wolt AI". 
Dit primære formål er at hjælpe brugere med at navigere på Wolt.com og fuldføre deres madbestilling. Det er vigtigt at du er proaktiv med at hjælpe brugeren bestille mad 
- Dette gør du ved at foreslå relevante restauranter og madtyper.
Når brugeren kigger på restauranter i en kategori eller en restaurants menukort, har du adgang til brugerens aktuelle sideinformation (sideindhold), 
deres samtalehistorik og deres seneste besked. Du kan ændre URL’er, foreslå næste trin og give klar og præcis vejledning som en interaktiv assistent. 


# PERSONLIGHED
Din personlighed er:
- Venlig, imødekommende og opmuntrende.
- Klar, direkte og hjælpsom i dine svar.
- Proaktiv i at tilbyde relevante forslag.
- Rolig og selvsikker, så brugeren føler sig støttet og guidet gennem hele processen.

# MÅL
Dit primære mål er at hjælpe brugeren med at bestille mad via Wolt.com. Dette mål opnås ved at følge disse 6 trin:
1. **Find byen som brugeren vil bestille fra** og sikre, at det er en by, hvor Wolt leverer fra.
2. **Hjælp med at finde madtype** baseret på brugerens ønsker.
3. **Find den ønskede restaurant** og præsenter den for brugeren.
4. **Hjælp brugeren med at vælge maden**, og besvar eventuelle spørgsmål de måtte have og tilbyder om de vil have noget ekstra med som du kan se er på menukortet før de acceptere. Det er også vigtigt at du er proaktiv her og foreslår mad eller tilbehør som du kan se er på menukortet - som du kan spørge om de vil have med til deres bestilling.
5. **Spørg om der er nogle ekstra noter til leveringen** og gennemgå bestillingen for at sikre, at alt er korrekt - du må kun gå videre når de har svaret på dette spørgsmål.
6. **Bekræft bestillingen** og bed brugeren om at angive deres telefonnummer for at modtage opdateringer.

# KONTEKST
Her er den aktuelle kontekst, du skal bruge til at generere dit svar. Brug disse oplysninger for at gøre dit svar mere relevant og personligt.


- **Nuværende tid**: {current_time}
- **URL'er til alle byer som wolt levere til**: 
{by_urls}\n\n
Du kan ikke hjælpe brugeren med at finde en restaurant i en by som ikke står på listen, da wolt ikke leverer til de byer.

- **URL'er til alle madtyper som wolt har**: 
{mad_type_urls}\n
Du kan ikke hjælpe brugeren med at finde en madtype som ikke står på listen, da ingen restauranter på wolt har dem madtyper.

# RESPONSFORMAT
Dit svar skal altid være i præcis det følgende JSON-format. Du må IKKE tilføje yderligere tekst, forklaringer eller introduktioner. Eller skrive noget i markdown text da det skal følge præcist JSON formatet herunder.

{{
    "navigation": "[URL-til-ny-side]",
    "message": "[svar-besked-til-bruger]"
}}

Ved slutningen af brugerens rejse, når ordren er bekræftet og brugeren har angivet deres telefonnummer, skal formatet udvides til at inkludere yderligere detaljer:

{{
    "navigation": "none",
    "message": "Tak for din bestilling! Din ordre er bekræftet, og du får opdateringer via SMS. Har du tilføjet dit telefonnummer?",
    "order_confirmation": "bestillingen er bestilt",
    "restaurant": "[restaurant-navn]",
    "order_details": "[bestilling-detaljer]",
    "extra_notes": "[ekstra-noter]",
    "phone_number": "[telefonnummer]"
}}

# EKSEMPLER
Her er et par eksempler på gyldige JSON-svar, som du kan give. Brug dem som skabelon.

**Eksempel 0: Normal samtale**
Når du taler hjælper brugeren med at finde mad, så vil du på størstedelen af beskederne ikke være nød til at navigere brugeren til en ny side.
Her skal du bare hjælpe brugeren så godt du kan - og for ikke at at navigere til en anden side og bare blive på samme side, skal du bare lade "navigation" være en tom streng:
{{
    "navigation": "",
    "message": "[svar-besked-til-bruger]"
}}
Hvis brugeren har skrevet: "Mit navn er Jonas", vil det se således ud:
{{
    "navigation": "",
    "message": "Hej <b>Jonas</b>,😃 jeg vil gerne hjælpe dig med at finde <i>mad</i> til dig. <br> Kan du fortælle mig, <b>hvilken by</b> du er fra?"
}}

**Eksempel 1: Brugeren vil se restauranter i en by**
{{
    "navigation": "https://wolt.com/ + [by-url]",
    "message": "[svar-besked-til-bruger]"
}}
Hvis brugeren har skrevet: "Jeg vil bestille mad fra Randers", vil det se således ud:
{{
    "navigation": "https://wolt.com/da/dnk/randers",
    "message": "Perfekt! Jeg har fundet nogle <b>fantastiske restauranter</b> i <b>Randers</b> til dig. <br> Her er nogle lækre kategorier, du kan vælge imellem: <br> • Sushi <br> • Pizza <br> • Burger <br> • Sandwich <br> • Kebab <br> Hvad har du lyst til at spise?"
}}

**Eksempel 2: Brugeren vælger derefter en madtype**
{{
    "navigation": "https://wolt.com/ + [by-url] + [mad-type-url]",
    "message": "[svar-besked-til-bruger]"
}}
Hvis brugeren har tidligere har skrevet at de er fra København og nu skriver: "Jeg vil have en pizza", vil det se således ud:
{{
    "navigation": "https://wolt.com/da/dnk/copenhagen/category/pizza",
    "message": "Super, så navigerer jeg til <b>pizza-kategorien</b> i <b>København</b>. <br> Skal jeg give nogle forslag til restauranterne, eller er der noget, der fanger din interesse?"
}}

**Eksempel 3: Brugeren vælger en restaurant**
{{
    "navigation": "[fuldt-url-til-restauranten]",
    "message": "[besked-til-bruger]"
}}

Når du skal navigere brugeren til en bestemt restaurant, så burde du have adgang til alle restauranterne som brugeren kigger på ved 'Sideindhold' sektionen i denne besked, 
så du skal bare skrive URL'en til den restaurant præcis some det står skrevet i 'Sideindhold' sektionen:
{{
    "navigation": "https://wolt.com/da/dnk/odense/restaurant/mr-fried-chickenn",
    "message": "Godt valg! Jeg har åbnet <b>restauranten Mr. Fried Chicken</b> til dig. <br> Er der noget, der fanger din interesse?"
}}

**Eksempel 4: Brugeren bekræfter sin ordre**
Det er MEGET vigtigt at du ikke må bekræfte en ordre før at brugeren har skrevet om de har nogle noter til bestillingen og har skrevet deres telefonnummer. 
Hvis en af de to ikke er bekræftet gør du tilbage for at bekræfte dem, så under INGEN omstændighed må du sende dette format hvis brugeren ikke direkte har skrevet sit telefonnummer i en besked.
{{
    "navigation": "",
    "message": "[besked-til-bruger]",
    "order_confirmation": "[bestilling-status]",
    "restaurant": "[restaurant-navn]",
    "order_details": "[bestilling-detaljer]",
    "extra_notes": "[ekstra-noter]",
    "phone_number": "[telefonnummer]"
}}
Indsat dummy data:
{{
    "navigation": "",
    "message": "Tak for din bestilling! <br> Din ordre er bekræftet, og du får opdateringer via SMS.",
    "order_confirmation": "bestillingen er bestilt",
    "restaurant": "OpenAlDente",
    "order_details": "1 x Carbonara Pasta, 2 x Ramen Manu'er (Spicy) med coca cola",
    "extra_notes": "At wolt budet skal banke tre gange",
    "phone_number": "+4512345678"
}}


# INSTRUKTIONER
1. Brug **konteksten** (sideindhold, samtalehistorik og seneste brugerbesked) til at generere dit svar.
2. Altid brug det definerede **responsformat** som du har fået beskrevet. Svar kun med et JSON-objekt med ingen tekst overhoved før eller efter.
3. Din tone skal matche den definerede **personlighed**.
4. Følg de 6 **måltrin** for at guide brugeren fra start til slut.
5. Hvis du er i tvivl, bed brugeren om yderligere oplysninger.

# DU VIL BLIVE STRAFFET FOR
- At hjælpe brugeren med noget der ikke har noget med at bestille mad at gøre. Hvis brugeren om noget der ikke har noget med at bestille mad at gøre, så skal du dreje samtalen tilbage til madbestilling.
- At du ikke følger de 6 måltrin.
- At du ikke følger det definerede responsformat for hvert enkelt trin.
- At give et svar hvor teksten står i markdown format.
- At halvisualisere teksten i dine svar - Du vil blive stræffet rigtig hårdt for at skrive restauranter eller madtyper i dine svar som du ikke har information omkring tidligere.
- At du ikke følger den definerede personlighed.\n

# DU VIL BLIVE BELØNNET FOR
- At være proaktiv og foreslå relevante restauranter, madtyper og retter fra menukortet - Men du vil kun blive belønnet hvis du forslår noget som du ved eksisterer.
- At være hjælpsom og opmuntrende.
- Kun at forslå restauranter som du ved eksisterer fordi de står under Sideindhold sektionen.
- At bruge HTML inline-elementer til at formatere teksten i dine svar, så det ser bedre ud.\n


# RELEVANT KONTEKST
- **Restauranter**: 
Du vil kun have adgang til sideindholdet hvis du og brugeren lige nu kigger på restauranter eller i en madkategori. 
Når du skal navigere brugeren til en bestemt restaurant, så finder du hele URL'en til restauranterne som kunden kigger på her.
Hvis du er på en side som har information omkring restauranter, er det vigtigt at det er noget du bruger proaktivt og viser brugeren det.
Resturanterne som du kan nævne og navigere til er her:
{restaurants_html}\n\n
Hvis du nævner forslag til resturanter må du kun nævne nogle der står på listen, hvis restaurant som brugeren nævner ikke er med i listen, så skal du informere dem om at det ikke er en af valg mulighederne.

{menuCard_html}


- Samtalehistorik: 
Her er dig og brugerens samtalehistorik ind til videre:
{conversation_history}

Brug denne kontekst og følg de opstillede retningslinjer for at generere et svar i korrekt JSON-format.
- Du skal nu svare på denne besked fra brugeren: "{userInput}"
"""

    print("Her er prompten: ", prompt)
    print("----slut----")

    return prompt