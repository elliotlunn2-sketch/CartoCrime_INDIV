import pandas as pd
from risk_calculator import LIMITES_AGE, NOMS_AGE
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

FOND = "#2b2b2b"
TEXTE = "#dce4ee"
ACCENT = "#3b82f6"
SURLIGNE = "#ef4444"
JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

class Graphiques:
    def __init__(self, donnees):
        self.donnees = donnees

    def par_heure(self):
        nombres = self.donnees["heure"].value_counts()
        nombres = nombres.reindex(range(24), fill_value=0)

        # Corriger le pic de midi pour l'affichage.
        nombres = nombres.astype(float)
        nombres[12] = (nombres[11] + nombres[13]) / 2

        fig = Figure(figsize = (6,3))
        ax = fig.add_subplot()
        ax.bar(nombres.index, nombres.values)
        ax.set_xlabel("Heure")
        ax.set_ylabel("Nombre de crimes rapportés")
        ax.set_title("Nombre de crimes selon l’heure")
        ax.set_xticks(range(24))
        fig.tight_layout()
        return fig
    
    def carte_chaleur(self, scenario=None):
        donnees = self.donnees
        titre = "Crimes rapportés — Tous les secteurs"

        if scenario is not None:
            secteur = scenario["secteur"]
            sexe = scenario["sexe"]
            donnees = donnees[
                (donnees["secteur"] == secteur) & (donnees["sexe"] == sexe)
            ]

            tranche = pd.cut([scenario["age"]], bins=LIMITES_AGE, labels=NOMS_AGE)[0]
            tranches = pd.cut(donnees["age"], bins=LIMITES_AGE, labels=NOMS_AGE)
            donnees = donnees[tranches == tranche]

            groupe = "Hommes" if sexe == "M" else "Femmes"
            titre = f"{secteur} — {groupe}, {tranche} ans"

        comptes = donnees.groupby(["jour_semaine", "heure"]).size()
        tableau = comptes.unstack(fill_value=0).reindex(
            index=range(7), columns=range(24), fill_value=0
        )

        # Remplacer les effectifs de 12 h par la moyenne
        # de 11 h et 13 h pour chaque jour.
        tableau = tableau.astype(float)

        tableau[12] = (tableau[11] + tableau[13]) / 2


        fig = Figure(figsize=(9, 5))
        ax = fig.add_subplot()
        image = ax.imshow(tableau, cmap="YlOrRd", aspect="auto", vmin=0,
                          vmax=max(1, tableau.to_numpy().max()))
        fig.colorbar(image, ax=ax, label="Nombre de crimes rapportés")
        ax.set_xticks(range(24))
        ax.set_yticks(range(7), JOURS)
        ax.set_xlabel("Heure")
        ax.set_ylabel("Jour")

        if scenario is not None:
            jour = scenario["jour_semaine"]
            heure = scenario["heure"]
            cadre = Rectangle((heure - 0.5, jour - 0.5), 1, 1,
                              fill=False, edgecolor="royalblue", linewidth=3)
            ax.add_patch(cadre)

            if heure == 12:
                titre += (f"\n{JOURS[jour]} à 12 h : "f"environ {tableau.loc[jour, heure]:.0f} incidents ""(estimation)")
            else:
                titre += (f"\n{JOURS[jour]} à {heure} h : "f"{int(tableau.loc[jour, heure])} incidents")


        ax.set_title(f"{titre} — {len(donnees)} incident(s) au total (Données brutes)")
        fig.tight_layout()
        return fig
        

    def par_secteur(self):
        nombres = self.donnees["secteur"].value_counts()
        nombres = nombres.sort_values()

        fig = Figure(figsize=(7, 4))
        ax = fig.add_subplot()
        ax.barh(nombres.index, nombres.values)
        ax.set_xlabel("Nombre de crimes rapportés")
        ax.set_ylabel("Secteur")
        ax.set_title("Nombre de crimes par secteur")
        fig.tight_layout()
        return fig
        

    def par_lieu(self):
        nombres = self.donnees["type_lieu"].value_counts().head(10)
        nombres = nombres.sort_values()

        fig = Figure(figsize=(7, 4))
        ax = fig.add_subplot()
        ax.barh(nombres.index, nombres.values)
        ax.set_xlabel("Nombre de crimes rapportés")
        ax.set_ylabel("Type de lieu")
        ax.set_title("Les 10 types de lieux avec le plus de crimes rapportés")
        fig.tight_layout()
        return fig
    
    def par_age(self):
        tranches = pd.cut(
            self.donnees["age"],
            bins=LIMITES_AGE,
            labels=NOMS_AGE
        )
        nombres = tranches.value_counts()
        nombres = nombres.reindex(NOMS_AGE, fill_value=0)

        fig = Figure(figsize=(7, 4))
        ax = fig.add_subplot()
        ax.bar(nombres.index, nombres.values)
        ax.set_xlabel("Tranche d’âge")
        ax.set_ylabel("Nombre de crimes rapportés")
        ax.set_title("Crimes rapportés selon l’âge de la victime")
        fig.tight_layout()
        return fig

