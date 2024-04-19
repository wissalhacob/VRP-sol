import pandas as pd
from ortools.linear_solver import pywraplp
from geopy.distance import geodesic
import folium


# Chargement des données depuis les fichiers Excel
df_village = pd.read_excel("./Coordonnées_cleaned.xlsx", index_col=None)
df_depot = pd.read_excel("./Dépot.xlsx")
df_besoin = pd.read_excel("./Population_cleaned.xlsx")

# Définition des véhicules
vehicles = [
    {'id': "V1", 'Capacity max en tonnes': 2.5, "Vitesse en Km/h": 295},
    {'id': "V2", 'Capacity max en tonnes': 4, "Vitesse en Km/h": 310},
    {'id': "V3", 'Capacity max en tonnes': 2.8, "Vitesse en Km/h": 310}
]

# Nombre de jours
nb_days = 3

# Définition du solveur
solver = pywraplp.Solver.CreateSolver('SCIP')

# Définition des variables de décision
x_i_j_m = {(i, j, m, k): solver.BoolVar(f'x_i_j_m[{i},{j},{m},{k}]') 
            for i in range(len(df_village)) 
            for j in range(nb_days)
            for m in range(len(vehicles))
            for k in range(len(df_depot))}

# Ajout des contraintes de capacité
for k in range(len(df_depot)):
    for m in range(len(vehicles)):
        for j in range(nb_days):
            solver.Add(
                solver.Sum(
                    (df_besoin.loc[i, 'besoins du village'] / 1000) * x_i_j_m[i, j, m, k] 
                    for i in range(len(df_village))
                ) <= vehicles[m]['Capacity max en tonnes']
            )

# Ajout des contraintes d'affectation
for i in range(len(df_village)):
    solver.Add(solver.Sum(x_i_j_m[i, j, m, k] 
                          for j in range(nb_days) 
                          for m in range(len(vehicles)) 
                          for k in range(len(df_depot))) == 1)

# Ajout des contraintes d'existence de chemin
for j in range(nb_days):
    for k in range(len(df_depot)):
        for m in range(len(vehicles)):
            solver.Add(solver.Sum(x_i_j_m[i, j, m, k] for i in range(len(df_village))) >= 1)

# Définition des variables de temps de trajet
travel_time = {}
for j in range(nb_days):
    for k in range(len(df_depot)):
        for m in range(len(vehicles)):
            travel_time[(j, k, m)] = solver.NumVar(0, solver.infinity(), f'travel_time_{j}_{k}_{m}')

# Calcul du temps de trajet pour chaque segment
for j in range(nb_days):
    for k in range(len(df_depot)):
        for m in range(len(vehicles)):
            travel_time[(j, k, m)].SetBounds(0, 2.5 * 3600)  # Limite de temps à 2,5 heures
            for i in range(len(df_village)):
                if x_i_j_m[i, j, m, k].solution_value() == 1:
                    distance = geodesic((df_village.loc[i, 'y'], df_village.loc[i, 'x']),
                                         (df_village.loc[i + 1, 'y'], df_village.loc[i + 1, 'x'])).kilometers
                    time = (distance / vehicles[m]['Vitesse en Km/h']) * 3600  # Convertir en secondes
                    solver.Add(travel_time[(j, k, m)] >= time)

# Contrainte pour limiter la somme des temps de trajet à 2,5 heures
for j in range(nb_days):
    for k in range(len(df_depot)):
        for m in range(len(vehicles)):
            solver.Add(solver.Sum(travel_time[(j, k, m)] for k in range(len(df_depot))) <= 2.5 * 3600)



# Définition de la fonction objectif
total_distance = {}
for j in range(nb_days):
    for k in range(len(df_depot)):
        for m in range(len(vehicles)):
            total_distance[(j, k, m)] = solver.NumVar(0, solver.infinity(), f'distance_{j}_{k}_{m}')
            path_distance = 0
            first_village_distance = geodesic((df_depot.loc[k, 'y'], df_depot.loc[k, 'x']),
                                               (df_village.loc[0, 'y'], df_village.loc[0, 'x'])).kilometers
            path_distance += first_village_distance
            for i in range(len(df_village) - 1):
                if x_i_j_m[i, j, m, k].solution_value() == 1:
                    village_distance = geodesic((df_village.loc[i, 'y'], df_village.loc[i, 'x']),
                                                (df_village.loc[i + 1, 'y'], df_village.loc[i + 1, 'x'])).kilometers
                    path_distance += village_distance

            last_village_distance = geodesic((df_village.loc[len(df_village) - 1, 'y'], df_village.loc[len(df_village) - 1, 'x']),
                                              (df_depot.loc[k, 'y'], df_depot.loc[k, 'x'])).kilometers
            path_distance += last_village_distance


            # Ajouter la contrainte pour que la variable de distance totale soit égale à la distance calculée
            solver.Add(total_distance[(j, k, m)] == path_distance)



