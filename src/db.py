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
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(db_path, timeout=5)
            cursor = conn.cursor()
            
            # Vérification de déduplication
            cursor.execute("SELECT 1 FROM processed_files WHERE filename = ?", (filename,))
            if cursor.fetchone():
                print(f"[{filename}] Déjà traité. Ignoré.")
                conn.close()
                return True

            # Insertion des données et marquage du fichier
            df.to_sql("transactions", conn, if_exists="append", index=False)
            cursor.execute("INSERT INTO processed_files (filename) VALUES (?)", (filename,))
            
            conn.commit()
            print(f"[{filename}] Insertion en base réussie.")
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"[{filename}] Erreur d'insertion (Tentative {attempt + 1}/{max_retries}) : {e}")
            if attempt == max_retries - 1:
                raise Exception(f"Échec définitif pour {filename} après {max_retries} tentatives.")
            time.sleep(2 ** attempt) 