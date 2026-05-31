# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import io        # Manipuler des fichiers "en mémoire" (les octets du PDF uploadé).
import os        # Lire les variables d'environnement (notre cle API).

import streamlit as st  # Le framework web : tout l'affichage passe par "st.xxx".

# La version installee (mistralai 2.4.8) expose la classe Mistral ici.
# (Le raccourci `from mistralai import Mistral` n'est pas dispo dans cet env.)
from mistralai.client.sdk import Mistral
import numpy as np   # Calcul sur des tableaux de nombres (les vecteurs d'embeddings).
import PyPDF2        # Extraire le texte des pages d'un PDF.
import faiss         # Recherche de vecteurs "les plus proches" (le coeur du RAG).

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
MODEL = "mistral-small-2603"   # Le modele qui REPOND (chat).
EMBED_MODEL = "mistral-embed"  # Le modele qui transforme du texte en vecteur.

# Message "cadre" (system prompt) envoye au modele AVANT la conversation.
# C'est lui qui : (1) force la reponse a s'appuyer sur le document -> evite que
# le modele brode avec ses connaissances generales ; (2) impose une reponse breve.
SYSTEM_PROMPT = (
    "Tu reponds aux questions en t'appuyant UNIQUEMENT sur le contexte du document "
    "fourni dans le message de l'utilisateur. "
    "Si l'information ne figure pas dans ce contexte, dis-le clairement au lieu d'inventer "
    "ou d'ajouter des connaissances exterieures (pas de ressources, livres ou liens non presents "
    "dans le document). "
    "Sois concis : va droit a l'essentiel, sans listes a rallonge ni details superflus."
)

# On lit la cle API dans l'environnement plutot que de l'ecrire en dur dans le code
# (jamais committer une cle). Avant de lancer : export MISTRAL_API_KEY="ta_cle"
mistral_api_key = os.environ.get("MISTRAL_API_KEY")

# Si la cle est absente, on affiche une erreur et on STOPPE l'app immediatement.
# Sans ce garde-fou, l'app planterait plus loin avec un message peu clair.
if not mistral_api_key:
    st.error("Variable d'environnement MISTRAL_API_KEY manquante. "
             "Lance : export MISTRAL_API_KEY=\"ta_cle\" puis relance l'app.")
    st.stop()

# On cree le client Mistral : c'est l'objet qui parle a l'API (chat + embeddings).
cli = Mistral(api_key=mistral_api_key)


# ─────────────────────────────────────────────────────────────────────────────
# OUTIL 1 : transformer un texte en vecteur (embedding)
# ─────────────────────────────────────────────────────────────────────────────
# Un "embedding" = une liste de nombres qui represente le SENS d'un texte.
# Deux textes au sens proche -> deux vecteurs proches. C'est ce qui permet la
# recherche par similarite plus bas.
def get_text_embedding(input: str):
    embeddings_batch_response = cli.embeddings.create(
        model=EMBED_MODEL,
        inputs=input,
    )
    # L'API renvoie une liste de resultats ; on a envoye 1 texte -> on prend [0].
    return embeddings_batch_response.data[0].embedding


# ─────────────────────────────────────────────────────────────────────────────
# OUTIL 2 : le RAG (Retrieval-Augmented Generation)
# ─────────────────────────────────────────────────────────────────────────────
# Objectif : retrouver, dans les PDF, les passages les plus utiles pour repondre
# a la question, et les renvoyer sous forme de texte.
def rag_pdf(pdfs: list, question: str) -> str:
    # 1) DECOUPAGE : on coupe chaque PDF en morceaux ("chunks") de 4096 caracteres.
    #    Pourquoi ? Un PDF entier est trop gros ; on travaille sur des bouts.
    chunk_size = 4096
    chunks = []
    for pdf in pdfs:
        chunks += [pdf[i:i + chunk_size] for i in range(0, len(pdf), chunk_size)]

    # 2) VECTORISATION : on transforme chaque chunk en vecteur, et on empile le
    #    tout dans un tableau numpy (1 ligne = 1 chunk).
    text_embeddings = np.array([get_text_embedding(chunk) for chunk in chunks])

    # 3) INDEX FAISS : on construit un index qui sait chercher les vecteurs proches.
    #    d = la taille d'un vecteur (nombre de colonnes). IndexFlatL2 = distance
    #    euclidienne (L2). On ajoute tous les vecteurs des chunks dans l'index.
    d = text_embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(text_embeddings)

    # 4) RECHERCHE : on vectorise la question, puis on demande a l'index les k=4
    #    chunks les plus proches. search() renvoie les distances (_D, ignorees) et
    #    les indices (I) des chunks trouves.
    question_embeddings = np.array([get_text_embedding(question)])
    _D, I = index.search(question_embeddings, k=4)

    # 5) RECONSTRUCTION : on recupere le texte des chunks trouves (via leurs indices)
    #    et on les colle ensemble pour former le "contexte" a donner au modele.
    retrieved_chunk = [chunks[i] for i in I.tolist()[0]]
    text_retrieved = "\n\n".join(retrieved_chunk)
    return text_retrieved