# Définition de la fonction objectif pour minimiser la somme des distances totales
objective = solver.Objective()
objective.SetMinimization()
for k in range(len(df_depot)):
    for m in range(len(vehicles)):
        for j in range(nb_days):
            objective.SetCoefficient(total_distance[(j, k, m)], 1)
def calculate_distance(route, depot_coords):
    total_distance = 0
    
    # Calculer la distance entre le dépôt et le premier village
    first_village_distance = geodesic(depot_coords, route[1]).kilometers
    total_distance += first_village_distance
    
    # Calculer la distance entre les villages
    for i in range(1, len(route) - 1):
        village_distance = geodesic(route[i], route[i + 1]).kilometers
        total_distance += village_distance
    
    # Calculer la distance entre le dernier village et le dépôt
    last_village_distance = geodesic(route[-2], depot_coords).kilometers
    total_distance += last_village_distance
    
    return total_distance

# Résolution du problème
status = solver.Solve()

# Extraction des chemins optimisés à partir des variables de décision du solveur
optimized_paths = []
for j in range(nb_days):
    for k in range(len(df_depot)):
        for m in range(len(vehicles)):
            path = [(df_depot.loc[k, 'y'], df_depot.loc[k, 'x'])]  # Début du chemin au dépôt
            for i in range(len(df_village)):
                if x_i_j_m[i, j, m, k].solution_value() == 1:
                    path.append((df_village.loc[i, 'y'], df_village.loc[i, 'x']))
            path.append((df_depot.loc[k, 'y'], df_depot.loc[k, 'x']))  # Fin du chemin au dépôt
            optimized_paths.append(path)


# Génération du fichier Excel
df_paths = pd.DataFrame(columns=['Jour', 'Dépôt', 'Véhicule', 'Chemin'])
my_map = folium.Map(location=[31.7917, -7.0926], zoom_start=8, control_scale=True, zoomControl=False, scrollWheelZoom=False, tiles='CartoDB PositronNoLabels')


# Ajout des marqueurs pour les dépôts
for _, depot in df_depot.iterrows():
    tooltip_text = f"<b>{depot['nom']}</b><br>"
    for j in range(nb_days):
        tooltip_text += f"<i>Jour {j + 1}:</i><br>"
        for m, vehicle in enumerate(vehicles):
            path_distance = 0
            first_village_distance = geodesic((depot['y'], depot['x']),
                                               (df_village.loc[0, 'y'], df_village.loc[0, 'x'])).kilometers
            path_distance += first_village_distance
            for i in range(len(df_village) - 1):
                if x_i_j_m[i, j, m, _].solution_value() == 1:
                    village_distance = geodesic((df_village.loc[i, 'y'], df_village.loc[i, 'x']),
                                                (df_village.loc[i + 1, 'y'], df_village.loc[i + 1, 'x'])).kilometers
                    path_distance += village_distance

            last_village_distance = geodesic((df_village.loc[len(df_village) - 1, 'y'], df_village.loc[len(df_village) - 1, 'x']),
                                              (depot['y'], depot['x'])).kilometers
            path_distance += last_village_distance

            tooltip_text += f"Véhicule {vehicle['id']}: {path_distance:.2f} km<br>"

        tooltip_text += "<br>"
    folium.Marker(location=[depot['y'], depot['x']], tooltip=tooltip_text, icon=folium.Icon(color='blue')).add_to(my_map)

# Ajout des marqueurs pour les villages
for _, village in df_village.iterrows():
    folium.Marker(location=[village['y'], village['x']], tooltip=village['Douar'], icon=folium.Icon(color='green')).add_to(my_map)

