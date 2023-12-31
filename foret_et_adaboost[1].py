# -*- coding: utf-8 -*-
"""Foret et Adaboost.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1e0ZoIzwvZgcjBu49SEIpwdTKorEL0BuW
"""

# importation des données
# code provenant du notebook jupyter sur l'ENT MLR
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from sklearn import neighbors
from sklearn.model_selection import train_test_split, cross_val_score, cross_validate
from sklearn.model_selection import ShuffleSplit, GridSearchCV

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from scipy.stats import stats
from sklearn.model_selection import cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

n = 31405
p = 0.8
Skiprows = np.where(np.random.uniform(size=(n)) > p)[0]

varnames = [str(i) for i in range(2497)]
data1 = pd.read_csv("https://perso.univ-rennes1.fr/valerie.monbet/MachineLearning/AndroidMalware_Training_set.csv",
                  sep=",",skiprows=Skiprows,
                  names = varnames,
                  header=None)

# on retire l'ensemble des échantillons sur laquelle on va faire nos tests et appliquer l'algorithme
# on retire le hash les deux colonnes suivants, non nécessaires pour l'apprentissage après
data2 = data1.drop(data1.columns[[2493, 2494, 2496]], axis=1)

# extractions des données
X = data2.iloc[:, :2492]
Y = data2.iloc[:, -1]

# Triage des données. On retire les NaN
X = X.dropna()
Y = Y.dropna()

# on sépare les données en deux ensembles - une pour l'apprentissage et l'autre pour le test
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.25, random_state=42)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X = scaler.transform(X)

# on met en place un arbre pour prédire le type de spam
foret = RandomForestClassifier()

#les paramètres à tester
paramgrid = {'max_depth':[8, 10, 12, 14], 'max_features':[80, 100, 120, 140]}

# on simule les différents forets et choisi le meilleur
recherche_foret = GridSearchCV(estimator=foret, param_grid = paramgrid, scoring='f1_weighted', cv=5, n_jobs = -1)
recherche_foret.fit(X_train, y_train)

print(recherche_foret.best_estimator_)

# On calcule la meilleure forêt
meilleur_foret = RandomForestClassifier(max_depth=14, max_features=140)
meilleur_foret.fit(X_train_sc, y_train) # apprentissage

# on affiche les erreurs de classfication utilisant la matrice de confusion
foret_predit = meilleur_foret.predict(X_test)

# comparaison des classifications et afichage d'une matrice de confusion
nos_labels = Y.unique()
matrice_de_confusion = confusion_matrix(foret_predit, y_test, normalize="true", labels = nos_labels)
conf_disp = ConfusionMatrixDisplay(matrice_de_confusion, display_labels=nos_labels)

fig, ax = plt.subplots(figsize=(12,12))
conf_disp.plot(ax=ax)
plt.show()

# on affiche le scoring de la meilleure forêt
# on calcule l'erreur
cv_scores = cross_validate(meilleur_foret, X, Y, cv=5, n_jobs = -1, scoring='f1_weighted')
erreur_f1 = np.round(np.mean(cv_scores['test_score']),3)

print(erreur_f1)

# On recherche le meilleur estimateur Adaboost
parametres = {'n_estimators': [200, 300, 400], 'learning_rate' : [0.01,0.1,1]}
adaboost = AdaBoostClassifier(DecisionTreeClassifier(max_depth=10, min_samples_leaf=5))
search = GridSearchCV(adaboost, parametres, scoring="f1_weighted", cv=5, n_jobs=-1)
search.fit(X_train,y_train)

print(search.best_estimator_)

# on affiche le score du meilleur adaboost
# on calcule l'erreur
meilleur_adaboost = AdaBoostClassifier(DecisionTreeClassifier(max_depth=10, min_samples_leaf=5), n_estimators=200, learning_rate=1)
cv_scores = cross_validate(meilleur_adaboost, X, Y, cv=5, n_jobs = -1, scoring='f1_weighted')
erreur_f1 = np.round(np.mean(cv_scores['test_score']),3)

print(erreur_f1)

# On affiche la matrice de confusion pour le meilleur choix d'Adaboost
meilleur_adaboost = AdaBoostClassifier(DecisionTreeClassifier(max_depth=10, min_samples_leaf=5), n_estimators=200, learning_rate=1)
meilleur_adaboost.fit(X_train_sc, y_train)

X_test_sc = scaler.fit_transform(X_test)
# on affiche les erreurs de classfication utilisant la matrice de confusion
adaboost_predit = meilleur_adaboost.predict(X_test_sc)

# comparaison des classifications et affichage d'une matrice de confusion
nos_labels = Y.unique()
matrice_de_confusion = confusion_matrix(adaboost_predit, y_test, normalize="true", labels = nos_labels)
conf_disp = ConfusionMatrixDisplay(matrice_de_confusion, display_labels=nos_labels)

fig, ax = plt.subplots(figsize=(12,12))
conf_disp.plot(ax=ax)
plt.show()

# On affiche les différences dans l'imporance des 10 premiers variables pour le meilleur arbre
meilleur_arbre = DecisionTreeClassifier(max_depth=10, min_samples_leaf=5)
meilleur_arbre.fit(X_train_sc, y_train) # apprentissage

importances_arbre = meilleur_arbre.feature_importances_

# les indices qui arrangent l'arbre
indices_arbres = np.argsort(importances_arbre)[-20:]

# Plot the feature importances of the forest
plt.title("Importances des variables pour le meilleur arbre")
plt.barh(range(20), importances_arbre[indices_arbres], color="r", align="center")
plt.yticks(range(20), indices_arbres)
plt.ylim([-1, 20])
plt.show()

# On affiche les différences dans l'imporance des 10 premiers variables entre pour le meilleur arbre
meilleur_foret = RandomForestClassifier(max_depth=14, max_features=140)
meilleur_foret.fit(X_train_sc, y_train) # apprentissage

importances_foret = meilleur_foret.feature_importances_

# les indices qui arrangent l'arbre
indices_foret = np.argsort(importances_foret)[-20:]

# on affiche dans un bar plot - code du cours
# Plot the feature importances of the forest
plt.title("Importances des variables pour la meilleure forêt")
plt.barh(range(20), importances_foret[indices_foret], color="r", align="center")
plt.yticks(range(20), indices_foret)
plt.ylim([-1, 20])
plt.show()