# ─────────────────────────────────────────────────────────────────────────────
# INTERFACE : titre + memoire de la conversation
# ─────────────────────────────────────────────────────────────────────────────
st.title("Chat with Mistral")

# st.session_state = la "memoire" de Streamlit qui survit aux re-executions.
# (Streamlit relance tout le script a CHAQUE interaction ; sans session_state,
#  l'historique serait perdu a chaque message.)
# On initialise une seule fois : la liste des messages et la liste des PDF.
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.pdfs = []

# A chaque relance du script, on re-affiche tout l'historique des messages
# pour que la conversation reste visible a l'ecran.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ─────────────────────────────────────────────────────────────────────────────
# COEUR : envoyer les messages a Mistral et streamer la reponse
# ─────────────────────────────────────────────────────────────────────────────
# C'est un GENERATEUR (mot-cle `yield`) : il renvoie la reponse morceau par
# morceau, ce qui permet l'affichage "en direct" facon ChatGPT.
def ask_mistral(messages: list, pdfs_bytes: list):
    # On construit une copie LOCALE des messages pour l'envoi a l'API :
    #  - on prefixe avec le SYSTEM_PROMPT (le cadre : grounding + concision) ;
    #  - on copie chaque message (dict(m)) pour ne PAS modifier l'historique
    #    stocke dans st.session_state quand on enrichira la question avec le PDF.
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    api_messages += [dict(m) for m in messages]

    # S'il y a des PDF charges, on enrichit la DERNIERE question de l'utilisateur
    # avec le contexte extrait des PDF (c'est l'etape "Augmented" du RAG).
    if pdfs_bytes:
        pdfs = []
        for pdf in pdfs_bytes:
            reader = PyPDF2.PdfReader(pdf)
            txt = ""
            for page in reader.pages:          # On concatene le texte de chaque page.
                txt += page.extract_text()
            pdfs.append(txt)
        # On retrouve les passages pertinents et on les place clairement comme
        # "contexte", separe de la question, pour que le system prompt s'y applique.
        context = rag_pdf(pdfs, api_messages[-1]["content"])
        api_messages[-1]["content"] = (
            f"Contexte extrait du document :\n{context}\n\n"
            f"Question : {api_messages[-1]['content']}"
        )

    # Appel a l'API en mode streaming : renvoie une suite d'evenements (chunks).
    resp = cli.chat.stream(model=MODEL, messages=api_messages, max_tokens=1024)
    for event in resp:
        # Chaque evenement contient un petit bout de texte dans delta.content.
        # `or ""` evite de planter quand un chunk a un contenu None (fin de flux).
        yield event.data.choices[0].delta.content or ""


# ─────────────────────────────────────────────────────────────────────────────
# ENTREE UTILISATEUR : la barre de chat
# ─────────────────────────────────────────────────────────────────────────────
# st.chat_input renvoie le texte tape (ou None). Le `:=` (walrus) affecte ET teste
# en meme temps : le bloc ne s'execute que si l'utilisateur a ecrit quelque chose.
if prompt := st.chat_input("Talk to Mistral!"):
    # 1) On affiche le message de l'utilisateur...
    with st.chat_message("user"):
        st.markdown(prompt)
    # ...et on l'ajoute a l'historique.
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2) On affiche la reponse de l'assistant en streaming.
    #    st.write_stream consomme le generateur et renvoie le texte complet final.
    with st.chat_message("assistant"):
        response_generator = ask_mistral(st.session_state.messages, st.session_state.pdfs)
        response = st.write_stream(response_generator)

    # 3) On ajoute la reponse complete a l'historique (pour la garder en memoire).
    st.session_state.messages.append({"role": "assistant", "content": response})


# ─────────────────────────────────────────────────────────────────────────────
# UPLOAD DE PDF
# ─────────────────────────────────────────────────────────────────────────────
# Widget pour choisir un fichier PDF. Renvoie None tant que rien n'est charge.
uploaded_file = st.file_uploader("Choose a file", type=["pdf"])
if uploaded_file is not None:
    # On lit les octets du fichier et on les stocke "en memoire" (BytesIO),
    # puis on l'ajoute a la liste des PDF gardee dans la session.
    bytes_io = io.BytesIO(uploaded_file.getvalue())
    st.session_state.pdfs.append(bytes_io)
