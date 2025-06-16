# Outil de transformation du fichier xlsx des colles vers des agendas iCal lisibles.
# Codé par Jean Prêtet, Septembre 2024 - Juin 2025
#
# L'outil ci-dessous fonctionne intrégralement sur la structure actuelle du fichier du colloscope.
# Des modifications de sa structure entraineront des erreurs dans le programme.
# 
# Le programme suivant fonctionne avec plusieurs fonctions et scripts, voici ce qu'ils font :
# 1. Extraire les données du fichier XLSX au chemin spécifié par l'utilisateur.
# 2. Transformer localement ce fichier XLSX en CSV pour une meilleur comptabilité avec le Python et éviter les problèmes de mise en forme.
# 3. Différents tests sont réalisés pour voir si le fichier contient des erreurs dans la chronologie des dates, les modifier en des dates lisibles par Python, 
# extraire la version du colloscope et finalement trouver le nombre de groupe de colle pour pouvoir itérer dessus.
# 4. La fonction crawler() est celle qui fait tout le travail, en fonctionnant bloc par bloc (un bloc = une matière).
# Chaque ligne du fichier est parcourue et quand le numéro du groupe de colle considéré est détecté, le programme ajoute la colle au calendrier iCal.
# crawler() finit par enregistrer les calendriers au chemin spécifié par l'utilisateur.
#
# L'objectif est que ce script soit relancé à chaque modification du programme de colle avant de republier les calendriers sur un site web.
# De cette manière, les élèves n'ont rien à faire à part ajouter l'adresse de l'agenda dans leurs agendas personnels (Google Calendar, Calendrier Apple, Outlook...), les modifications apparaitront directement.
#
# CONSEILS
# Il est préférable de créer un répertoire dédié à l'export des agendas des groupes de colle.
# 


########################################################################
# PROGRAMME DE DECLARATION DES BOUCLES ET VARIABLES
########################################################################
# IMPORT DES MODULES NECESSAIRES
from icalendar import Calendar, Event
from datetime import datetime
import pandas as pd
import numpy as np
import io
import uuid

#CHEMIN DU FICHIER XLSX
programme_xlsx = "python/colloscope PTSIB_Année_2425_V16.xlsx" # MODFIIER LE CHEMIN ICI !

# LECTURE DU FICHIER XLSX
try :
    df = pd.read_excel(programme_xlsx, sheet_name=0)
except :
    raise ValueError(f"⚠️ Le chemin d'accès `{programme_xlsx}` est érroné !")

# CONVERTTIR EN CSV POUR UNE LECTURE PLUS SIMPLE
csv_temporaire = io.StringIO()
df.to_csv(csv_temporaire, index=False, header=False)
csv_temporaire.seek(0)

# NORMALISER LES DATES
def transform_date(value):
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                date_obj = datetime.strptime(value.strip(), fmt)
                return date_obj.strftime("%d/%m/%Y")
            except ValueError:
                continue
    return value

def normaliser_dates(csv_content = csv_temporaire.read()):
    # Lire le contenu CSV et transformer les dates directement
    lines = csv_content.splitlines()
    transformed_lines = []

    for line in lines:
        # Diviser la ligne en colonnes
        columns = line.split(',')
        # Appliquer la transformation à chaque colonne
        transformed_columns = [transform_date(col) for col in columns]
        # Rejoindre les colonnes transformées en une ligne
        transformed_lines.append(','.join(transformed_columns))

    # Rejoindre les lignes transformées en un seul contenu CSV
    return('\n'.join(transformed_lines))

programme_csv = normaliser_dates()
#print(programme_csv)

# LECTURE DU FICHIER CSV
df = pd.read_csv(io.StringIO(programme_csv), header=None)

# RÉCUPERER LA VERSION DU COLLOSCOPE
def version(nom_fichier=programme_xlsx):
    """
    Entrée : chemin d'accès au fichier
    Sortie : Version du colloscope
    """
    print("ℹ️ Calcul de la version")
    pos = nom_fichier.find('V')
    if pos != -1:
        version_with_ext = nom_fichier[pos:]
        version = version_with_ext.split('.')[0]
    else:
        print("⚠️ Version du colloscope non trouvée automatiquement. Veuillez l'entrer manuellement.")
        version = input("Version ? (Exemple : V12) : ")
    return version

