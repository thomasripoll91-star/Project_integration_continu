import pandas as pd

def load_csv(filepath: str) -> pd.DataFrame:
    return pd.read_csv(filepath)

def add_high_amount_flag(df: pd.DataFrame) -> pd.DataFrame:
    # Création d'une copie pour garantir la pureté de la fonction
    df_out = df.copy()
    df_out["flag_alerte"] = df_out["montant"] > 5000
    return df_out

def calculate_sums(df: pd.DataFrame) -> dict:
    # Retourne un nouveau dictionnaire sans modifier l'entrée
    return {
        "par_iban_origine": df.groupby("iban_origine")["montant"].sum().to_dict(),
        "par_banque_source": df.groupby("banque_source")["montant"].sum().to_dict(),
        "par_iban_destinataire": df.groupby("iban_destinataire")["montant"].sum().to_dict(),
    }