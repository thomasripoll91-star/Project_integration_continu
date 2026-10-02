import csv

def load_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

def apply_business_rules(transactions):
    processed = []
    for t in transactions:
        # Copie du dictionnaire pour respecter la contrainte de fonction pure
        new_t = t.copy()
        try:
            # Tentative de conversion en nombre décimal
            new_t["montant"] = float(new_t["montant"])
            # Ajout du flag
            new_t["flag_high_amount"] = True if new_t["montant"] > 5000 else False
            processed.append(new_t)
        except ValueError:
            # Si le montant est invalide (ex: "INVALID_MONTANT"), on ignore la ligne
            print(f"[Alerte Data Quality] Montant invalide ignoré : {new_t.get('montant')}")
            continue
    return processed

def aggregate_data(transactions):
    agg = {
        "sum_by_iban_origine": {},
        "sum_by_banque_source": {},
        "sum_by_iban_destinataire": {}
    }
    
    for t in transactions:
        m = float(t["montant"])
        
        orig = t["iban_origine"]
        agg["sum_by_iban_origine"][orig] = agg["sum_by_iban_origine"].get(orig, 0) + m
        
        bank = t["banque_source"]
        agg["sum_by_banque_source"][bank] = agg["sum_by_banque_source"].get(bank, 0) + m
        
        dest = t["iban_destinataire"]
        agg["sum_by_iban_destinataire"][dest] = agg["sum_by_iban_destinataire"].get(dest, 0) + m
        
    return agg