# Parcours de chaque dépôt
vehicle_colors = ['blue', 'green', 'red']  # Couleurs pour chaque véhicule
optimized_paths = []  # Liste pour stocker les chemins optimisés
# Construction du dictionnaire des chemins par jour
paths_by_day = {day: [] for day in range(1, nb_days + 1)}
# Parcours de chaque dépôt
for j in range(nb_days):
    for k in range(len(df_depot)):
        for m in range(len(vehicles)):
            path = [(df_depot.loc[k, 'y'], df_depot.loc[k, 'x'])]
            village_names = [df_depot.loc[k, 'nom']]  # Ajouter le nom du dépôt au début du chemin
            visited_villages_indices = []  # Liste pour stocker les indices des villages visités par le véhicule
            for i in range(len(df_village)):
                if x_i_j_m[i, j, m, k].solution_value() == 1:
                    visited_villages_indices.append(i)  # Stocker l'indice du village visité

            # Ajouter les coordonnées des villages visités au chemin
            for i in visited_villages_indices:
                village_coords = (df_village.loc[i, 'y'], df_village.loc[i, 'x'])
                path.append(village_coords)
                village_names.append(df_village.loc[i, 'Douar'])

            # Ajouter les coordonnées du dépôt à la fin du chemin
            path.append((df_depot.loc[k, 'y'], df_depot.loc[k, 'x']))
            village_names.append(df_depot.loc[k, 'nom'])

            # Ajouter le chemin et les noms de village au dictionnaire
            paths_by_day[j + 1].append((path, vehicles[m]['id'], village_names))  # Modification ici

            # Stocker le chemin optimisé dans la liste
            optimized_paths.append((path, vehicle_colors[m], village_names))  # Correction ici
            
            # Ajout des données à df_paths
            df_paths = pd.concat([df_paths, pd.DataFrame({
                'Jour': [j + 1],
                'Dépôt': [df_depot.loc[k, 'nom']],
                'Véhicule': [vehicles[m]['id']],
                'Chemin': [village_names]
            })], ignore_index=True)
            
            # Créer un chemin avec un attribut data-day correspondant au jour
            polyline = folium.PolyLine(path, color=vehicle_colors[m], weight=2.5, opacity=1)  # Correction ici
            # Ajouter un attribut data-day au chemin
            polyline.options['data-day'] = j + 1
            
            # Condition pour n'afficher que les chemins du jour 1
            if j == 2:
                polyline.add_to(my_map)  # Ajoutez le chemin à la carte du jour 1 uniquement

from folium import Element

# Création des boutons avec des liens vers les fichiers HTML correspondants
buttons_html = """
<div id="buttons" style="position: fixed; top: 10px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 1px solid black;">
    <h3 style="margin-top: 0;">Contrôle des Chemins</h3>
"""

for day in range(1, nb_days + 1):
    buttons_html += f"""
    <button onclick="window.location.href='./optimized_delivery_map_day_{day}.html'">Jour {day}</button>
"""

buttons_html += """
</div>
"""

my_map.get_root().html.add_child(Element(buttons_html))





sidebar_html = """
<div style="position: fixed; right: 10px; width: 400px; max-height:100%; overflow-y: auto; z-index: 1000; background-color: white; padding: 10px; border: 1px solid black;">
    <h3 style="margin-top: 0;">Planning</h3>
    <ul style="margin-top: 0;">
"""


# Construction de la liste des chemins
for day in range(1, nb_days + 1):
    sidebar_html += f"<li><strong>Jour {day}:</strong></li>"
    for path, vehicle, village_names in paths_by_day[day]:
        sidebar_html += "<ul>"
        sidebar_html += f"<li>{', '.join(village_names)}; (Véhicule: {vehicle})</li>"
        sidebar_html += "</ul>"

sidebar_html += """
    </ul>
</div>
"""


# Ajout de la barre latérale personnalisée à la carte
my_map.get_root().html.add_child(folium.Element(sidebar_html))

# Enregistrement du fichier Excel
path_to_output = "./Chemins.xlsx"
with pd.ExcelWriter(path_to_output) as writer:
    df_paths.to_excel(writer, index=False)


print("Les chemins ont été enregistrés dans le fichier:", path_to_output)
my_map.save("./optimized_delivery_map_day_3.html")