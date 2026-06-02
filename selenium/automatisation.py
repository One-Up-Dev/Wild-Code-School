from selenium import webdriver 
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys 
import time 
import pandas as pd 

# Configuration du navigateur
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)

# Ouvre le navigateur et va sur le site amazon.com
driver.get("https://www.amazon.com/")

# Clique sur le bouton "Continue Shopping" si il apparait
try:
    time.sleep(3)
    clic_bouton_dismiss = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[3]/div/div/form/div/div/span/span/button')
    clic_bouton_dismiss.click()
except:
    pass 

# Clique sur le bouton des cookies si il apparait
try:
    time.sleep(3)
    clic_bouton_dismiss = driver.find_element(By.XPATH, '//*[@id="nav-flyout-iss-anchor"]/div[2]/div/div[3]/span[1]/span/input')
    clic_bouton_dismiss.click()
    print('Bouton dismiss cliqué !')

# Vide la barre de recherche avant d'indiquer quelque chose
    recherche_produit = driver.find_element(By.ID, 'twotabsearchtextbox')
    recherche_produit.clear()
# On indique ce quon recherche
    recherche_produit.send_keys("Macbook pro 2025")
    recherche_produit.send_keys(Keys.ENTER)
    # On attend le temps que la page des produits charge
    time.sleep(5)

except:
    pass

# On va récupérer un produit
try:
    # On cherche les produits avec find_elements
    cartes_produits = driver.find_elements(By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')
    
    liste_donnees = []

    # On fait une boucle sur chaque carte de produit trouvée
    for carte in cartes_produits:
        try:
            # On cherche le titre et le prix À l'intérieur de la carte 
            nom = carte.find_element(By.CSS_SELECTOR, "h2 span").text
            prix = carte.find_element(By.CLASS_NAME, 'a-price-whole').text
            
            # On ajoute le produit au dictionnaire
            liste_donnees.append({"Nom": nom, "Prix": prix})
        except:
            continue # Si un élément manque dans la carte on passe au suivant

    # Boucle terminé, on créé le DataFrame
    df = pd.DataFrame(liste_donnees)
    print(df)

except Exception as nomDeLerreur:
    print(f'Erreur : {nomDeLerreur}')