# Je créer le graphique du top 5 des crimes les plus rapportés pour le scénario donné.
    def top_5(self, top, source_top):
        from textwrap import fill
        from matplotlib.figure import Figure

        top = top.sort_values()

        # Couleurs
        palette = {
            1: "#3ca0f8",
            2: "#2b87f8",
            3: "#326ed6",
            4: "#445c83",
            5: "#5b6575"
        }

        # Les crimes avec le meme nombre d'incidents auront le meme rang, donc la meme couleur.
        rangs = top.rank(ascending=False, method="min").astype(int)

        couleurs = [palette[rang] for rang in rangs]
            

        fig = Figure(figsize=(10, 5.2), facecolor='#2f3136')
        ax = fig.add_subplot()
        ax.set_facecolor("#43464d")

        # Je limite les noms des crimes à 28 caractères pour éviter que le texte ne déborde.
        noms = [fill(nom, width=28) for nom in top.index]

        barres = ax.barh(noms, top.values, color=couleurs, edgecolor="none")

        # Texte
        ax.set_xlabel(
            "Nombre de crimes rapportés",
            fontsize=15,
            color="white",
            labelpad=10)

        ax.set_ylabel("")
        
        ax.set_title(
            "Top 5 des crimes les plus rapportés",
            fontsize=25,
            color="white",
            fontweight="bold",
            pad=14)

        # Reduire la taille des étiquettes de l'axe y et x pour éviter le chevauchement.
        ax.tick_params(axis="y", labelsize=14, colors="white")
        ax.tick_params(axis="x", labelsize=14, colors="white")

        # Retirer certaines bordures
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("white")
        ax.spines["bottom"].set_color("white")

        # Quadtrllage
        ax.grid(axis="x", linestyle="--", alpha=0.15, color="white")
        ax.set_axisbelow(True)

        # AFficher les valeurs sur les barres
        max_val = max(top.values)
        for barre,valeur in zip(barres, top.values):
            ax.text(
                valeur + max_val * 0.02,
                barre.get_y() + barre.get_height() / 2,
                str(valeur),
                va="center",
                ha="left",
                color="white",
                fontsize=15,
                fontweight="bold"
            )

        # Ajuster les limites pour laisser de l'espace pour les étiquettes
        ax.set_xlim(0, max_val * 1.15)

        # Ajouter la source du top 5
        fig.text(
            0.5,
            0.04,
            f"Données utilisées pour le top 5 : {source_top}",
            ha="center",
            fontsize=11,
            color="white"
        )

        # Ajuster les marges.
        fig.subplots_adjust(
            left=0.21,
            right=0.95,
            top=0.88,
            bottom=0.20)

        return fig

