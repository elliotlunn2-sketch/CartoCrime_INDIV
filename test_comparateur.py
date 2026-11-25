from chargeur_donnees import ChargeurDonnees
from risk_calculator import CalculateurRisque
from comparateur_scenarios import ComparateurScenarios

#Charger les dpnnées et créer le calculateur de risque
donnees = ChargeurDonnees("data/export.csv").charger()
calculateur = CalculateurRisque(donnees)

# Créer le comparateur de scénarios
comparateur = ComparateurScenarios(calculateur)

# Scenarios:
scenario1 = {
    "secteur": "Hollywood",
    "jour_semaine": 5,
    "heure": 9,
    "sexe": "M",
    "age": 25,
}

scenario2 = {
    "secteur": "Pacific",
    "jour_semaine": 5,
    "heure": 23,
    "sexe": "M",
    "age": 25,
}

comparaison = comparateur.comparer(scenario1, scenario2)

print("Scenario 1:", comparaison["resultat1"].indice)
print("Scenario 2:", comparaison["resultat2"].indice)
print("Difference:", comparaison["difference"])
print("Différence relative :", comparaison["difference_pourcentage"], "%")

if comparaison["difference"] > 0:
    print("Le scénario 2 présente un risque plus élevé que le scénario 1.")
elif comparaison["difference"] < 0:
    print("Le scénario 1 présente un risque plus élevé que le scénario 2.")
else:
    print("Les deux scénarios présentent le même niveau de risque.")


# Tester la decomposition des facteurs.
from math import exp

contributions = comparaison["contributions"]

if contributions is None:
    print("Erreur lors de la décomposition des facteurs :", comparaison["erreur_decomposition"])

else:
    print("\nContributions des facteurs:")

    for facteur, contribution in contributions.items():
        print(f"  {facteur}: {contribution:.2f} %")

# Verifier si les contributions reconstruisent la difference relative entres les indices.

total = sum(contributions.values())
variation = (exp(total / 100) - 1) * 100  # Convertir le total en pourcentage de variation

print(f"\nTotal des contributions : {total:.2f} %")
print(f"Variation reconstruite à partir des contributions : {variation:.2f} %")