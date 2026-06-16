# 📘 Révision — Checkpoint 3 Data Analyst

> Documentation pratique organisée par thème, pour réviser ce qui a été codé dans
> `Checkpoint_3_Data_Analyst.ipynb`. Format question → réponse.
>
> **État :** ✅ Regex · ✅ Scraping (Missions 1, 2 & 3) · ✅ Géocoding/Folium · ✅ NLP (vérifié) · ✅ JSON

---

## Sommaire

1. [Regex](#1-regex)
2. [Scraping](#2-scraping)
3. [Géocoding (+ carte Folium)](#3-géocoding--carte-folium)
4. [NLP — Classification de sentiments](#4-nlp--classification-de-sentiments)
5. [JSON — manipulation récursive](#5-json--manipulation-récursive-optionnel)

---

# 1. Regex

## 1.1 Les 3 regex (version actuelle du notebook)

```python
import re

# 1) Valide la plupart des formats d'emails standards
regex_email = r"\S+@\S+\.\S+"

# 2) Valide une date au format AAAA-MM-JJ
regex_date = r"\d{4}-\d{2}-\d{2}"

# 3) Valide un code postal français standard à 5 chiffres
regex_cp = r"^0[1-9]|[1-8]\d|9[0-8]$"
```

> ℹ️ Ce sont des versions **volontairement simples**. Elles « marchent » sur les cas
> évidents mais ont des **limites** (voir les ⚠️ ci-dessous, vérifiées en exécutant le
> code). Des versions plus robustes sont données en [1.4](#14-versions-robustes-optionnel).

### ❓ C'est quoi le `r"..."` ?
Une **raw string** : Python n'interprète pas les `\` comme caractères spéciaux
(`\n`, `\t`...). Indispensable en regex car on utilise des `\` partout.

### ❓ À quoi servent `^` et `$` ?
Ce sont les **ancres** : `^` = début de chaîne, `$` = fin. Elles forcent la chaîne
**entière** à correspondre. Sans elles (ou mal placées), une chaîne avec du texte en
trop peut matcher quand même — c'est la cause de plusieurs bugs ci-dessous.

---

### Regex email `\S+@\S+\.\S+` — décorticage

| Bout | Signification |
|---|---|
| `\S+` | 1+ caractères **non-espace** (avant le `@`) |
| `@` | le `@` littéral |
| `\S+` | 1+ non-espace (le domaine) |
| `\.` | un point **littéral** |
| `\S+` | 1+ non-espace (l'extension) |

✅ Rejette bien `"invalide@"` et `"@nope.com"`.
⚠️ **Limite** : pas d'ancre `$`. Avec `re.match` (qui n'ancre qu'au début), une chaîne
avec **du texte en trop** passe : `"test@exemple.com garbage"` → **True** (à tort).
Accepte aussi des trucs douteux (`a@@b..c`). C'est laxiste mais « attrape la plupart
des formats », ce que demandait la consigne.

---

### Regex date `\d{4}-\d{2}-\d{2}` — décorticage

| Bout | Signification |
|---|---|
| `\d{4}` | 4 chiffres (année) |
| `-` | tiret littéral |
| `\d{2}` | 2 chiffres (mois) |
| `\d{2}` | 2 chiffres (jour) |

✅ Accepte le format `AAAA-MM-JJ` et rejette `"2026-6-1"` (1 seul chiffre).
⚠️ **Bugs** : aucune **borne** sur le mois/jour, ni ancre de fin → acceptent des dates
**invalides** :
- `"2026-13-01"` (mois 13) → **True**
- `"2026-02-30"` (30 février) → **True**
- `"2026-06-15 garbage"` (texte en trop) → **True**

→ Pour borner, il faudrait `^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$` (voir 1.4).

---

### Regex code postal `^0[1-9]|[1-8]\d|9[0-8]$` — décorticage

> 🟥 **Cette regex est cassée** : elle ne valide **que 2 chiffres**, pas 5.

**Pourquoi ?** Le `|` (OU) a la priorité **la plus faible**. La regex est donc lue
comme **3 alternatives** indépendantes :

| Alternative | Ce qu'elle teste |
|---|---|
| `^0[1-9]` | « commence par `0` puis 1-9 » (juste 2 caractères, ancré au début) |
| `[1-8]\d` | « un chiffre 1-8 suivi d'un chiffre » (aucune ancre !) |
| `9[0-8]$` | « `9` puis 0-8 à la fin » |

Comme `re.match` n'ancre **qu'au début**, c'est surtout `[1-8]\d` qui agit → il suffit
que les **2 premiers** caractères ressemblent à un département. Conséquences vérifiées :

| Entrée | Résultat | Attendu | |
|---|---|---|---|
| `"75001"` | True | True | ✅ (par chance, matche juste `"75"`) |
| `"750011"` (6 chiffres) | **True** | False | 🟥 bug |
| `"12abc"` | **True** | False | 🟥 bug |
| `"97400"` (DOM) | **False** | True | 🟥 bug |
| `"00999"` | False | False | ✅ |

→ La version correcte (valide bien **5 chiffres**) : `^(?:0[1-9]|[1-8]\d|9[0-8])\d{3}$`
(voir 1.4). Le `(?:...)` regroupe les alternatives **avant** d'exiger `\d{3}`.

> 🔑 **Leçon clé** : `|` s'étend le plus loin possible. Pour limiter sa portée, il faut
> le **mettre entre parenthèses** : `(a|b)c` ≠ `a|bc`.

---

## 1.2 Aide-mémoire de syntaxe regex

| Symbole | Sens | Exemple |
|---|---|---|
| `\d` | un chiffre | `\d{4}` = 4 chiffres |
| `\w` | lettre, chiffre ou `_` | |
| `.` | n'importe quel caractère | (échappé : `\.` = un vrai point) |
| `[...]` | **classe** : un seul caractère parmi la liste | `[abc]`, `[0-9]` |
| `[^...]` | un caractère **sauf** ceux listés | `[^0-9]` |
| `+` | 1 ou plus | |
| `*` | 0 ou plus | |
| `?` | 0 ou 1 (optionnel) | |
| `{n}` | exactement n | `\d{4}` |
| `{n,m}` | entre n et m | |
| `(a\|b)` | a **ou** b (alternative) | |
| `(?:...)` | groupe sans capture | |
| `^` `$` | début / fin de chaîne | |

💡 Dans une classe `[...]`, les caractères `.` `+` `*` perdent leur sens spécial → pas besoin de les échapper.

---

## 1.3 Les boucles de test

```python
emails = ["test@exemple.com", "j.dupont+wcs@mail-server.fr", "invalide@", "@nope.com", "a@b.fr", "fab-paris@job.co.fr"]

print("Emails :")
for e in emails:
    print(f"  {e:28} -> {bool(re.match(regex_email, e))}")
```

### ❓ Que fait `re.match(regex, e)` ?
Essaie de faire correspondre la regex au **début** de `e`. Renvoie un **objet match**
si ça colle, sinon **`None`**.

| Fonction | Ancrage |
|---|---|
| `re.match` | au **début** seulement |
| `re.search` | n'importe où dans la chaîne |
| `re.fullmatch` | toute la chaîne (équivaut à `^...$`) |

> ⚠️ **Important ici** : `re.match` n'ancre **qu'au début**. Comme les regex actuelles
> n'ont pas de `$` (ou un `$` mal placé), du **texte en trop** à la fin passe inaperçu.
> `re.fullmatch` corrigerait ça automatiquement.

### ❓ Pourquoi `bool(...)` ?
Convertit le résultat en booléen lisible : objet match → `True`, `None` → `False`.

### ❓ Le `{e:28}` dans la f-string ?
`:28` aligne la chaîne sur 28 caractères → les `->` sont en colonnes propres.
(Variante : `{e!r:28}` ajouterait les guillemets via `repr()`, pratique pour repérer
les espaces parasites.)

### 🔑 Réflexe clé
On teste **toujours** une regex avec des cas **valides ET invalides** (les pièges :
`invalide@`, `2026-13-01`, `750011`...) pour prouver qu'elle rejette ce qu'elle doit
rejeter. C'est exactement ce qui a permis de **voir les bugs** ci-dessus.

---

## 1.4 Versions robustes (optionnel)

Si tu veux corriger les limites repérées plus haut, voici des versions **ancrées et
bornées** (à utiliser avec `re.match` ou `re.fullmatch`) :

```python
# Email : ancré des deux côtés, finit par une lettre/chiffre
regex_email = r"^[\w.+-]+@[\w-]+\.[\w.-]+\w$"

# Date : mois 01-12 et jour 01-31 réellement bornés
regex_date = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"

# Code postal : valide bien 5 chiffres (le (?:...) regroupe avant d'exiger \d{3})
regex_cp = r"^(?:0[1-9]|[1-8]\d|9[0-8])\d{3}$"
```

| Différence clé | Effet |
|---|---|
| `^...$` partout | empêche le texte en trop |
| `(0[1-9]\|1[0-2])` pour le mois | rejette `13`, `00` |
| `(?:...)\d{3}` pour le CP | force **5 chiffres** (corrige le bug du `\|`) |

---

# 2. Scraping

> Cibles : [books.toscrape.com](https://books.toscrape.com/) — récupérer titre, prix, etc.

> 🗺️ **Comment lire cette partie.** Les sections **2.1 → 2.6** retracent le
> **cheminement d'apprentissage** (concepts + versions intermédiaires explorées dans
> `Untitled.ipynb` : fonction `prix_en_euros`, variable `lien_du_site`, missions
> séparées, version « à plat »…). Le **notebook du checkpoint** (`Checkpoint_3`), lui,
> ne contient **qu'une seule cellule** consolidée (les 3 missions) → c'est la section
> **2.7** qui correspond **littéralement** à ce code. Les noms y diffèrent un peu
> (`URL_SITE`/`TAUX_GBP_EUR` et conversion en ligne, au lieu de `lien_du_site`/`prix_en_euros`).

## 2.1 C'est quoi le scraping ?

`requests.get(url)` télécharge le **HTML brut** d'une page (du texte avec des balises).
Le scraping = **extraire des infos précises** de ce HTML. **BeautifulSoup** transforme
ce texte en objet navigable pour aller piocher dedans.

```
Le navigateur affiche une page ⟷ derrière, c'est du HTML ⟷ requests le télécharge ⟷ BeautifulSoup le fouille
```

---

## 2.2 La cellule de préparation

```python
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

lien_du_site = "https://books.toscrape.com/"
taux_gbp_eur = 1.17  # taux de conversion approximatif GBP -> EUR

def prix_en_euros(texte_prix):
    """Convertit un prix type '£51.77' en euros."""
    montant = float(re.search(r"[\d.]+", texte_prix).group())
    return round(montant * taux_gbp_eur, 2)
```

| Outil | Rôle |
|---|---|
| `requests` | télécharge la page |
| `BeautifulSoup` (de `bs4`) | analyse / fouille le HTML |
| `pandas` | range le résultat en tableau (DataFrame) |
| `urljoin` | construit des URL proprement |

### ❓ Comment marche `prix_en_euros` ?
Le prix sur le site est une **chaîne** `"£51.77"` (avec le symbole £), inutilisable pour calculer.

| Étape | Effet |
|---|---|
| `re.search(r"[\d.]+", texte_prix)` | isole les chiffres+point → `51.77` (jette le £) |
| `.group()` | récupère le texte trouvé → encore une chaîne `"51.77"` |
| `float(...)` | convertit en **nombre** `51.77` |
| `* taux_gbp_eur` | conversion £ → € |
| `round(..., 2)` | arrondit aux centimes |

💡 Définie **une fois** dans une fonction → réutilisée dans les 3 missions (principe **DRY**).

---

## 2.3 Mission 1 — titre + prix de tous les livres

```python
titres = []
prix = []

for page in range(1, 51):                                    # boucle externe : les 50 pages
    url = urljoin(lien_du_site, f"catalogue/page-{page}.html")
    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    for livre in soup.select("article.product_pod"):         # boucle interne : les 20 livres
        titres.append(livre.h3.a["title"])
        prix.append(prix_en_euros(livre.select_one("p.price_color").text))

livres_m1 = pd.DataFrame({"titre": titres, "prix_euros": prix})
```

### Le schéma mental
```
Pour chaque page (1→50) :
    télécharger la page
    Pour chaque livre de la page (×20) :
        récupérer titre + prix → ranger dans les listes
À la fin : listes → DataFrame
```
Double boucle : 50 pages × 20 livres = **1000 livres**.

### ❓ Détails ligne par ligne

| Code | Explication |
|---|---|
| `titres = []` / `prix = []` | listes vides remplies au fur et à mesure (`append`) |
| `range(1, 51)` | nombres **1 à 50** (la borne 51 est exclue) |
| `f"catalogue/page-{page}.html"` | f-string : insère le n° → `page-1.html`, `page-2.html`... |
| `urljoin(base, chemin)` | colle l'URL proprement (gère les `/`) |
| `requests.get(url).content` | le HTML brut (octets) |
| `BeautifulSoup(..., "html.parser")` | objet fouillable ; `"html.parser"` = moteur intégré |
| `soup.select("article.product_pod")` | **liste** de tous les livres de la page |
| `livre.h3.a["title"]` | navigue `<h3>`→`<a>`, lit l'**attribut** `title` (titre complet) |
| `livre.select_one("p.price_color")` | **un seul** élément (le prix) |
| `pd.DataFrame({col: liste})` | construit le tableau colonne par colonne |

---

## 2.4 Comment trouver les bons sélecteurs ?

> **LA** compétence du scraping.

### Méthode en 2 étapes
1. **Inspecter** : clic droit → « Inspecter » (ou `F12`) sur l'élément voulu dans le
   navigateur. Le HTML correspondant se surligne.
2. **Lire la structure** et repérer des **balises + classes** fiables et répétées.

> 💡 Depuis Python, sans navigateur : `print(element.prettify())` affiche le HTML indenté.

### Le HTML réel d'un livre
```html
<article class="product_pod">
  <h3>
    <a href="..." title="A Light in the Attic">A Light in the ...</a>
  </h3>
  <div class="product_price">
    <p class="price_color">£51.77</p>
    <p class="instock availability"> In stock </p>
  </div>
</article>
```

| Ce qu'on veut | Sélecteur | Pourquoi |
|---|---|---|
| Le conteneur d'un livre | `article.product_pod` | balise `article` + classe `product_pod` |
| Le titre | `livre.h3.a["title"]` | le texte visible est tronqué (`...`), l'attribut `title` est **complet** |
| Le prix | `p.price_color` | classe unique dans le bloc livre |

### 🔑 La logique de « zoom »
On cible **le conteneur répété d'abord** (`article.product_pod`), PUIS on cherche
**à l'intérieur** avec `livre.select_one(...)`. Ça garantit que titre et prix
appartiennent **au même livre**.

```python
for livre in soup.select("article.product_pod"):  # 1. lister les livres
    livre.h3.a["title"]                            # 2. chercher DANS ce livre
    livre.select_one("p.price_color")             #    (pas dans toute la page)
```

### Critères d'un BON sélecteur
| ✅ À privilégier | ❌ À éviter |
|---|---|
| classe sémantique (`price_color`) | position (`p:nth-child(3)`) — casse vite |
| le plus court possible | chemins longs `div > div > p` |
| unique dans son contexte | classes auto-générées (`css-1x7yz`) |

### `select` vs `select_one`
- `select(...)` → **liste** d'éléments (pour boucler).
- `select_one(...)` → **le premier** élément seul (pour une valeur unique).

### Deux façons d'écrire un chemin
```python
livre.h3.a["title"]                 # navigation par balises (chemin simple)
livre.select_one("p.price_color")   # sélecteur CSS (plus puissant/robuste)
```

---

## 2.5 Le `.text` — passer du HTML au texte Python

```python
livre.select_one("p.price_color").text
```

### ❓ Quelle différence avec/sans `.text` ?

| Expression | Renvoie | Type |
|---|---|---|
| `livre.select_one("p.price_color")` | la balise `<p ...>£51.77</p>` | `Tag` (objet bs4) |
| `....text` | le contenu `"£51.77"` | `str` (chaîne) |

`.text` **extrait le contenu textuel** de la balise (en jetant le HTML autour).
C'est l'étape qui fait passer du **monde HTML** au **monde texte Python**, exploitable
par `re.search`, `float`, etc.

### Pourquoi c'est obligatoire ici
```python
prix.append( prix_en_euros( livre.select_one("p.price_color").text ) )
#                            └─ Tag ──────────────────────┘ .text  └─ "£51.77"
```
Sans `.text`, on passerait un `Tag` à `prix_en_euros`, et le `re.search` planterait
(la regex travaille sur du texte, pas sur un objet HTML).

### ⚠️ Piège : `.text` ramasse TOUT le texte des balises filles
Pour `<p class="instock availability"><i></i> In stock </p>`, `.text` renvoie
`'\n\n    \n        In stock\n    \n'` (avec espaces et `\n`).

→ D'où le `.text.strip().lower()` en Mission 2 :
- `.strip()` enlève espaces/`\n` au début et à la fin
- `.lower()` met en minuscules (comparaison insensible à la casse)

> 🔑 `.text` = « donne-moi le **contenu lisible** de cette balise, sans le HTML ».
> Variante pratique : `.get_text(strip=True)` fait `.text` + nettoyage d'un coup.

---

## 2.6 Mission 2 — ajouter la catégorie et le stock

> But : DataFrame **catégorie · titre · prix (€) · en stock**.
> Code de la version « à plat » (sans `urljoin`, sans fonction) — `Untitled.ipynb`.

### ❓ Pourquoi c'est plus dur que la Mission 1 ?
La **catégorie n'apparaît pas** sur la page liste d'un livre. L'astuce : ne plus
parcourir le catalogue page par page, mais **parcourir chaque catégorie** une par une
via le menu latéral → on connaît ainsi la catégorie de chaque livre « gratuitement ».

---

### Cellule 1 — Imports
```python
import pandas as pd
import requests
from bs4 import BeautifulSoup

URL_SITE = "https://books.toscrape.com/"
TAUX_GBP_EUR = 1.17
```
Mêmes outils qu'en Mission 1. On n'importe **pas** `urljoin` : on construira les URL à la main.

---

### Cellule 2 — Récupérer les catégories
```python
soup = BeautifulSoup(requests.get(URL_SITE).content, "html.parser")

categories = {}
for a in soup.select("div.side_categories ul li ul li a"):
    nom = a.text.strip()
    categories[nom] = URL_SITE + a["href"]   # concaténation

print(len(categories), "catégories")
```

| Code | Explication |
|---|---|
| `soup.select("div.side_categories ul li ul li a")` | tous les liens du **menu latéral** (le `ul` imbriqué = la sous-liste des catégories) |
| `a.text.strip()` | le nom de la catégorie (sans espaces autour) |
| `URL_SITE + a["href"]` | l'URL complète : le href est relatif (`catalogue/category/.../index.html`) et `URL_SITE` finit par `/` → simple collage |
| `categories[nom] = ...` | on remplit un **dictionnaire** `{nom: url}` |

→ Résultat : **50 catégories**.

---

### Cellule 3 — Parcourir catégories et pages (le cœur)
```python
livres = []

for nom, url_categorie in categories.items():
    dossier = url_categorie.replace("index.html", "")   # .../travel_2/
    url = url_categorie

    while url:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")

        for bloc in soup.select("article.product_pod"):
            prix_texte = bloc.select_one("p.price_color").text
            prix_euros = round(float(prix_texte.replace("£", "")) * TAUX_GBP_EUR, 2)
            dispo = bloc.select_one("p.instock.availability").text
            livres.append({
                "categorie": nom,
                "titre": bloc.h3.a["title"],
                "prix_euros": prix_euros,
                "en_stock": "in stock" in dispo.lower(),
            })

        suivant = soup.select_one("li.next a")
        if suivant:
            url = dossier + suivant["href"]   # .../travel_2/ + page-2.html
        else:
            url = None
```

**Trois boucles emboîtées dans l'idée :**
```
Pour chaque catégorie :
    Tant qu'il reste une page (while url) :
        Pour chaque livre de la page :
            extraire les infos
        passer à la page suivante (ou arrêter)
```

| Élément | Rôle |
|---|---|
| `for nom, url_categorie in categories.items()` | parcourt le dict : `nom` + son `url` |
| `while url:` | continue **tant que** `url` n'est pas `None` → gère la pagination de la catégorie |
| `bloc.select_one("p.price_color").text` | le prix texte `"£51.77"` |
| `float(prix_texte.replace("£", ""))` | enlève le `£` puis convertit en nombre |
| `"in stock" in dispo.lower()` | `True`/`False` selon la dispo (insensible à la casse) |
| `livres.append({...})` | range un **dictionnaire par livre** dans la liste |

### 🔑 Le point délicat : reconstruire l'URL de la page suivante
Le bouton « next » donne un href **court** (`page-2.html`), relatif au **dossier** de la
catégorie — pas à `URL_SITE`. Donc :
```python
dossier = url_categorie.replace("index.html", "")   # .../travel_2/index.html -> .../travel_2/
url = dossier + suivant["href"]                       # .../travel_2/ + page-2.html
```
> C'est exactement ce que `urljoin(url, href)` faisait automatiquement en résolvant
> un lien relatif. Le faire à la main montre la mécanique — mais ça ne marche que
> parce que les liens sont **simples** (pas de `../` ni de `/` initial).

| `while` / `if` | Effet |
|---|---|
| `suivant = soup.select_one("li.next a")` | cherche le bouton « next » (`None` s'il n'existe pas) |
| `url = dossier + suivant["href"]` | il y a une page suivante → on la prépare |
| `else: url = None` | plus de page → `while url` s'arrête, on passe à la catégorie suivante |

---

### Cellule 4 — Résultat
```python
df = pd.DataFrame(livres)
print(df.shape)
df.head()
```
`pd.DataFrame(liste_de_dicts)` : chaque dictionnaire devient une **ligne**, ses clés
deviennent les **colonnes**. → **(1000, 4)**.

---

### 💡 Variante « canonique » avec `urljoin` (notebook du checkpoint)
Dans `Checkpoint_3_Data_Analyst.ipynb`, on utilise `urljoin` qui évite de gérer le
dossier à la main, et un **dict en compréhension** pour les catégories :
```python
categories = {a.text.strip(): urljoin(lien_du_site, a["href"])
              for a in soup.select("div.side_categories ul li ul li a")}
...
url = urljoin(url, suivant["href"]) if suivant else None
```
Même logique, juste plus condensé. `urljoin` est plus **robuste** (gère les liens
relatifs complexes) ; la concaténation est plus **explicite** pour comprendre.

---

## 2.7 Les 3 missions dans une seule cellule (version finale)

> Version de `Untitled.ipynb`. Chaque mission **enrichit** le DataFrame de la
> précédente au lieu de tout re-scraper. On relie les missions par une **clé unique**
> `id_livre`. Résultat final : **(1000, 6)**.

### L'idée générale
| Mission | Ajoute | Comment |
|---|---|---|
| 1 | `titre`, `prix_euros` (+ clé) | scrape les 50 pages du catalogue |
| 2 | `categorie`, `en_stock` | scrape les catégories, puis `merge` |
| 3 | `description`, `nb_stock` | visite les 1000 fiches, puis `merge` |

Pourquoi une **clé** ? Parce que les missions parcourent le site dans un **ordre
différent** (catalogue vs catégories). Pour rattacher les bonnes infos au bon livre,
on a besoin d'un identifiant commun. Le titre **ne convient pas** (un doublon existe :
« The Star-Touched Queen »). On utilise donc l'**identifiant de l'URL** de la fiche,
ex. `its-only-the-himalayas_981`.

---

### Bloc 0 — Imports et constantes
```python
import pandas as pd
import requests
from bs4 import BeautifulSoup

URL_SITE = "https://books.toscrape.com/"
TAUX_GBP_EUR = 1.17  # taux approximatif livre -> euro
```
| Ligne | Rôle |
|---|---|
| `import pandas as pd` | manipuler des tableaux (DataFrame) |
| `import requests` | télécharger les pages web |
| `from bs4 import BeautifulSoup` | analyser le HTML |
| `URL_SITE = ...` | l'adresse de base, réutilisée partout |
| `TAUX_GBP_EUR = 1.17` | constante pour convertir les prix £ → € |

---

### Bloc 1 — Mission 1 (DataFrame de base)
```python
ids, titres, prix = [], [], []

for page in range(1, 51):
    url = f"https://books.toscrape.com/catalogue/page-{page}.html"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for bloc in soup.select("article.product_pod"):
        ids.append(bloc.h3.a["href"].split("/")[-2])          # clé unique
        titres.append(bloc.h3.a["title"])
        prix_texte = bloc.select_one("p.price_color").text
        prix.append(round(float(prix_texte.replace("£", "")) * TAUX_GBP_EUR, 2))

df = pd.DataFrame({"id_livre": ids, "titre": titres, "prix_euros": prix})
```

| Ligne | Explication détaillée |
|---|---|
| `ids, titres, prix = [], [], []` | crée **3 listes vides** d'un coup (affectation multiple) qu'on va remplir |
| `for page in range(1, 51):` | boucle sur les pages **1 à 50** (51 exclu) |
| `url = f"...page-{page}.html"` | f-string : insère le n° de page dans l'URL |
| `requests.get(url).content` | télécharge la page → HTML brut (octets) |
| `BeautifulSoup(..., "html.parser")` | transforme le HTML en objet fouillable `soup` |
| `for bloc in soup.select("article.product_pod"):` | parcourt les **20 livres** de la page (voir [2.4](#24-comment-trouver-les-bons-sélecteurs-)) |
| `bloc.h3.a["href"]` | l'URL de la fiche, ex. `"its-only-the-himalayas_981/index.html"` |
| `.split("/")[-2]` | coupe sur `/` → `["its-...-981", "index.html"]`, `[-2]` = **avant-dernier** = la clé |
| `bloc.h3.a["title"]` | l'attribut `title` = le **titre complet** (le texte visible est tronqué) |
| `bloc.select_one("p.price_color").text` | le prix en texte, ex. `"£51.77"` (voir [2.5](#25-le-text--passer-du-html-au-texte-python)) |
| `prix_texte.replace("£", "")` | enlève le `£` → `"51.77"` |
| `float(...)` | convertit la chaîne en **nombre** `51.77` |
| `... * TAUX_GBP_EUR` | conversion en euros |
| `round(..., 2)` | arrondit à 2 décimales (centimes) |
| `pd.DataFrame({...})` | construit le tableau : 3 colonnes alignées → **(1000, 3)** |

> 🔑 **`.split("/")[-2]`** : un index négatif compte **depuis la fin**. `[-1]` = dernier
> élément (`index.html`), `[-2]` = avant-dernier (la clé). C'est plus robuste que `[0]`.

---

### Bloc 2 — Mission 2 (ajout catégorie + stock)
```python
soup = BeautifulSoup(requests.get(URL_SITE).content, "html.parser")
categories = {a.text.strip(): URL_SITE + a["href"]
              for a in soup.select("div.side_categories ul li ul li a")}

infos = []
for nom, url_categorie in categories.items():
    dossier = url_categorie.replace("index.html", "")
    url = url_categorie
    while url:
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        for bloc in soup.select("article.product_pod"):
            dispo = bloc.select_one("p.instock.availability").text
            infos.append({
                "id_livre": bloc.h3.a["href"].split("/")[-2],   # même clé
                "categorie": nom,
                "en_stock": "in stock" in dispo.lower(),
            })
        suivant = soup.select_one("li.next a")
        url = dossier + suivant["href"] if suivant else None

df = df.merge(pd.DataFrame(infos), on="id_livre")   # AJOUT des 2 colonnes
```

| Ligne | Explication détaillée |
|---|---|
| `soup = ...requests.get(URL_SITE)...` | télécharge la page d'accueil (pour lire le menu) |
| `{a.text.strip(): URL_SITE + a["href"] for a in ...}` | **dict en compréhension** : pour chaque lien `a`, crée une paire `nom: url` |
| `a.text.strip()` | le nom de la catégorie, sans espaces autour |
| `URL_SITE + a["href"]` | URL complète par **concaténation** (href relatif + base) |
| `soup.select("div.side_categories ul li ul li a")` | les 50 liens de catégorie (le double `ul li` saute « Books », voir [2.6](#26-mission-2--ajouter-la-catégorie-et-le-stock)) |
| `for nom, url_categorie in categories.items():` | parcourt le dict : récupère **clé + valeur** ensemble |
| `dossier = url_categorie.replace("index.html", "")` | le **dossier** de la catégorie (pour reconstruire les pages suivantes) |
| `url = url_categorie` | on démarre sur la 1re page de la catégorie |
| `while url:` | continue **tant que** `url` n'est pas `None` (gère la pagination) |
| `dispo = ...instock.availability...text` | le texte de dispo, ex. `"  In stock  "` |
| `infos.append({...})` | range un **dictionnaire par livre** (clé + catégorie + stock) |
| `"in stock" in dispo.lower()` | `True`/`False` : « in stock » est-il présent ? (`.lower()` = insensible à la casse) |
| `suivant = soup.select_one("li.next a")` | cherche le bouton « next » (`None` si absent) |
| `url = dossier + suivant["href"] if suivant else None` | s'il existe → URL de la page suivante, sinon `None` (stoppe le `while`) |
| `df.merge(pd.DataFrame(infos), on="id_livre")` | **l'ajout** : colle `categorie` + `en_stock` sur `df` via la clé |

> 🔑 **`df.merge(autre_df, on="id_livre")`** = un JOIN SQL. Pour chaque ligne de `df`,
> pandas trouve la ligne de `autre_df` ayant le **même `id_livre`** et accole ses
> colonnes. C'est ça qui évite de re-scraper titre/prix.
>
> 🔑 **`if ... else ...` sur une ligne** (ternaire) : `A if condition else B` vaut `A`
> si la condition est vraie, sinon `B`. Ici on choisit l'URL suivante ou `None`.

#### 🔎 Zoom sur la pagination (les 2 lignes clés)
```python
suivant = soup.select_one("li.next a")
url = dossier + suivant["href"] if suivant else None
```

**Ligne 1 — trouver le bouton « next ».** Sur le site :
```html
<li class="next"><a href="page-2.html">next</a></li>
```
- `select_one("li.next a")` cherche le `<a>` dans un `<li class="next">`.
- 2 cas : il **renvoie le `Tag`** s'il existe, ou **`None`** sur la dernière page
  (pas de `<li class="next">`). Ce `None` sera le **signal d'arrêt**.

**Ligne 2 — préparer l'URL suivante (ou arrêter).** C'est un **ternaire** :

| Partie | Valeur |
|---|---|
| condition | `suivant` |
| A (si vrai) | `dossier + suivant["href"]` → l'URL de la page suivante |
| B (si faux) | `None` |

- **`if suivant` sans `== None`** : un `Tag` est « vrai », `None` est « faux ` → se lit
  « si on a trouvé un bouton next ».
- ⚠️ **Précédence** : le ternaire a une priorité très faible → Python lit
  `url = (dossier + suivant["href"]) if suivant else None`. Le `dossier + suivant["href"]`
  est donc évalué **comme un bloc**, et **seulement** si `suivant` est vrai (pas de
  plantage `None["href"]`).

**Lien avec le `while url:`** : tant qu'il y a un next → `url` reçoit la page suivante →
le `while` continue. À la dernière page → `suivant = None` → `url = None` → `while url:`
devient faux → on arrête et on passe à la catégorie suivante.

> 🔑 Pattern « tant qu'il y a un suivant » : on utilise `url = None` comme **drapeau de
> fin** de boucle.

---

### Bloc 3 — Mission 3 (ajout description + nb en stock)
```python
cles, descriptions, nb_stocks = [], [], []

for numero, id_livre in enumerate(df["id_livre"]):
    url = f"https://books.toscrape.com/catalogue/{id_livre}/index.html"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    # nombre en stock : "In stock (22 available)" -> 22
    dispo = soup.select_one("p.instock.availability").text
    nb_stocks.append(int(dispo.split("(")[1].split(" ")[0]) if "(" in dispo else 0)

    # description : paragraphe juste après le titre "Product Description" (parfois absent)
    bloc_desc = soup.select_one("#product_description ~ p")
    descriptions.append(bloc_desc.text.strip() if bloc_desc else "")

    cles.append(id_livre)

    if numero % 100 == 0:
        print(numero, "livres traités...")

df_details = pd.DataFrame({"id_livre": cles, "description": descriptions, "nb_stock": nb_stocks})
df = df.merge(df_details, on="id_livre")   # AJOUT des 2 colonnes
```

> ⚠️ Description et nombre exact en stock ne sont **que** sur la **fiche** de chaque
> livre → il faut visiter les 1000 fiches une par une (~8 min, c'est normal).

| Ligne | Explication détaillée |
|---|---|
| `cles, descriptions, nb_stocks = [], [], []` | 3 listes vides à remplir |
| `for numero, id_livre in enumerate(df["id_livre"]):` | parcourt les clés du DataFrame ; `enumerate` ajoute un **compteur** `numero` (0, 1, 2...) |
| `url = f"...catalogue/{id_livre}/index.html"` | reconstruit l'URL de la fiche **à partir de la clé** |
| `requests.get(url)` + `BeautifulSoup(...)` | télécharge et analyse la fiche |
| `dispo = ...instock.availability...text` | texte de dispo, ex. `"In stock (22 available)"` |
| `dispo.split("(")[1]` | coupe sur `(` → prend la 2e partie `"22 available)..."` |
| `.split(" ")[0]` | coupe sur l'espace → prend le 1er morceau `"22"` |
| `int(...)` | convertit `"22"` en nombre `22` |
| `... if "(" in dispo else 0` | sécurité : s'il n'y a pas de `(`, on met `0` (évite un plantage) |
| `bloc_desc = soup.select_one("#product_description ~ p")` | le `<p>` **juste après** l'élément d'id `product_description` |
| `bloc_desc.text.strip() if bloc_desc else ""` | la description nettoyée ; `""` si elle est absente (`bloc_desc` vaut `None`) |
| `cles.append(id_livre)` | mémorise la clé du livre courant |
| `if numero % 100 == 0:` | `%` = reste de division ; vrai tous les 100 → affiche un **suivi** de progression |
| `df_details = pd.DataFrame({...})` | tableau des nouvelles infos + la clé |
| `df = df.merge(df_details, on="id_livre")` | **l'ajout** des colonnes `description` + `nb_stock` |

> 🔑 **Extraction par `split` au lieu d'une regex** : `"In stock (22 available)"`
> → `.split("(")[1]` → `"22 available)"` → `.split(" ")[0]` → `"22"`. On « découpe »
> le texte étape par étape. Plus verbeux qu'une regex, mais très lisible.
>
> 🔑 **Sélecteur `A ~ B`** (« frère général ») : cible un `<p>` situé **après**
> l'élément `#product_description`, au même niveau. `#` = sélecteur d'**id**
> (équivalent de `.` pour les classes).
>
> 🔑 **`enumerate(liste)`** : à chaque tour donne `(indice, élément)`. Sans lui, on
> n'aurait pas le compteur pour le `print` de suivi.

---

### Bloc 4 — Résultat final
```python
df = df.drop(columns="id_livre")   # la clé n'est plus utile à l'affichage
print(df.shape)
df.head()
```
| Ligne | Explication |
|---|---|
| `df.drop(columns="id_livre")` | supprime la colonne clé (elle n'a servi qu'aux `merge`) |
| `print(df.shape)` | affiche les dimensions → `(1000, 6)` |
| `df.head()` | affiche les 5 premières lignes |

**Colonnes finales :** `titre · prix_euros · categorie · en_stock · description · nb_stock`.

---

### 🧠 Récap des concepts clés de la cellule
| Concept | À retenir |
|---|---|
| **Clé `id_livre`** | identifiant unique tiré de l'URL (`split("/")[-2]`) pour relier les missions |
| **Enrichissement** | chaque mission `append` ses dicts puis `merge` → pas de duplication |
| **`merge(on=...)`** | jointure type SQL sur la clé commune |
| **`while url:` + « next »** | boucle de pagination tant qu'il reste une page |
| **`split` en chaîne** | découper du texte sans regex |
| **ternaire `A if c else B`** | choisir une valeur sur une ligne (gère les cas absents) |
| **`enumerate`** | compteur pour le suivi de progression |

> ⚠️ Limite réseau : visiter 1000 fiches une par une est **lent** (~8 min) et peut
> déclencher un **rate-limit** (`ConnectionError`) si on relance trop souvent. Ce
> n'est pas un bug du code → attendre 1-2 min et relancer. La parallélisation
> (concept avancé, à voir plus tard) résout la lenteur.

---

# 3. Géocoding (+ carte Folium)

> But : transformer des **adresses** de restaurants parisiens en **coordonnées GPS**
> (via l'API gratuite de l'IGN `data.geopf.fr`), puis les afficher sur une **carte**.

## 3.1 L'API de géocodage

```python
url = "https://data.geopf.fr/geocodage/search?q=73 Avenue de Paris Saint-Mandé"
requests.get(url).json()
```
On envoie une adresse dans le paramètre `q`, l'API répond en **JSON** (format GeoJSON).
La structure utile :
```
features[0] -> geometry -> coordinates -> [longitude, latitude]
```
> ⚠️ **Piège GeoJSON** : l'ordre est `[longitude, latitude]` (lon **d'abord**),
> alors que Folium attend `[latitude, longitude]` (lat d'abord). Ordre inversé !

## 3.2 La fonction de récupération

```python
def recuperationLongEtLat(url):
  try:
    data = requests.get(url).json()
    longitude = data["features"][0]["geometry"]["coordinates"][1]
    latitude = data["features"][0]["geometry"]["coordinates"][0]
    return longitude, latitude
  except:
    print("L'url n'a pas marché")
```

| Ligne | Explication |
|---|---|
| `try:` | tente la récupération ; si quoi que ce soit échoue → `except` |
| `requests.get(url).json()` | télécharge **et** parse la réponse JSON en dictionnaire Python |
| `data["features"][0]` | le 1er (= meilleur) résultat de l'API |
| `["geometry"]["coordinates"]` | la liste `[lon, lat]` |
| `[1]` / `[0]` | `[1]` = latitude, `[0]` = longitude (ordre GeoJSON) |
| `return longitude, latitude` | renvoie un **tuple** |
| `except:` | en cas d'erreur (adresse introuvable, réseau...) → message, et renvoie `None` |

> ⚠️ **Nommage trompeur** (à savoir) : les variables sont **mal nommées**.
> `coordinates[1]` est la **latitude**, mais elle est rangée dans une variable appelée
> `longitude` (et inversement). Le **contenu** du tuple retourné est donc en réalité
> `(latitude, longitude)`. Ça **fonctionne quand même** car c'est utilisé de façon
> cohérente et que Folium reçoit le bon ordre (voir 3.4) — mais les noms mentent.

## 3.3 La boucle sur toutes les adresses

```python
coordonnees = []
for ligne in range(0, food_paris.shape[0]):
  url = f"https://data.geopf.fr/geocodage/search?q={food_paris.loc[ligne, 'adresse']}&postcode={food_paris.loc[ligne, 'code postal'].split()[0]}"
  coordonnees.append(recuperationLongEtLat(url))

food_paris["coordonnees"] = coordonnees
```

| Ligne | Explication |
|---|---|
| `for ligne in range(0, food_paris.shape[0]):` | parcourt chaque ligne (0 → 28) |
| `food_paris.loc[ligne, 'adresse']` | l'adresse de la ligne courante |
| `...['code postal'].split()[0]` | `"75001 Paris"` → `split()` → `["75001","Paris"]` → `[0]` = `"75001"` |
| `&postcode=...` | ajouter le code postal **affine** le résultat de l'API (bonne pratique) |
| `coordonnees.append(...)` | empile le tuple (ou `None` si échec) |
| `food_paris["coordonnees"] = coordonnees` | ajoute la colonne au DataFrame |

## 3.4 La carte Folium

```python
import folium

carte = folium.Map(location=[48.8566, 2.3522], zoom_start=13)  # centre = Paris

for _, restaurant in food_paris.iterrows():
    coords = restaurant["coordonnees"]
    if coords:  # on saute les adresses non géocodées (None)
        folium.Marker(
            location=[coords[0], coords[1]],  # [latitude, longitude]
            popup=f"{restaurant['nom']} — {restaurant['adresse']}",
            tooltip=restaurant["nom"],
            icon=folium.Icon(color="red", icon="info-sign", prefix="glyphicon"),
        ).add_to(carte)

carte
```

| Ligne | Explication |
|---|---|
| `folium.Map(location=[lat, lon], zoom_start=13)` | crée la carte centrée sur Paris |
| `for _, restaurant in food_paris.iterrows():` | parcourt les lignes ; `_` = on ignore l'index |
| `if coords:` | un tuple est « vrai », `None` est « faux » → on ignore les échecs |
| `location=[coords[0], coords[1]]` | `coords` contient `(lat, lon)` → Folium reçoit bien `[lat, lon]` ✅ |
| `popup=...` | texte au **clic** sur le marqueur |
| `tooltip=...` | texte au **survol** |
| `.add_to(carte)` | ajoute le marqueur à la carte |
| `carte` | afficher la carte (dernière ligne de la cellule) |

### ❓ Le `_` dans `for _, restaurant in food_paris.iterrows()`

`iterrows()` ne renvoie pas que les lignes : à chaque tour il donne un **couple
(tuple)** `(index, ligne)` :
- `index` = l'index de la ligne (0, 1, 2...)
- `ligne` = le contenu de la ligne (une `Series` avec `nom`, `adresse`, `coordonnees`...)

Python **dépaquette** ce couple en deux variables directement dans le `for` (comme
`a, b = (10, 20)`) :
```python
for index, restaurant in food_paris.iterrows():
#   ^^^^^  ^^^^^^^^^^  index  +  la ligne
```

Ici on **n'utilise pas l'index** → par **convention**, on le nomme `_` pour dire
« je reçois cette valeur mais je l'ignore volontairement ».

> 🔑 `_` n'est **pas** un mot-clé magique : c'est une variable normale (`for poubelle,
> restaurant in ...` marcherait pareil). Mais `_` est le **signal universel** entre
> devs : « cette valeur ne m'intéresse pas ». On le retrouve dans `for _ in range(5):`
> (répéter 5 fois sans compteur) ou `valeur, _ = ma_fonction()`.

| Élément | Sens |
|---|---|
| `food_paris.iterrows()` | génère des couples `(index, ligne)` |
| `_, restaurant` | dépaquette le couple en 2 variables |
| `_` | l'index, **volontairement ignoré** |
| `restaurant` | la ligne courante (Series), qu'on exploite |

## 3.5 ✅ Vérification — ce qui est bon / à améliorer
| Aspect | Verdict |
|---|---|
| Appel API + parsing JSON | ✅ correct |
| Affinage avec `&postcode=` | ✅ bonne pratique |
| Gestion des échecs (`try/except` → `None`, puis `if coords`) | ✅ robuste |
| Carte Folium : ordre `[lat, lon]`, popups, marqueurs | ✅ **la carte est juste** |
| Noms `longitude`/`latitude` dans la fonction | ⚠️ **inversés** vs leur contenu (marche par cohérence, mais trompeur) |
| `except:` nu | ⚠️ attrape **tout** (même Ctrl-C) ; mieux : `except Exception:` + dire quelle adresse échoue |

> **En résumé** : le géocodage et la carte **fonctionnent correctement**. Le seul vrai
> point d'attention est le **nommage inversé** lat/lon dans la fonction — à corriger
> pour la lisibilité, même si le résultat est bon.

---

# 4. NLP — Classification de sentiments

> But : prédire si un avis de restaurant est `good` ou `bad` à partir de son texte.
> Données : 10 000 avis (`restaurant.zip`), label dérivé du nombre d'étoiles.

## 4.1 Données et label

```python
df_restaurants = pd.read_csv(".../restaurant.zip", index_col='Unnamed: 0').loc[:, ["date","stars","text","useful"]]
df_restaurants["sentiment"] = df_restaurants["stars"].apply(lambda x: "bad" if x <= 3 else "good")
```
| Ligne | Explication |
|---|---|
| `read_csv(..., index_col='Unnamed: 0')` | charge le CSV, utilise la 1re colonne comme index |
| `.loc[:, [...]]` | ne garde que 4 colonnes utiles |
| `.apply(lambda x: "bad" if x <= 3 else "good")` | crée le **label** : ≤ 3 étoiles → `bad`, sinon `good` |

## 4.2 Nettoyage du texte (2 fonctions)

```python
import nltk
from nltk.corpus import stopwords
import string

# Fonction 1 : ponctuation -> espace, et minuscules
def suppressionPonctuationEtMiseEnMinuscule(phrase):
  listeClean = []
  for caractere in phrase:
    if caractere in string.punctuation:
      listeClean.append(" ")
    else:
      listeClean.append(caractere.lower())
  return "".join(listeClean).replace("  ", " ").strip()

# Fonction 2 : suppression des mots vides (stop words)
def suppressionStopWords(phrase):
  listeClean = []
  for mot in phrase.split(" "):
    if mot not in stopwords.words("english"):
      listeClean.append(mot)
  return " ".join(listeClean).replace("  ", " ")
```

| Élément | Explication |
|---|---|
| `string.punctuation` | la liste des caractères de ponctuation (`!"#$%...`) |
| Fonction 1 | remplace chaque ponctuation par `" "`, met le reste en minuscules |
| `.replace("  "," ").strip()` | réduit les doubles espaces et enlève les bords |
| `stopwords.words("english")` | les « mots vides » anglais (the, is, you...) |
| Fonction 2 | garde uniquement les mots **non** vides |

**Vérifié** : `func2(func1("Hello, how are you? Fine, thank you."))` → `'hello fine thank'` ✅
(exactement la sortie attendue par la consigne).

> ⚠️ **Performance** : `stopwords.words("english")` est appelé **dans la boucle**, à
> chaque mot → mesuré **~6000× plus lent** qu'un `set` précalculé. Sur 10 000 avis,
> c'est des minutes perdues. La variable `stop_words` est définie mais **jamais
> utilisée**. À corriger plus tard : `stop_words = set(stopwords.words("english"))`
> puis `if mot not in stop_words`.
>
> ⚠️ **Consigne** : elle demandait **une seule** fonction `func_clean(str)->str` ;
> ici c'est scindé en deux (fonctionne en les chaînant).

## 4.3 Application + X / y

```python
ma_x_clean_list = []
for i in range(0, df_restaurants.shape[0]):
    ma_x_clean_list.append(suppressionStopWords(suppressionPonctuationEtMiseEnMinuscule(df_restaurants.text[i])))
df_restaurants_x_clean = pd.DataFrame(ma_x_clean_list)
df_restaurants = pd.concat([df_restaurants, df_restaurants_x_clean], axis=1)
df_restaurants = df_restaurants.rename(columns={0: "text_clean"})

X_clean = df_restaurants["text_clean"]
y = df_restaurants.sentiment
```
| Ligne | Explication |
|---|---|
| boucle + `append` | nettoie chaque avis (les 2 fonctions chaînées) |
| `pd.DataFrame(liste)` | transforme la liste en colonne |
| `pd.concat([...], axis=1)` | colle la colonne nettoyée à côté (alignement **par index**) |
| `rename(columns={0: "text_clean"})` | nomme la nouvelle colonne |
| `X_clean` / `y` | features (texte nettoyé) / cible (sentiment) |

> ⚠️ **Fragile** : `df.text[i]` (accès par **label**) + `concat(axis=1)` (alignement par
> index) ne marchent **que parce que l'index est 0..9999**. Plus robuste :
> `df['text'].apply(...)` qui gère l'alignement seul.

## 4.4 Split train / test

```python
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X_clean, y, test_size=0.2, random_state=32)
```
- `test_size=0.2` → 80 % entraînement / 20 % test.
- `random_state=32` → tirage reproductible (imposé par la consigne). ✅

## 4.5 Vectorisation TF-IDF

```python
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer()
X_train_vecto = vectorizer.fit_transform(X_train)   # apprend le vocabulaire SUR LE TRAIN
X_test_vecto  = vectorizer.transform(X_test)        # applique le MÊME vocabulaire au test
```
TF-IDF transforme le **texte en nombres** (poids de chaque mot selon sa rareté).

> 🔑 **`fit_transform` sur train, `transform` sur test** : on apprend le vocabulaire
> **uniquement** sur le train, sinon on triche (fuite de données = *data leakage*).
> ✅ Bien fait ici — c'est le piège classique évité.

## 4.6 Modèles + évaluation

```python
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

logreg = LogisticRegression()
logreg.fit(X_train_vecto, y_train)

arbre = DecisionTreeClassifier()
arbre.fit(X_train_vecto, y_train)
```

### Comparaison train / test (faite dans le notebook)
```python
print("Régression logistique")
print(f"  Train : {logreg.score(X_train_vecto, y_train):.3f}")
print(f"  Test  : {logreg.score(X_test_vecto,  y_test):.3f}")
print("===============================================")
print("Arbre de décision")
print(f"  Train : {arbre.score(X_train_vecto, y_train):.3f}")
print(f"  Test  : {arbre.score(X_test_vecto,  y_test):.3f}")
```

**Résultats obtenus :**

| Modèle | Train | Test | Lecture |
|---|---|---|---|
| Régression logistique | **0.895** | **0.836** | écart faible → **sain**, généralise bien |
| Arbre de décision | **1.000** | **0.699** | écart énorme → **overfitting franc** |

→ La **régression logistique est meilleure**. L'arbre apprend par cœur le train
(100 %) mais s'effondre sur le test (69,9 %). Piste citée dans le notebook : un
`GridSearch` sur les hyper-paramètres de l'arbre pour limiter l'overfitting.

### ⚠️ Erreur rencontrée : `score` sur le texte brut
```python
logreg.score(X_test, y_test)
# ValueError: Expected a 2-dimensional container but got pandas.Series
```
**Cause** : le modèle a été entraîné sur le **vectorisé** (`X_train_vecto`). Il faut
donc l'évaluer sur `X_test_vecto`, **pas** sur `X_test` (qui est du texte 1D).

> 🔑 **Règle d'or** : tout ce qu'on donne au modèle après l'entraînement
> (`score`, `predict`...) doit passer par la **même transformation** que le train
> → toujours `..._vecto`, jamais le texte brut.

### ❌ Reste à faire : la matrice de confusion
La consigne demande aussi une **matrice de confusion** + « combien de "bad" sont bien
prédits ». Pas encore dans le notebook. Pour mémoire :
```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
y_pred = logreg.predict(X_test_vecto)
ConfusionMatrixDisplay(confusion_matrix(y_test, y_pred), display_labels=logreg.classes_).plot()
```

## 4.7 ✅ Vérification — récap NLP
| Aspect | Verdict |
|---|---|
| Données + label (`bad`/`good`) | ✅ |
| Nettoyage (résultat `'hello fine thank'`) | ✅ correct |
| Nettoyage (perf stopwords) | ⚠️ très lent (à corriger plus tard) |
| `func_clean` en 1 seule fonction | ⚠️ scindé en 2 |
| Application + X/y | ⚠️ fonctionne mais fragile (`df.text[i]` + `concat`) |
| `train_test_split` (random_state=32) | ✅ |
| TF-IDF (fit train / transform test) | ✅ bien fait |
| Entraînement des 2 modèles | ✅ |
| Comparaison train/test + diagnostic overfitting | ✅ **fait** (LogReg 0.895/0.836 · Arbre 1.000/0.699) |
| Matrice de confusion + comptage des « bad » | ❌ **manquante** |

---

# 5. JSON — manipulation récursive (optionnel)

> But : extraire **tous** les fruits et légumes d'un dictionnaire **imbriqué à
> profondeur inconnue**, et les ranger dans deux listes, puis dans un dictionnaire propre.

## 5.1 Le problème

```python
food = {
  "clé1": {"fruit1": "pomme", "légume4": "brocoli"},
  "clé2": {"légume1": "carotte", "fruit5": "banane", "légume3": "courgette"},
  "clé3": {"niveau1": {"niveau2": {"fruit3": "orange", "légume5": "aubergine", "fruit5": "mangue"}}},
  "clé4": {"niveau1": {"niveau2": {"niveau3": {"fruit6": "raisin", ...}}}}
}
```
La difficulté : les fruits/légumes sont **enfouis à des profondeurs différentes**
(parfois 1 niveau, parfois 4). On ne peut pas écrire un nombre fixe de boucles `for`
imbriquées → il faut une **fonction récursive**.

## 5.2 La fonction récursive

```python
fruits_list = []
vegetables_list = []

def parcourir(noeud):
    # Parcourt récursivement le dictionnaire et trie fruits / légumes
    for cle, valeur in noeud.items():
        if isinstance(valeur, dict):
            parcourir(valeur)            # sous-dictionnaire -> on descend
        elif "fruit" in cle:
            fruits_list.append(valeur)
        elif "légume" in cle:
            vegetables_list.append(valeur)

parcourir(food)
```

| Ligne | Explication détaillée |
|---|---|
| `fruits_list = []` / `vegetables_list = []` | listes globales remplies pendant le parcours |
| `def parcourir(noeud):` | la fonction prend un dictionnaire (ou sous-dictionnaire) |
| `for cle, valeur in noeud.items():` | parcourt chaque paire **clé → valeur** |
| `if isinstance(valeur, dict):` | la valeur est-elle **encore un dictionnaire** ? |
| `parcourir(valeur)` | **oui → la fonction s'appelle elle-même** sur ce sous-dictionnaire (= on descend d'un niveau) |
| `elif "fruit" in cle:` | sinon, si la **clé** contient le mot `fruit` → c'est un fruit |
| `fruits_list.append(valeur)` | on range la valeur (ex. `"pomme"`) dans les fruits |
| `elif "légume" in cle:` | idem pour les légumes |

> 🔑 **La récursivité** = une fonction qui **s'appelle elle-même**. Ici, chaque fois
> qu'on tombe sur un dictionnaire **dans** le dictionnaire, on relance `parcourir`
> dessus. Elle « descend » donc automatiquement, quel que soit le nombre de niveaux.
> C'est LA bonne réponse quand la profondeur est **inconnue ou variable**.
>
> 🔑 **Les 2 conditions d'une récursion qui se termine** :
> - **cas récursif** : `isinstance(valeur, dict)` → on continue de descendre ;
> - **cas de base** : la valeur n'est **pas** un dict (c'est une chaîne `"pomme"`) →
>   on ne rappelle pas `parcourir`, on range la valeur. Sans ce cas d'arrêt, la
>   fonction tournerait à l'infini.
>
> 🔑 **`isinstance(x, dict)`** : renvoie `True` si `x` est un dictionnaire. C'est le
> test qui distingue « il faut descendre » de « c'est une feuille à ranger ».

### Comment ça se déroule (trace)
```
parcourir(food)
 └─ clé1 -> dict ? oui -> parcourir({fruit1:pomme, légume4:brocoli})
              ├─ fruit1 -> "fruit" dans la clé -> fruits += pomme
              └─ légume4 -> "légume" dans la clé -> légumes += brocoli
 └─ clé3 -> dict ? oui -> parcourir(niveau1)
              └─ niveau2 -> dict ? oui -> parcourir(niveau2)
                            ├─ fruit3 -> fruits += orange ...
```

> 💡 **Astuce de debug** : ajouter un `print(valeur)` au début de la boucle permet de
> **voir** la descente dans la console (très utile pour comprendre une récursion).
> À retirer une fois que ça marche.

## 5.3 Le dictionnaire final

```python
food_dict = {"fruits": fruits_list, "legumes": vegetables_list}
food_dict
```
On range simplement les deux listes sous deux clés. Résultat (conforme à l'attendu) :
```python
{'fruits':  ['pomme', 'banane', 'orange', 'mangue', 'raisin', 'fraise', 'pastèque'],
 'legumes': ['brocoli', 'carotte', 'courgette', 'aubergine', 'poivron']}
```

## 5.4 ✅ Vérification
| Aspect | Verdict |
|---|---|
| Récursion (descente à profondeur variable) | ✅ correcte |
| Cas de base (arrêt sur les feuilles) | ✅ présent |
| Tri fruit/légume via `"... in cle"` | ✅ |
| Résultat == solution attendue | ✅ |
| `print(valeur)` dans la boucle | 💡 trace de debug → à retirer pour la version propre |

---

🎉 **Checkpoint 3 complet** : Regex · Scraping · Géocoding · NLP · JSON.
