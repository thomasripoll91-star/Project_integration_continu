import sqlite3
import time
import pandas as pd

def init_db(db_path="pipeline.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS processed_files (filename TEXT PRIMARY KEY)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                      (datetime_transaction TEXT, iban_origine TEXT, pays_source TEXT,
                       banque_source TEXT, iban_destinataire TEXT, pays_destinataire TEXT,
                       montant REAL, flag_alerte BOOLEAN)''')
    conn.commit()
    conn.close()

def insert_with_retry(db_path: str, df: pd.DataFrame, filename: str, max_retries: int = 3):
    # - définir un nombre maximal de tentatives (max_retries = 3)
    # - effectuer plusieurs tentatives (boucle for)
    for attempt in range(max_retries):
        try:
            # SIMULATION DU PROBLÈME TEMPORAIRE (Échoue à la tentative 0, réussit ensuite)
            if attempt == 0:
                raise sqlite3.OperationalError("Erreur simulée : Base de données temporairement inaccessible")

            conn = sqlite3.connect(db_path, timeout=5)
            cursor = conn.cursor()
            
            # Éviter les doublons
            cursor.execute("SELECT 1 FROM processed_files WHERE filename = ?", (filename,))
            if cursor.fetchone():
                print(f"[{filename}] Fichier déjà traité. Ignoré.")
                conn.close()
                return True

            df.to_sql("transactions", conn, if_exists="append", index=False)
            cursor.execute("INSERT INTO processed_files (filename) VALUES (?)", (filename,))
            
            conn.commit()
            print(f"[{filename}] Insertion réussie à la tentative {attempt + 1}.")
            conn.close()
            return True
            
        # - détecter l’échec
        except sqlite3.Error as e:
            # - afficher clairement les erreurs rencontrées
            print(f"[{filename}] Échec (Tentative {attempt + 1}/{max_retries}) : {e}")
            
            if attempt == max_retries - 1:
                # - arrêter la pipeline si le nombre maximal est dépassé
                print(f"[{filename}] Nombre maximal de tentatives atteint. Arrêt de la pipeline.")
                raise Exception(f"Arrêt critique : impossible d'insérer le fichier {filename}.")
            
            # - attendre avant une nouvelle tentative
            attente = 2 ** attempt  # Attente exponentielle : 1s, 2s...
            print(f"[{filename}] Nouvelle tentative dans {attente} seconde(s)...")
            time.sleep(attente)