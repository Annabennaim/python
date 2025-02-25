#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 14:53:04 2024

@author: chloemarangon
"""

#PROJET C : Création d'un simulateur de carnet d'ordres__
#Marangon_Chloe   Kerautret_Gurvan   Bennaim_Anna (projet à 3 personnes)

#Dans ce projet, nous avons mis en place un carnet d'ordres en partant d'un produit financier quelconque, échangeable sur un marché financier de manière générale. Nous avons implémenté plusieurs méthodes de classe afin de différencier les takers, makers, acheteurs et vendeurs. Puis nous avons mis en place un exemple concret avec l'intervention de plusieurs traders afin de tester le fonctionnement de ce carnet d’ordres continu.

#Enfin, nous avons implémenté une méthode de fixing afin de calculer le prix de fixing comme cela se fait avant et après la fermeture des marchés financiers europééens.

#Importation des packages
from datetime import datetime
import pandas as pd
import warnings
warnings.filterwarnings("ignore", message="The behavior of DataFrame concatenation with empty or all-NA entries is deprecated") #messagd d'erreur


#PARTIE 1 : Nous definissons la classe Ordre permettant l'ajout ou l'annulation d'ordres par participant.
class Ordre:
#initialisation des différents paramètres nécessaires pour construire le carnet d’ordre
    def __init__(self, tick_size, lot_size):
    # Initialisation des paramètres de contrôle du tick et du lot
        self.tick_size = tick_size
        self.lot_size = lot_size
       	# Creation d'un carnet d'ordres à l'achat et un à la vente  ; division du carnet d’ordre en deux parties pour distinguer les ordres d’achat et de vente
        self.ordre_achat = pd.DataFrame(columns=['prix', 'position', 'quantite', 'ref', 'horaire', 'role', 'participant'])
        self.ordre_vente = pd.DataFrame(columns=['prix', 'position', 'quantite', 'ref', 'horaire', 'role', 'participant'])


    #méthode pour vérifier si l'ordre entré verifie les contraintes de tick et lot.
    def _valider_ordre(self, prix, quantite):
    # Validation de la taille du tick et du lot selon les règles de marché 
        
        epsilon = 0.01  #on cree un epsilon pour les erreus d'arrondi
        #on vérifie que le prix de l'ordre est un multiple du tick et que la quantité est un multiple est un multiple du lot.
        if not (prix % self.tick_size < 0.01 and quantite % self.lot_size < 0.01):
            print(f"\n\n {quantite % self.lot_size}\n\n")  
            raise ValueError("Le prix et la quantité de l'ordre doivent respecter les contraintes de tick et de lot des marchés.")

#Chaque participant a 3 options : ajouter un ordre d’achat, ajouter un ordre de vente ou supprimer un ordre. Donc définissons donc 3 méthodes principales propres à cette classe.

#définition de la fonction d’ajout d’un ordre d'achat.
    def ajout_ordre_achat(self, prix, position, quantite, horaire, role, participant):
        #on stocke les informations données par le participant dans un dictionnaire pour faciliter le stockage des données. Un ordre émis doit comporter la quantité, le prix, le type de position: achat ou vente, la reference de l'ordre, le role: taker ou maker.
        # On fait appel à la méthode afin de vérifier si l'ordre entré vérifie les contraintes de tick et de lot.
        self._valider_ordre(prix, quantite)
   		# Vérification si le participant est un maker ou un taker
        if role not in ["maker", "taker"]:  
       		print(f"Erreur : {participant} n'est pas autorisé à ajouter un ordre d'achat.")
        	return
        #Sinon, on enregistre les informations comme un nouvel ordre.
        new_order = {'prix': prix,'position': position, 'quantite': quantite, 'ref': f"{participant}_{quantite}_{horaire}_{prix}_{position}_{role}", 'horaire': horaire,'role': role, 'participant': participant}
#Un participant est soit maker, soit taker
#Si il est maker, il va placer un ordre dans le carnet qui ne s’executera que lorsqu'un taker sera preneur de son ordre.
        if role == "maker":
            self.ordre_achat = pd.concat([self.ordre_achat, pd.DataFrame([new_order])], ignore_index=True)
     		#On place l’ordre dans le carnet existant et on trie ensuite le carnet pour que les ordre soient triées par ordre de prix puis de temps dans un second temps si les prix sont égaux
            self.ordre_achat.sort_values(by=['prix', 'horaire'], ascending=[False, True], inplace=True)
        elif role == "taker":      
            #Si il est taker, il va acheter au prix de marché
            self._executer_ordre_taker(new_order, 'achat')
        
        
#On implemente maintenant une fonction dans le cas où l'agent voudrait ajouter un ordre cette fois ci à la vente.
#même logique que dans notre fonction ajout_ordre_achat mais pour un ordre de vente
    def ajout_ordre_vente(self, prix, position, quantite, horaire, role, participant):
    #On teste si les caractéristiques entrées vérifient les contraintes de tick et de lot des marchés.
        self._valider_ordre(prix, quantite)
  		# Vérification si le participant est un vendeur ou un taker.
        if role not in ["taker", "maker"]:  	
            print(f"Erreur : {participant} n'est pas autorisé à ajouter un ordre de vente.")
            #si le participant n"est pas autorisé à entrer un ordre dans le carnet d'ordres à la vente, on sort de la fonction.
            return
    	#si le participant est autorisé à entrer un ordre dans le carnet d'ordres à la vente, on enregistre les informations de l'ordre dans new_order. 
        new_order = {
      		'prix': prix,
       		'position': position, 
        	'quantite': quantite,
        	'ref': f"{participant}_{quantite}_{horaire}_{prix}_{position}_{role}", 
    		'horaire': horaire, 
     		'role': role, 
     		'participant': participant
        }
        if role == "maker":
     	#On ajoute l’ordre de vente à notre carnet de vente.
            self.ordre_vente = pd.concat([self.ordre_vente,pd.DataFrame([new_order])], ignore_index=True)
            #On trie les ordres de vente par tri croissant puisque les ordres à la vente les moins chers interessent le plus d’investisseurs.
            self.ordre_vente.sort_values(by=['prix', 'quantite'], ascending=[True, True], inplace=True)
        else:
       	# Les takers tentent d'exécuter leur ordre immédiatement puisqu'ils sont preneurs de prix.
            self._executer_ordre_taker(new_order, 'vente')
        

    # Fonction définie pour executer un ordre dans le cas où le participant serait taker, c'est à dire preneur de prix. Pas besoin de faire le même type de fonction pour un maker puisque le makeur fixe les prix et attend qu'une contrepartie "matche" son ordre.
    def _executer_ordre_taker(self, ordre_taker, type_ordre):
        ordres_supprimes = []
        carnet_o = self.ordre_achat if type_ordre == 'vente' else self.ordre_vente
        # Tri du carnet d'ordres pour mettre en avant les ordres les plus attractifs pour les investisseurs : les plus hauts prix pour les achats et les plus bas pour les ventes.
        carnet_o.sort_values(by=['prix', 'quantite'], ascending=[(type_ordre == 'achat'), True], inplace=True)
        #quantité restante qu’il faut satisfaire 
        quantite_restante = ordre_taker['quantite']
        # Parcours du carnet d'ordres pour trouver des ordres correspondants à exécuter.
        for index, ordre in carnet_o.iterrows():
            if (type_ordre == 'vente' and ordre['prix'] >= ordre_taker['prix']) or (type_ordre == 'achat' and ordre['prix'] <= ordre_taker['prix']):
                # Pour les ventes, on cherche des ordres d'achat à un prix égal ou supérieur, et inversement pour les achats. Puisque si je suis acheteur je suis pret à payer un certain prix ou moins et inversement si je suis vendeur j’accepte de vendre à un certain prix ou plus.
                quantite_echangeable = min(quantite_restante, ordre['quantite'])
            	# Détermination de la quantité qui peut être effectivement échangée.
               	quantite_restante = quantite_restante-quantite_echangeable
            	# Mise à jour de la quantité restante de l'ordre taker.
                if ordre['quantite'] >= quantite_echangeable: 
                # Si l'ordre en carnet n'est que partiellement exécuté, ajustement de la quantité.
                    carnet_o.at[index, 'quantite'] = carnet_o.at[index, 'quantite'] - quantite_echangeable
                    
                    if (carnet_o.at[index, 'quantite'] == 0):
                    #sauvegarde de l'index de l'ordre a supprimer a la fin de la boucle
                        ordres_supprimes.append(index)

                if quantite_restante == 0:  
                    # Arrêt de la boucle si l'ordre taker a été entièrement exécuté.
                    break
        
        #Suppression des ventes/achats epuises
        carnet_o = carnet_o.drop(ordres_supprimes).reset_index(drop=True)
        if type_ordre == 'vente':
            self.ordre_achat = carnet_o
        else:
            self.ordre_vente = carnet_o
        
        # Si le taker n'a pas pu exécuter la totalité de son ordre et qu'il reste de la quantité, nous allons l'ajouter au carnet comme un ordre maker.
        if quantite_restante > 0:
            horaire_actuel = datetime.now().isoformat()
        
            if type_ordre == 'vente':
            #On ajoute l’ordre dans le carnet approprié donc on teste si c’est un ordre d’achat ou de vente.
                ordre_restant = {'prix': ordre_taker['prix'], 'quantite': quantite_restante, 'participant': ordre_taker['participant'], 'role': 'maker', 'position': 'achat', 'ref':f"{ordre_taker['participant']}_{quantite_restante}_{horaire_actuel}_{ordre_taker['prix']}_{'vente'}_{'maker'}", 'horaire':horaire_actuel}
                self.ordre_vente = self.ordre_vente._append(ordre_restant, ignore_index=True)
            else: #si c'est un ordre d'achat
                ordre_restant = {'prix': ordre_taker['prix'], 'quantite': quantite_restante, 'participant': ordre_taker['participant'], 'role': 'maker', 'position': 'achat', 'ref':f"{ordre_taker['participant']}_{quantite_restante}_{horaire_actuel}_{ordre_taker['prix']}_{'achat'}_{'maker'}", 'horaire':horaire_actuel}
                self.ordre_achat = self.ordre_achat._append(ordre_restant, ignore_index=True)
            print(f"Le reste de l'ordre de {quantite_restante} unités pour le taker {ordre_taker['participant']} a été ajouté comme un ordre maker.")
            #On prévient l’agent que son ordre a bien été ajouté en ordre maker.

# Méthode pour afficher le carnet
    def afficher_carnets(self):
    # methode pas utilisee dans le code principal mais implementee pour tester le code et verifier le fonctionnement de notre carnet d'ordre à l'achat et à la vente.
        if (self.ordre_achat.empty):
        #on indique que le carnet d'ordres d'achats est vide
            print("Carnet d'achat: VIDE")
        else:
            print("Carnet d'achat :\n", self.ordre_achat)
        if (self.ordre_vente.empty):
        #on indique que le carnet d'odre de ventes est vide
            print("Carnet de vente: VIDE")
        else:
            print("Carnet de vente :\n", self.ordre_vente)



#methode créée dans le cas ou un participant voudrait retirer un ordre d'un carnet d'ordre.
    def annuler_ordre(self, ref, participant):
    #Ici, comme on a deux carnets d'ordres distincts pour l'achat et la vente, faire une methode pour les ordres d'achat et une pour les ordres de vente semblait être mieux adapté.
    # Identifier les indices des ordres d'achat à annuler
        indices_achat_a_annuler = self.ordre_achat[(self.ordre_achat['ref'] == ref) & (self.ordre_achat['participant'] == participant)].index
    # s'il n'y a aucun ordre à annuler l'ordre ne peut pas être dans cette liste.
        if len(indices_achat_a_annuler) == 0: 
            print("Aucun ordre d'achat correspondant trouvé pour annulation.")
        else:
            self.ordre_achat = self.ordre_achat.drop(indices_achat_a_annuler) 
            #sinon on retrouve l'ordre à partir de son indice puis on le supprime.

        # Identifier les indices des ordres de vente à annuler
        indices_vente_a_annuler = self.ordre_vente[(self.ordre_vente['ref'] == ref) & (self.ordre_vente['participant'] == participant)].index
        # s'il n'y a aucun ordre à annuler l'ordre ne peut pas être dans cette liste.
        if len(indices_vente_a_annuler) == 0:            
           	print("Aucun ordre de vente correspondant trouvé pour annulation.")
        else:
        	#sinon on retrouve l'ordre à partir de son indice puis on le supprime.
            self.ordre_vente = self.ordre_vente.drop(indices_vente_a_annuler) 


    #Dans cette partie, nous allons mettre en place une méthode fixing destinée à déterminer le prix d'un actif financier à un moment donné. On cherche le prix (de fixing) défini comme le prix auquel le volume maximal d'ordres peut être exécuté. C'est-à-dire le prix ou le plus d'acheteurs et vendeurs acceptent de procéder à l'échange. Cette méthode est notamment utilisée avant l’ouverture et après la fermeture des marchés afin de déterminer un  prix de référence pour les investisseurs.
    
    def calculer_fixing(self):
    # Tout d'abord, on combine les deux types de carnets afin de synthétiser et de regrouper tous les ordres d'achat et de vente émis par les participants du marché.
        carnet_total = pd.concat([
        self.ordre_achat.assign(type='Achat'),
        self.ordre_vente.assign(type='Vente') ])

   	 # On tri les ordres par prix de manière à favoriser les achats à des prix élevés et les ventes à des prix faibles. Sur les marchés, il y a plus de transactions à des prix acheteurs élevés et des prix vendeurs faibles.
        carnet_total.sort_values(by=['prix', 'type'], ascending=[False, True], inplace=True)

  
# Initialisation des variables pour le volume maximal exécuté et le prix de fixing associé.
        v_max = 0  
        #on initialise le volume maximal
        prix_fix = 0 
        #on initialise le prix correspondant
  
 #On parcours chaque prix pour déterminer le volume exécuté et identifier le prix de fixing optimal.
        for prix in carnet_total['prix'].unique():
        	# Calcul de la quantité totale des ordres d'achat à ce prix ou à un prix plus élevé.
           	# Cela représente la demande totale pour le produit au prix donné ou à un prix supérieur.
        	v_achat =  carnet_total[( carnet_total['type'] == 'Achat') & ( carnet_total['prix'] >= prix)]['quantite'].sum()
        	# Calcul de la quantité totale des ordres de vente à ce prix ou à un prix moins élevé.
        	# Cela représente l'offre totale du produit au prix donné ou à un prix inférieur.
        	v_vente =  carnet_total[( carnet_total['type'] == 'Vente') & ( carnet_total['prix'] <= prix)]['quantite'].sum()
        	#Le volume execute est le volume minimum entre le volume d’achat et de vente, on ne peut pas executer plus que ce que proposent les agents.
        	v_exe = min(v_achat, v_vente)

        	# Si ce prix permet d'exécuter un plus grand volume d'ordres que le volume maximum, on met à jour le prix de fixing et le volume maximum.
        if v_exe > v_max:
            v_max = v_exe 
            prix_fix = prix

    	#A la fin de notre boucle, on retourne le prix de fixing trouvé ainsi que le volume maximal correspondant à ce prix.
        return prix_fix, v_max


#PARTIE 2 : Mise en place de l'exemple pour tester la Classe.

# Mise en place de l’exemple : 
exemple = Ordre(tick_size=0.01, lot_size=1)

# Ajout d’ordres de vente afin de tester la méthode de maker et vendeur.
exemple.ajout_ordre_vente(prix=100.5, position="vente", quantite=100, horaire="2023-04-08T09:30:00", participant="Trader Alain", role="maker")
exemple.ajout_ordre_vente(prix=101, position="vente", quantite=5, horaire="2023-04-08T10:00:00", participant="Trader Bernard", role="maker")

# Ajout d'ordres d'achat afin de tester la méthode de taker et acheteur.
exemple.ajout_ordre_achat(prix=99.5, position="achat", quantite=2, horaire="2023-04-08T10:30:00", participant="Trader Emma", role="maker")
exemple.ajout_ordre_achat(prix=102, position="achat", quantite=3, horaire="2023-04-08T11:00:00", participant="Trader Jose", role="taker")
exemple.ajout_ordre_achat(prix=101.5, position="achat", quantite=3, horaire="2023-04-08T11:30:00", participant="Trader Claude", role="taker")

# Un taker souhaite acheter immédiatement à un prix plus élevé que les offres existantes.
exemple.ajout_ordre_achat(prix=101.5, position="achat", quantite=7, horaire="2023-04-08T11:30:00", participant="Trader Claude", role="taker")

# Un taker souhaite vendre immédiatement à un prix plus bas que les offres existantes.
exemple.ajout_ordre_vente(prix=98.5, position="vente", quantite=10, horaire="2023-04-08T14:00:00", participant="Trader George", role="maker")

# Un taker souhaite acheter plus que ce qui est disponible sur le marché à l’achat.
exemple.ajout_ordre_achat(prix=99.5, position="achat", quantite=20, horaire="2023-04-08T15:30:00", participant="Trader Clara", role="taker")

# Affichage des carnets d'ordres pour observer l'état après les transactions.
#exemple.afficher_carnets()

# Annulation d'un ordre de vente par le Trader Alain.
exemple.annuler_ordre(ref="Trader Alain_100_2023-04-08T09:30:00_100.5_vente_maker", participant="Trader Alain")

# Affichage des carnets d'ordres après l'annulation de l'ordre par ce trader.
exemple.afficher_carnets()


#Après execution de ce projet, on obtient le carnet d'ordres résultant des différentes observations.

