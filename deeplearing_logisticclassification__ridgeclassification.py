# -*- coding: utf-8 -*-
"""DeepLearing_LogisticClassification& RidgeClassification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ssHQa13oPtmFQprBWKXBJVaE4KBHoxh1
"""

#Deep Learning

from __future__ import print_function
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import RMSprop
from sklearn.model_selection import train_test_split
import tensorflow as tf

from tensorflow.python.ops.numpy_ops import np_config
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

n = 31405
p = 0.3
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

# on convertit notre ensemble Y en donnée numérique
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(Y)
y = y.astype(np.float32)
X = X.astype(np.float32)

# On partitionne les données en ensemble d'apprentissage et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

num_classes = len(pd.unique(y))
batch_size = 128

# on initialise le modèle
model = Sequential()

# on ajoute les couches neuronals
# on utilise les deux fonctions logistiques les plus populaires
# trois couches neuronals en tout
model.add(Dense(num_classes, activation='relu', input_shape = (2492, ))) #activation relu
model.add(Dropout(0.1)) # on garde un dropout rate à 10% pour éviter le sur-apprentissage

model.add(Dense(64, activation = 'relu'))
model.add(Dropout(0.2)) # on monte le dropout rate à 20% pour éviter le sur-apprentissage

model.add(Dense(num_classes, activation='softmax')) 
model.add(Dropout(0.1)) 

# on donne les paramètres pour évaluer les modèles
# on utilise sparse_categorical_crossentropy pour classifier nos données
model.compile(loss='sparse_categorical_crossentropy', optimizer= RMSprop(), metrics='accuracy', run_eagerly=True)

# étape d'apprentissage
history = model.fit(X_train, y_train, epochs=10, validation_split= 0.2, batch_size=128)

model.summary()
score = model.evaluate(X_test, y_test, verbose=0)

print('Test loss:', score[0])
print('Test accuracy:', score[1])

plt.plot(history.history['accuracy'],label='train')
plt.legend(loc= 'upper left')
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.show()

plt.plot(history.history['loss'],label='train')
plt.legend(loc= 'upper right')
plt.title('Model cost')
plt.ylabel('Cost')
plt.xlabel('Epoch')
plt.show()

# On définit la fonction f1_weighted manuellement puisque Keras n'a pas de metric intrèseque pour f1_weighted
# y_pred est dans la forme [batch_size, num_classes].
# y_true est dans la forme [batch_size].
def f1_weighted(y_true, y_pred):
    y_true = y_true.numpy()
    y_pred = y_pred.numpy()

    categorie = np.zeros(len(y_true))

    for i in range(len(y_true)):
      # on choisit le meilleur classe - l'indice pour laquelle la (log-)probabilité est le maximum est la classe predit à cette étape
      categorie[i] = np.argmax(y_pred[i,:])

    f1score = f1_score(y_true, categorie, average='weighted')
    return f1score

# une modèle qui utilise la fonction f1_weighted pour evaluer le modèle
np_config.enable_numpy_behavior()

# on initialise le modèle
model = Sequential()

# on ajoute les couches neuronals
# on utilise les deux fonctions logistiques les plus populaires
# trois couches neuronals en tout
model.add(Dense(num_classes, activation='relu', input_shape = (2492, ))) #activation relu
model.add(Dropout(0.1)) # on garde un dropout rate à 10% pour éviter le sur-apprentissage

model.add(Dense(64, activation = 'relu'))
model.add(Dropout(0.2)) # on monte le dropout rate à 20% pour éviter le sur-apprentissage

model.add(Dense(num_classes, activation='softmax')) 
model.add(Dropout(0.1)) 

# on donne les paramètres pour évaluer les modèles
# on utilise sparse_categorical_crossentropy pour classifier nos données
model.compile(loss='sparse_categorical_crossentropy', optimizer= RMSprop(), metrics= f1_weighted, run_eagerly=True)

# étape d'apprentissage
history = model.fit(X_train, y_train, epochs=10, validation_split= 0.2, batch_size=128)

model.summary()
score = model.evaluate(X_test, y_test, verbose=0)

print('Test loss:', score[0])
print('Test accuracy:', score[1])

#Accuracy on the training dataset
trainPred = model.predict(X_train)
accuracy_score(y_train, trainPred)

# Normalisation des données

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.fit_transform(X_test)
X = scaler.transform(X)

#Régression Logistique
from sklearn.linear_model import LogisticRegression

clf = LogisticRegression(penalty='l2')

# on recherche le meilleur term de pénalité
paramgrid = {'C':[0.2, 0.4, 0.6, 0.8]}

# on simule les différents LassoRegression avec les pénalités et on choisit le meilleur
recherche_logistique = GridSearchCV(estimator=clf, param_grid = paramgrid, scoring='f1_weighted', cv=5, n_jobs = -1)
recherche_logistique.fit(X_train_sc, y_train)

print(recherche_logistique.best_estimator_)

# Ici, on initialise le meilleur estimateur 
model = LogisticRegression(penalty='l2', C=0.8)

logModel=model.fit(X_train_sc, y_train) # apprentisage
y_pred= model.predict(X_test) #test

train_log= logModel.predict(X_train)
accuracy_score(y_train,train_log)

accuracy_score(y_test,y_pred)

f1_score(y_test,y_pred,average='weighted')

titles_options = [("Confusion matrix, without normalisation", None),
                   ("Normalized confusion matrix", 'true')]

for title, normalize in titles_options:
    disp = ConfusionMatrixDisplay.from_estimator(logModel,X_test,y_test, normalize = normalize,
                               include_values=True, xticks_rotation='horizontal', cmap='viridis', colorbar=True)
    disp.ax_.set_title(title)

    print(title)
    print(disp.confusion_matrix)

    plt.show()

#Ridge Classifier
from sklearn.linear_model import RidgeClassifier

# Create RidgeClassifier instance
rdgclassifier = RidgeClassifier(random_state=0)

# Recherche du meilleur alpha (coefficient de normalisation) ici aussi
paramgrid = {'alpha':[2, 4, 6, 8, 10, 12]}

# on simule les différents RidgeRegression avec les pénalités et on choisit le meilleur
recherche_ridge = GridSearchCV(estimator=rdgclassifier, param_grid = paramgrid, scoring='f1_weighted', cv=5, n_jobs = -1)
recherche_ridge.fit(X_train_sc, y_train)

print(recherche_ridge.best_estimator_)

# Ici, on initialise le meilleur estimateur Ridge
model_ridge = RidgeClassifier(alpha=2, random_state=0)

model_ridge.fit(X_train_sc, y_train) # apprentisage
y_pred= model.predict(X_test) #test

accuracy_score(y_test,y_pred)



f1_score(y_test,y_pred,average='weighted')