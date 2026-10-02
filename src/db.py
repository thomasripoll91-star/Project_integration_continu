import sqlite3
import time
import hashlib

DB_PATH = "pipeline.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime_transaction TEXT,
            iban_origine TEXT,
            banque_source TEXT,
            iban_destinataire TEXT,
            montant REAL,
            flag_high_amount BOOLEAN
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_files (
            file_hash TEXT PRIMARY KEY,
            filename TEXT,
            processed_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def compute_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def is_file_processed(file_hash):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_files WHERE file_hash = ?", (file_hash,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def insert_transactions_with_retry(transactions, file_path, max_retries=3, simulate_fail=False):
    file_hash = compute_file_hash(file_path)
    if is_file_processed(file_hash):
        print(f"Fichier ignoré {file_path}: Déjà traité.")
        return

    attempt = 0
    while attempt < max_retries:
        try:
            if simulate_fail and attempt == 0:
                raise sqlite3.OperationalError("Database is locked (Simulated temporary failure)")

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            for t in transactions:
                cursor.execute('''
                    INSERT INTO transactions 
                    (datetime_transaction, iban_origine, banque_source, iban_destinataire, montant, flag_high_amount)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (t["datetime_transaction"], t["iban_origine"], t["banque_source"], t["iban_destinataire"], t["montant"], t["flag_high_amount"]))
            
            cursor.execute("INSERT INTO processed_files (file_hash, filename, processed_at) VALUES (?, ?, ?)", 
                           (file_hash, file_path, time.strftime('%Y-%m-%dT%H:%M:%S')))
            conn.commit()
            conn.close()
            print(f"Données insérées avec succès depuis {file_path}")
            return

        except sqlite3.OperationalError as e:
            attempt += 1
            print(f"Tentative {attempt}/{max_retries} échouée : {e}")
            if attempt >= max_retries:
                print("Nombre maximum de tentatives atteint. Arrêt du pipeline.")
                raise e
            print("Nouvelle tentative dans 2 secondes...")
            time.sleep(2)