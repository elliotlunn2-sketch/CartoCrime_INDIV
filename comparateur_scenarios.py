from math import log

# On compare les indices de risque de deux scénarios et on affiche les résultats dans une fenêtre.

class ComparateurScenarios:
    
    def __init__(self, calculateur):
        self.calculateur = calculateur

    def comparer(self, scenario1, scenario2):
        # On calcule les indices de risque pour les deux scénarios
        resultat1 = self.calculateur.calculer_indice(scenario1)
        resultat2 = self.calculateur.calculer_indice(scenario2)

        indice1 = resultat1.indice
        indice2 = resultat2.indice

        # Differnece entre les indices de risque
        difference = round(indice2 - indice1, 2)

        if indice1 != 0:
            difference_pourcentage = round((difference / indice1) * 100, 2)
        else:
            difference_pourcentage = None  # Évite la division par zéro si l'indice du scénario 1 est nul

        # Decomposer la différence entre les facteurs.
        try:
            contributions = self.decomposer_difference(resultat1, resultat2)
            erreur_decomposition = None

        except ValueError as e:
            contributions = None
            erreur_decomposition = str(e)

        return {
            "resultat1": resultat1,
            "resultat2": resultat2,
            "difference": difference,
            "difference_pourcentage": difference_pourcentage,
            "contributions": contributions,
            "erreur_decomposition": erreur_decomposition,
            "scenario1": scenario1.copy(),
            "scenario2": scenario2.copy(),
        }

    def decomposer_difference(self, resultat1, resultat2):
        """Décompose la différence entre deux indices de risque en contributions par facteur."""
        partiels1 = resultat1.partiels_bruts
        partiels2 = resultat2.partiels_bruts

        # Les deux scenarios doivent utiliser les mêmes facteurs pour que la comparaison ait du sens.
        if not partiels1 or not partiels2:
            raise ValueError("Les indices de risque doivent contenir des indices partiels pour la décomposition.")

        if set(partiels1) != set(partiels2):
            raise ValueError("Les deux scénarios doivent avoir les mêmes facteurs pour la décomposition.")

        nb_facteurs = len(partiels1)
        contributions = {}

        for facteur in partiels1:
            indice1 = partiels1[facteur]
            indice2 = partiels2[facteur]

            # Calculer la contribution du facteur avec logarithme pour éviter les problèmes de multiplication de petits nombres.
            contribution = log(indice2 / indice1) / nb_facteurs
            contributions[facteur] = contribution * 100  # Convertir en pourcentage

        # Trier les facteurs
        contributions = dict(sorted(
            contributions.items(),
            key=lambda element: abs(element[1]),
            reverse=True))

        return contributions