# Graphique comparant les indices de risque de deux scénarios.
    def comparer_indices(self, comparaison):
        indice1 = comparaison["resultat1"].indice
        indice2 = comparaison["resultat2"].indice

        indices = [indice1, indice2]
        noms = ["Scénario 1", "Scénario 2"]

        # Couleurs des deux scenarios
        if indice1 > indice2:
            couleurs = ["#ef4444", "#22c55e"]
        elif indice2 > indice1:
            couleurs = ["#22c55e", "#ef4444"]
        else:
            couleurs = ["#2b87f8", "#2b87f8"]

        fig = Figure(figsize=(9, 5), facecolor='#2f3136')
        ax = fig.add_subplot()
        ax.set_facecolor("#43464d")

        # Creer les deux barres.
        barres = ax.bar(noms, indices, color=couleurs, width=0.5)

        #ligne de reference.
        ax.axhline(
            y=1,
            color="#e5e7eb",
            linestyle="--",
            linewidth=1.5,
            label="Indice de référence (1.00)")

        ax.set_title(
            "Comparaison des indices de risque",
            fontsize=26,
            color="white",
            fontweight="bold",
            pad=15)

        ax.set_ylabel("Indice de risque relatif", fontsize=18, color="white", labelpad=15)
        ax.tick_params(axis="both", labelsize=13, colors="white")

        # Afficher les valeurs par dessus chaque barre.
        for barre, valeur in zip(barres, indices):
            ax.text(
                barre.get_x() + barre.get_width() / 2,
                valeur + 0.02,
                f"{valeur:.2f}",
                ha="center",
                va="bottom",
                fontsize=18,
                fontweight="bold",
                color="white"
                )

        ax.set_ylim(0, max(1, max(indices)) * 1.25)

        # Grille
        ax.grid(axis="y", linestyle="--", alpha=0.15, color="white")
        ax.set_axisbelow(True)

        # Retirer les bordures.
        for bordure in ax.spines.values():
            bordure.set_visible(False)

        ax.legend(
            facecolor="#43464d",
            edgecolor="none",
            labelcolor="white"
        )

        fig.subplots_adjust(
            left=0.10,
            right=0.95,
            top=0.85,
            bottom=0.10
        )

        return fig


    # Affiche les contributions des facteurs a la difference.
    def graphique_contributions(self, contributions):
        if contributions is None:
            raise ValueError("Les contributions sont indisponibles.")

        # Meilleurs noms pour l'affichage.
        noms_facteurs = {
            "secteur": "Secteur",
            "jour_semaine": "Jour",
            "heure": "Heure",
            "tranche_age": "Tranche d'âge",
            "sexe": "Sexe",
        }

        facteurs = list(contributions.keys())
        valeurs = list(contributions.values())

        noms = [noms_facteurs.get(f, f) for f in facteurs]

        # Bleu = augmente, rouge = diminution.
        couleurs = []
        for valeur in valeurs:
            if valeur > 0:
                couleurs.append("#16a34a")
            elif valeur < 0:
                couleurs.append("#dc2626")
            else:
                couleurs.append("#64748b")

        fig = Figure(figsize=(9, 5), facecolor="#2f3136")
        ax = fig.add_subplot()
        ax.set_facecolor("#43464d")

        barres = ax.barh(noms, valeurs, color=couleurs, height=0.6)

        # Mettre un ligne a zero.
        ax.axvline(0, color="white", linewidth=1.2)

        # Met facteur le plus important en haut.
        ax.invert_yaxis()

        ax.set_title(
            "Contribution des facteurs",
            fontsize=25,
            color="white",
            fontweight="bold",
            pad=15
        )

        ax.set_xlabel(
            "Contribution logarithmique (×100)",
            fontsize=16,
            color="white",
            labelpad=15
        )

        ax.tick_params(axis="x", labelsize=14, colors="white")
        ax.tick_params(axis="y", labelsize=18, colors="white")

        # On fait de l'espace pour les valeurs.
        max_val = max(1, max(abs(v) for v in valeurs))
        ax.set_xlim(-max_val * 1.3, max_val * 1.3)

        # Afficher les contributions au bout des barres.
        for barre, valeur in zip(barres, valeurs):
            if valeur >= 0:
                position_x = valeur + max_val * 0.03
                alignement = "left"
            else:
                position_x = valeur - max_val * 0.03
                alignement = "right"

            ax.text(
                position_x,
                barre.get_y() + barre.get_height() / 2,
                f"{valeur:+.2f}",
                ha=alignement,
                va="center",
                fontsize=14,
                fontweight="bold",
                color="white"
                )

        ax.grid(axis="x", linestyle="--", alpha=0.15, color="white")
        ax.set_axisbelow(True)

        for bordure in ax.spines.values():
            bordure.set_visible(False)

        fig.subplots_adjust(
                    left=0.12,
                    right=0.95,
                    top=0.85,
                    bottom=0.15
                )

        return fig