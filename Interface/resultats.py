import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

COULEURS = {"faible": "#16a34a", "moyen": "#ca8a04", "élevé": "#dc2626"}


class Resultats(ctk.CTkFrame):
    def __init__(self, master, figures):
        super().__init__(master, corner_radius=15)
        self.grid_columnconfigure(0, weight=1)

        # crée et place la carte de l'indice
        self.carte = ctk.CTkFrame(self, corner_radius=20, fg_color="gray25")
        self.carte.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 15))
        self.carte.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)



        #texte de l'indice sur la carte
        self.indice = ctk.CTkLabel(self.carte, text="—", font=("Segoe UI", 20,), text_color="white")
        self.indice.grid(row=1, column=0, pady=(0, 25))

        #Texte initiale
        self.categorie = ctk.CTkLabel(self.carte, text="Remplissez le scénario à analyser", font=("Segoe UI", 30, "bold"), text_color="white")
        self.categorie.grid(row=0, column=0, pady=(25, 0))


        #Onglets des graphiques
        self.onglets = ctk.CTkTabview(self)
        self.onglets.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))

        self.canvas = {}
        for nom, figure in figures.items():
            self.onglets.add(nom)
            self._placer_figure(nom, figure)

        self.onglets.add("Top 5")

        self.onglets.add("Comparaison")
        self.onglets.add("Contributions")

        self.message_contributions = ctk.CTkLabel(
            self.onglets.tab("Contributions"),
            text="",
            font=("Segoe UI", 16),
            wraplength=600
        )


    #Place les graphiques
    def _placer_figure(self, onglet, figure):
        if onglet in self.canvas:
            self.canvas[onglet].get_tk_widget().destroy()

        canvas = FigureCanvasTkAgg(figure, master=self.onglets.tab(onglet))
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.canvas[onglet] = canvas

        # Rafraichir le graphique apres la mise a jour de l'interface. (La page souvrait, mais pas le graphique)
        canvas.get_tk_widget().after_idle(canvas.draw_idle)


    #affichage de la carte de résultats
    def afficher(self, resultat, top, figure, figure_top):
        couleur = COULEURS.get(resultat.categorie, "gray25")
        self.carte.configure(fg_color=couleur)
        self.categorie.configure(text=f"Risque {resultat.categorie}")
        ecart = round(abs(resultat.indice - 1) * 100)
        if resultat.indice >= 1:
            phrase = f"{ecart} % plus élevé que la moyenne  ({resultat.indice}×)"
        else:
            phrase = f"{ecart} % plus bas que la moyenne  ({resultat.indice}×)"

        self.indice.configure(text=phrase)
        self._placer_figure("Jour × heure", figure)
        self._placer_figure("Top 5", figure_top)
        self.onglets.set("Jour × heure")


    def afficher_comparaison(self, comparaison, figure_indices, figure_contributions):
        self.vider_comparaison()

        indice1 = comparaison["resultat1"].indice
        indice2 = comparaison["resultat2"].indice
        pourcentage = comparaison["difference_pourcentage"]

        self.carte.configure(fg_color="#43464d")

        self.categorie.configure(
            text="Comparaison de scénarios"
        )

        if pourcentage is not None:
            phrase = (
                f"Scénario 1 : {indice1:.2f}  |  "
                f"Scénario 2 : {indice2:.2f}\n"
                f"Variation de l'indice : {pourcentage:+.2f} %"
            )
        else:
            phrase = (
                f"Scénario 1 : {indice1:.2f}  |  "
                f"Scénario 2 : {indice2:.2f}"
            )

        self.indice.configure(text=phrase)

        # Selectionner automatiquement l'onglet de comparaison
        self.onglets.set("Comparaison")

        # Affcher le graphique qui compare.
        self._placer_figure("Comparaison", figure_indices)

        # Affciher les contributions.
        if figure_contributions is not None:
            self._placer_figure("Contributions", figure_contributions)
        else:
            self.message_contributions.configure(
                text=comparaison["erreur_decomposition"]
            )

            self.message_contributions.pack(
                expand=True,
                padx=20,
                pady=20
            )




    def vider_comparaison(self):
        for onglet in ["Comparaison", "Contributions"]:
            if onglet in self.canvas:
                self.canvas[onglet].get_tk_widget().destroy()
                del self.canvas[onglet]

        self.message_contributions.pack_forget()