#RÉCUPERER LE NOMBRE DE GROUPES (pour itérer dessus)
def trouver_max_groupe(df):
    """
    Entrée : Data Frame du programme de colle
    Sortie : Maximum des valeurs numériques dans le rectangle D4 à AP12
    """
    print("ℹ️ Calcul du nombre de groupes")
    sous_df = df.iloc[3:12, 3:42]  # D4 à AP12
    numeriques = pd.to_numeric(sous_df.values.flatten(), errors='coerce')
    numeriques_valides = numeriques[~pd.isna(numeriques)]
    maximum = int(numeriques_valides.max())
    if len(numeriques_valides) == 0:
        print("⚠️ Nombre de groupes non trouvé automatiquement. Veuillez l'entrer manuellement.")
        maximum = str(input("Nombre de groupes ? (Exemple : 16) : "))
    return maximum

# VERIFIER LA CHRONOLOGIE DES DATES
def verifier_chronologie(df):
    """
    Entrée : Data Frame
    Sortie : Dates problématiques
    """
    print("📅 Vérification des dates")
    ligne_dates = df.iloc[1, 3:]  # Ligne 2, colonnes à partir de D (index 3)
    dates = []
    dates_problématiques = []

    for cell in ligne_dates:
        if isinstance(cell, str) and cell.strip() == '':
            continue
        try:
            date = pd.to_datetime(cell)
            if pd.isna(date):
                continue
            dates.append(date.date())
        except Exception:
            continue

    for i in range(1, len(dates)):
        delta = (dates[i] - dates[i - 1]).days
        if delta == 7:
            print(f"✅ OK : {dates[i - 1]} → {dates[i]}")
        elif delta == 21:
            print(f"🟡 Vacances : {dates[i - 1]} → {dates[i]} ({delta} jours)")
        else:
            print(f"❌ Erreur de chronologie entre {dates[i - 1]} et {dates[i]} : {delta} jours")
            dates_problématiques.append(f'{dates[i - 1]} → {dates[i]}')
        if dates_problématiques :
            raise ValueError(f"⚠️ Erreur : les dates {dates_problématiques} sont à modifier.")

# NORMALISER LES VALEURS DES SEMAINES
def convertir_semaine_en_date(semaine):
    # Si semaine est déjà une date ou un timestamp
    if isinstance(semaine, (pd.Timestamp, datetime)):
        return pd.to_datetime(semaine).normalize()

    # Si c’est un nombre Excel (float ou int)
    if isinstance(semaine, (int, float, np.integer, np.floating)):
        return (pd.to_datetime("1899-12-30") + pd.to_timedelta(semaine, unit='D')).normalize()

    # Si c’est une chaîne de caractères
    if isinstance(semaine, str):
        try:
            return pd.to_datetime(semaine, errors='raise').normalize()
        except Exception:
            return pd.NaT

    # Si rien n’a fonctionné
    return pd.NaT


