from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_definition_url(mot):
    """Récupère l'URL Larousse et le numéro associé pour un mot donné"""
    search_url = f"https://www.larousse.fr/dictionnaires/francais/{mot}"
    response = requests.get(search_url)
    if response.status_code == 200:
        # Retourne l'URL finale après la redirection
        return response.url
    else:
        return None

def scrape_definitions(url):
    """Scrape toutes les définitions à partir de l'URL donnée"""
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraction du mot principal et de sa catégorie grammaticale
        word = soup.find('h2', class_='AdresseDefinition').text.strip()
        category = soup.find('p', class_='CatgramDefinition').text.strip()

        # Extraction des définitions
        definitions_list = []
        definitions = soup.find_all('li', class_='DivisionDefinition')
        for definition in definitions:
            definitions_list.append(definition.text.strip())

        # Extraction des synonymes
        synonyms_section = soup.find_all('p', class_='Synonymes')
        synonyms = [syn.text.strip() for syn_section in synonyms_section for syn in syn_section.find_all('span', class_='Renvois')]
        
        # Extraction des autres résultats potentiels (autres articles)
        other_results = []
        other_result_sections = soup.find_all('article', class_='sel')
        for section in other_result_sections:
            title = section.find('div', class_='item-result').text.strip()
            other_results.append(title)
        
        # Création de la structure JSON
        result = {
            "word": word,
            "category": category,
            "definitions": definitions_list,
            "synonyms": synonyms,
            "other_results": other_results
        }
        return result
    else:
        return None

@app.route('/recherche', methods=['GET'])
def recherche():
    mot = request.args.get('dico')
    
    if mot:
        url = get_definition_url(mot)
        
        if url:
            result = scrape_definitions(url)
            if result:
                return jsonify(result)
            else:
                return jsonify({"error": "Définitions non trouvées"}), 404
        else:
            return jsonify({"error": "Mot non trouvé"}), 404
    else:
        return jsonify({"error": "Veuillez fournir un mot"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
