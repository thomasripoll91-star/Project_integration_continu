import os
import sqlite3
import pytest
from src.db import init_db, DB_PATH
from src.process import apply_business_rules, aggregate_data
from main import run_pipeline

@pytest.fixture(autouse=True)
def setup_teardown():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_processing_functions():
    # Test des fonctions pures isolées
    raw_data = [
        {"iban_origine": "FR1", "banque_source": "BNP", "iban_destinataire": "DE1", "montant": "6000"},
        {"iban_origine": "FR1", "banque_source": "BNP", "iban_destinataire": "DE2", "montant": "1000"},
        {"iban_origine": "FR2", "banque_source": "SG", "iban_destinataire": "DE1", "montant": "INVALID_MONTANT"}
    ]
    
    processed = apply_business_rules(raw_data)
    
    # La ligne invalide doit être ignorée, il ne reste que 2 transactions
    assert len(processed) == 2
    assert processed[0]["flag_high_amount"] is True
    assert processed[1]["flag_high_amount"] is False
    
    agg = aggregate_data(processed)
    assert agg["sum_by_iban_origine"]["FR1"] == 7000.0

def test_pipeline_integration():
    # Test complet de la pipeline de bout en bout
    run_pipeline(simulate_fail=False)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 8 enregistrements générés au total - 1 ligne invalide ignorée = 7 insertions
    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    assert count == 7, "7 transactions valides doivent être insérées dans la base"
    
    cursor.execute("SELECT montant, flag_high_amount FROM transactions WHERE montant > 5000")
    high_amounts = cursor.fetchall()
    for row in high_amounts:
        assert row[1] == 1, "Le flag_high_amount doit être True (1) pour les montants > 5000"
        
    conn.close()