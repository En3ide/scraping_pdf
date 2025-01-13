import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def scrape_and_download_pdfs(page_url, download_directory, div_id=None, div_class=None):
    """
    Scrap la page web passé en argument pour récupérer tout les pdf contenue

    Args:
        page_url (str): URL de la page à scrap
        download_directory (str): Chemin vers le repertoire de téléchargement
        div_id (str): Si contenu dans un champ en particulier de la page, alors on donne l'id
        div_class (str): Si contenu dans un champ en particulier de la page, alors on donne la class
    """
    os.makedirs(download_directory, exist_ok=True)

    try:
        # Fetch the webpage
        response = requests.get(page_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the webpage: {e}")
        return

    # Parse the HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all <a> tags with href not ending in .pdf and include the text of the link
    # Récupérer le div spécifié
    if div_id:
        container = soup.find('div', id=div_id)
    elif div_class:
        container = soup.find('div', class_=div_class)
    else:
        container = soup  # Analyse complète si aucun div n'est spécifié
    if container is None:
        print(f"Div with id='{div_id}' or class='{div_class}' not found.")
        return
    
    # Find all <a> tags with href ending in .pdf
    pdf_links = [
        a['href'] for a in container.find_all('a', href=True)
        if a['href'].endswith('.pdf')
    ]

    if not pdf_links:
        print("No PDF links found on the page.")
        return

    print(f"Found {len(pdf_links)} PDF(s).")

    for link in pdf_links:
        # Resolve relative URLs to absolute URLs
        pdf_url = link if link.startswith('http') else requests.compat.urljoin(page_url, link)

        try:
            # Fetch the PDF content
            pdf_response = requests.get(pdf_url)
            pdf_response.raise_for_status()

            # Determine the file name
            pdf_name = os.path.basename(pdf_url)

            # Save the PDF to the directory
            pdf_path = os.path.join(download_directory, pdf_name)
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(pdf_response.content)

            print(f"Downloaded: {pdf_name}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {pdf_url}: {e}")
    

if __name__ == "__main__":
    page_url = input("Enter the URL of the webpage to scrape: ").strip()
    download_directory = input("Enter the directory to save PDFs (e.g., ./result): ").strip()
    
    scrape_and_download_pdfs(page_url, download_directory, "listing", )
