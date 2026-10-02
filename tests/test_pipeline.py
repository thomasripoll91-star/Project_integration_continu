import os
import sqlite3
import pandas as pd
import pytest
from src.process import add_high_amount_flag, calculate_sums
from src.db import init_db, insert_with_retry

@pytest.fixture
def sample_data():
    """Génère un DataFrame de test prévisible."""
    data = {
        "datetime_transaction": ["2023-10-01", "2023-10-02"],
        "iban_origine": ["FR123", "FR123"],
        "pays_source": ["France", "France"],
        "banque_source": ["BNP", "BNP"],
        "iban_destinataire": ["DE456", "ES789"],
        "pays_destinataire": ["Allemagne", "Espagne"],
        "montant": [1500.0, 6000.0]
    }
    return pd.DataFrame(data)

@pytest.fixture
def test_db():
    """Initialise une base de données temporaire et la supprime à la fin."""
    db_path = "test_pipeline.db"
    init_db(db_path)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)

def test_traitement_flags(sample_data):
    """Vérifie que les flags sont correctement positionnés."""
    df_flagged = add_high_amount_flag(sample_data)
    
    flag_1500 = df_flagged.loc[df_flagged["montant"] == 1500.0, "flag_alerte"].iloc[0]
    flag_6000 = df_flagged.loc[df_flagged["montant"] == 6000.0, "flag_alerte"].iloc[0]
    
    assert flag_1500 == False
    assert flag_6000 == True

def test_traitement_sommes(sample_data):
    """Vérifie que les calculs de sommes produisent les résultats attendus."""
    sums = calculate_sums(sample_data)
    
    assert sums["par_iban_origine"]["FR123"] == 7500.0
    assert sums["par_banque_source"]["BNP"] == 7500.0
    assert sums["par_iban_destinataire"]["DE456"] == 1500.0
    assert sums["par_iban_destinataire"]["ES789"] == 6000.0

def test_insertion_et_deduplication(test_db, sample_data):
    """Vérifie l'insertion en base, les valeurs enregistrées et la prévention des doublons."""
    df_flagged = add_high_amount_flag(sample_data)
    filename = "test_batch.csv"
    
    # 1. Première insertion
    insert_with_retry(test_db, df_flagged, filename)
    
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions")
    assert cursor.fetchone()[0] == 2  # Les deux lignes sont insérées
    
    # 2. Vérification d'une valeur spécifique (le flag enregistré en base)
    cursor.execute("SELECT flag_alerte FROM transactions WHERE montant = 6000.0")
    assert cursor.fetchone()[0] == 1  # SQLite stocke les booléens True comme 1
    
    # 3. Seconde insertion avec le même nom de fichier (doit être ignorée)
    insert_with_retry(test_db, df_flagged, filename)
    
    cursor.execute("SELECT COUNT(*) FROM transactions")
    assert cursor.fetchone()[0] == 2  # Le total reste 2, pas de doublons
    
    conn.close()