# CALCUL ELEVES
def crawler(df, chemin):
    for group in range(1,trouver_max_groupe(df)+1): # on boucle sur le nombre de groupes de colles + 1 car le dernier est exclu
        print(f"📅 Calcul du groupe {group}")
        # Création et initialisation d'un objet calendrier
        cal = Calendar()
        # Ajouter les propriétés de base du calendrier
        cal.add('version', Version)
        cal.add('prodid', '-//Colles PTSI B//collesptsib.github.io//FR')
        cal.add('calscale', 'GREGORIAN')

        # Ajouter le bloc de fuseau horaire
        timezone_block = """BEGIN:VTIMEZONE
        TZID:Europe/Paris
        X-LIC-LOCATION:Europe/Paris
        BEGIN:DAYLIGHT
        TZOFFSETFROM:+0100
        TZOFFSETTO:+0200
        TZNAME:CEST
        DTSTART:19700329T020000
        RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
        END:DAYLIGHT
        BEGIN:STANDARD
        TZOFFSETFROM:+0200
        TZOFFSETTO:+0100
        TZNAME:CET
        DTSTART:19701025T030000
        RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
        END:STANDARD
        END:VTIMEZONE"""

        # Ajouter le bloc de fuseau horaire au calendrier
        cal.add('vtimezone', timezone_block)

        ligne_dates = df.iloc[0,3:]
        i = 0
        while i < len(df):
            cell = df.iloc[i, 0]

            # Si cellule non vide et pas NaN → matière
            if not pd.isna(cell) and str(cell).strip() != '' and str(cell).strip() != "Unnamed: 0":
                matiere = str(cell).strip()
                #print(f"\nMatière : {matiere}")

                i += 1
                bloc = []

                # Tant qu'on est dans le bloc (première cellule non vide)
                while i < len(df):
                    ligne = df.iloc[i]
                    if pd.isna(ligne[0]) or str(ligne[0]).strip() == '':
                        break  # fin du bloc

                    bloc.append(ligne)
                    i += 1

                # Manipulation sur le bloc de la matière traitée
                for ligne in bloc:
                    #print(f"Prof : {ligne.iloc[0]}")
                    professeur = str(ligne.iloc[0]).strip()
                    info_date_heure = ligne.iloc[1]
                    salle = ligne.iloc[2]

                    # Parcourir les colonnes de dates à partir de la 4ème colonne (index 3)
                    for j in range(3, len(df.columns)):
                        semaine = str(ligne_dates[j])
                        valeur_raw = ligne.iloc[j]

                        # Si valeur vide ou NaN, on saute
                        if pd.isna(valeur_raw):
                            continue

                        try:
                            valeur = float(valeur_raw)
                        except Exception:
                            continue

                        # Vérifier si la valeur correspond au groupe (exemple 1)
                        if valeur == float(group):
                            #print("ok")

                            if isinstance(info_date_heure, str) and " " in info_date_heure:
                                jour, horaire = info_date_heure.split(' ')
                                heure_debut, heure_fin = horaire.split('-')

                                # Calculer le jour relatif
                                if jour == 'Lu':
                                    jour_semaine = 0
                                elif jour == 'Ma':
                                    jour_semaine = 1
                                elif jour == 'Me':
                                    jour_semaine = 2
                                elif jour == 'Je':
                                    jour_semaine = 3
                                elif jour == 'Ve':
                                    jour_semaine = 4

                                # Vérifier que semaine est une date valide
                                try:
                                    date_event = datetime.strptime(semaine, '%d/%m/%Y') + pd.DateOffset(days=jour_semaine)
                                except ValueError:
                                    print(f"Erreur de format de date pour la semaine: {semaine} :")
                                    continue

                                # Définir l'heure de début et de fin de l'événement
                                heure_debut = int(heure_debut)
                                heure_fin = int(heure_fin)

                                # Créer un objet Événement
                                event = Event()
                                event.add('summary', f"Colle {matiere} {professeur}")
                                event.add('location', salle)
                                event.add('dtstart', datetime(date_event.year, date_event.month, date_event.day, heure_debut, 0, 0, tzinfo=None))
                                event.add('dtend', datetime(date_event.year, date_event.month, date_event.day, heure_fin, 0, 0, tzinfo=None))
                                event.add('description', Version)  # Variable globale, à définir
                                event['dtstart'].params['TZID'] = "Europe/Paris"
                                event['dtend'].params['TZID'] = "Europe/Paris"
                                # Ajouter un UID unique avec un préfixe spécifique
                                event.add('uid', f"@collesptsib#{uuid.uuid4()}")
                                cal.add_component(event)
            else:
                i += 1

        with open(chemin + f"Colles Groupe {group}.ics" , 'ab') as f:
            f.write(cal.to_ical())

    print("✅ Programme de colle exporté avec succès pour les élèves.")
    print(f"📂 Les fichiers ont été exportés au chemin : {chemin}")


########################################################################

# PROGRAMME GENERAL
# Appel de la fonction de version
global Version
Version = version()
# Appel de la fonction calculant le nombre de groupes
nb_groupes = trouver_max_groupe(df)
# Appel de la fonction de vérification
verifier_chronologie(df)

crawler(df,chemin="python/Colles/")