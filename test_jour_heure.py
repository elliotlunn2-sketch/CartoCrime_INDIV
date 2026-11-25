
import numpy as np
from chargeur_donnees import ChargeurDonnees

# Presnetement dans mes facteurs j'ai mis le jour et l'heure séparés, mais je peux aussi les combiner en un seul facteur avec 168 modalités (7 jours * 24 heures).
# Je vais comparer les deux approches.

def compter_creneaux(donnees):
    """Compte les incidents pour les 168 créneaux jour-heure."""

    tableau = donnees.groupby(
        ["jour_semaine", "heure"]
    ).size().unstack(fill_value=0)

    tableau = tableau.reindex(
        index=range(7),
        columns=range(24),
        fill_value=0
    ).to_numpy(dtype=float, copy=True)

    # Appliquer la même correction de midi que CartoCrime.
    tableau[:, 12] = (tableau[:, 11] + tableau[:, 13]) / 2

    return tableau


# Charger les données.
donnees = ChargeurDonnees("data/export.csv").charger()

# Séparer les données chronologiquement.
date_limite = donnees["date"].quantile(0.70)

print("Date de séparation :", date_limite.date())

effectifs = []
perte_separee = 0
perte_combinee = 0
total_test = 0
secteurs_ameliores = 0

for secteur, groupe in donnees.groupby("secteur"):

    entrainement = groupe[groupe["date"] <= date_limite]
    test = groupe[groupe["date"] > date_limite]

    if entrainement.empty or test.empty:
        continue

    # Comptes pour les deux périodes.
    comptes = compter_creneaux(entrainement)
    comptes_test = compter_creneaux(test)

    effectifs.extend(comptes.flatten())

    n = comptes.sum()

    # Modèle 1 : jour et heure séparés.
    proba_jour = (comptes.sum(axis=1) + 1) / (n + 7)
    proba_heure = (comptes.sum(axis=0) + 1) / (n + 24)

    proba_separee = proba_jour[:, None] * proba_heure[None, :]

    # Modèle 2 : jour et heure combinés.
    proba_combinee = (comptes + 1) / (n + 168)

    # Évaluer les modèles sur les données de test.
    perte1 = -(comptes_test * np.log(proba_separee)).sum()
    perte2 = -(comptes_test * np.log(proba_combinee)).sum()

    perte_separee += perte1
    perte_combinee += perte2
    total_test += comptes_test.sum()

    if perte2 < perte1:
        secteurs_ameliores += 1


# TEST A : représentativité.
effectifs = np.array(effectifs)

print("\n--- TEST A : REPRÉSENTATIVITÉ ---")
print("Nombre de créneaux :", len(effectifs))
print("Minimum d'incidents :", effectifs.min())
print("Médiane :", np.median(effectifs))

for seuil in [10, 30, 50, 100]:
    pourcentage = (effectifs < seuil).mean() * 100
    print(f"Créneaux avec moins de {seuil} incidents : {pourcentage:.2f} %")


# TEST B : comparaison des modèles.
score1 = perte_separee / total_test
score2 = perte_combinee / total_test

amelioration = (score1 - score2) / score1 * 100

print("\n--- TEST B : COMPARAISON DES MODÈLES ---")
print(f"Modèle séparé : {score1:.5f}")
print(f"Modèle combiné : {score2:.5f}")
print(f"Amélioration : {amelioration:+.3f} %")
print(f"Secteurs améliorés : {secteurs_ameliores} sur 21")


# En conclusion, ce gros test a servi un peu a rien :(.
# Seulement 10/21 des secteurs ont été améliorés par le modèle combiné, et l'amélioration globale est de seulement 0.3%.
# Donc je vais rester avec le modèle séparé pour l'instant.
# Je vais quand meme garder le code du test pour montrer mon travail.