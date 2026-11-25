import customtkinter as ctk
from tkinter import filedialog
from exportation import Exportation
from Interface.formulaire import Formulaire
from Interface.resultats import Resultats
from chargeur_donnees import ChargeurDonnees
from risk_calculator import CalculateurRisque
from graphiques import Graphiques
from comparateur_scenarios import ComparateurScenarios

#Classe App, arrange et presente l'interface pratique.
class App (ctk.CTk):
    def __init__(self):
        super().__init__()

        #importation et nettoyage des données
        donnees = ChargeurDonnees("data/export.csv").charger()
        self.donnees = donnees
        self.calculateur = CalculateurRisque(donnees)
        self.graphiques = Graphiques(donnees)
        self.comparateur = ComparateurScenarios(self.calculateur)

        # Scenarios de comparaison
        self.scenario1 = None
        self.dernier_scenario = None

        #condition initiales
        self.title("CartoCrime 2.0")
        self.geometry("1200x700")
        self.minsize(400, 300)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)


        #Création des figures
        graphiques = Graphiques(donnees)
        figures = {
            "Jour × heure": graphiques.carte_chaleur(),
            "Par heure": graphiques.par_heure(),
            "Par secteur": graphiques.par_secteur(),
            "Par lieu": graphiques.par_lieu(),
            "Par âge": graphiques.par_age(),
        }

        #Création des panneau formulaire et résultats
        self.left_panel = Formulaire(self, on_analyser=self.analyser)
        self.right_panel  = Resultats(self, figures)     
        self.left_panel.grid(row=0, column=0, sticky="ns", padx=15, pady=15)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)
        self.bouton_export = ctk.CTkButton(
            self.left_panel, text="Exporter le rapport", state="disabled"
        )
        self.bouton_export.grid(column=0, padx=20, pady=10)

        #Bouton pour memoriser le premier scenario.
        self.bouton_comparaison = ctk.CTkButton(
            self.left_panel,
            text="Mémoriser le scénario 1",
            state="disabled",
            command=self.memoriser_scenario
        )

        self.bouton_comparaison.grid(
            column=0,
            padx=20,
            pady=10
        )

        # Texte inidquant le scenario memoriser.
        self.label_comparaison=ctk.CTkLabel(
            self.left_panel,
            text="Aucun scénario mémorisé",
            font=("Segoe UI", 12),
            wraplength=220
        )

        self.label_comparaison.grid(
            column=0,
            padx=20,
            pady=5
        )



    #fonction d'analyse du scénario
    def analyser(self, scenario):
        try:
            resultat = self.calculateur.calculer_indice(scenario)
            top, source_top = self.calculateur.top_crimes(scenario, avec_source=True)
            figure_top = self.graphiques.top_5(top, source_top)
            figure = self.graphiques.carte_chaleur(scenario)
            self.right_panel.afficher(resultat, top, figure, figure_top)
            self.bouton_export.configure(
                state="normal",
                command=lambda: self.exporter_rapport(scenario, resultat, top)
            )

             # Section pour comparateur
            self.dernier_scenario = scenario.copy()
            self.bouton_comparaison.configure(state="normal")
            
            # Comparer les scenarios si le dernier a ete memoriser.
            # Mon code ne marchait pas donc, j'ai fais des prints pour voir cest ou que ca buggait.
            if self.scenario1 is not None:
                print("Debut de la comparaison")
                comparaison = self.comparateur.comparer(
                    self.scenario1,
                    scenario
                )

                print("Calcul de la comparaison reussi")

                figure_indices = self.graphiques.comparer_indices(
                    comparaison
                )
                print("Graphique des indices créé")

                figure_contributions = None
                if comparaison["contributions"] is not None:
                    figure_contributions = (
                        self.graphiques.graphique_contributions(
                            comparaison["contributions"]
                        )
                    )

                print("Début de l'affichage des graphiques")

                self.right_panel.afficher_comparaison(
                    comparaison,
                    figure_indices,
                    figure_contributions
                )

                print("Affichage terminé")

            

        except ValueError as e:
            print("Erreur :", e)



    def exporter_rapport(self, scenario, resultat, top):
        chemin = filedialog.asksaveasfilename(
            title="Enregistrer le rapport",
            initialfile="rapport_cartocrime.txt",
            defaultextension=".txt",
            filetypes=[("Fichier texte", "*.txt")]
        )
        if chemin:
            Exportation().exporter(chemin, scenario, resultat, top, self.donnees)

    def memoriser_scenario(self):
        if self.scenario1 is None:
            
            if self.dernier_scenario is None:
                return
            # Memoriser une copie du dernier scenario
            self.scenario1 = self.dernier_scenario.copy()

            self.bouton_comparaison.configure(
                text="Effacer le scénario 1"
            )

            self.label_comparaison.configure(
                text=(
                    f"Scénario 1 mémorisé\n"
                    f"{self.scenario1["secteur"]} - "
                    f"{self.scenario1["heure"]} h"
                )
            )

        else:
            self.scenario1 = None

            self.bouton_comparaison.configure(
                text="Mémoriser le scénario 1"
            )

            self.label_comparaison.configure(
                text="Aucun scénario mémorisé"
            )

            self.right_panel.vider_comparaison()

            if self.dernier_scenario is not None:
                self.analyser(self.dernier_scenario)