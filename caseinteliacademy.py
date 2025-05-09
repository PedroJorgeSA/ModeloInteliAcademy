# -*- coding: utf-8 -*-
"""caseInteliAcademy.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1sZ4UfNcJklGDyMS5SEFgs7UCisgUs9hp
"""

## 1. Importação das Bibliotecas
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer

## 2. Carregamento dos Dados
train = pd.read_csv('dados_clientes.csv')
test = pd.read_csv('desafio.csv')

print(f'Dados de treino carregados com {train.shape[0]} linhas e {train.shape[1]} colunas.')
print(f'Dados de teste carregados com {test.shape[0]} linhas e {test.shape[1]} colunas.')

## 3. Pré-processamento e Engenharia de Features

import ast

def processa_produtos(df):
    produtos_possiveis = ['Produto A', 'Produto B', 'Produto C', 'Produto D', 'Produto E', 'Produto F']
    def parse_produtos(x):
        if isinstance(x, list):
            return x
        try:
            return ast.literal_eval(x)
        except:
            return []
    df['produtos_assinados'] = df['produtos_assinados'].apply(parse_produtos)
    for prod in produtos_possiveis:
        df[f'has_{prod}'] = df['produtos_assinados'].apply(lambda lst: int(prod in lst))
    df['num_produtos'] = df['produtos_assinados'].apply(len)
    df = df.drop('produtos_assinados', axis=1)
    return df

train = processa_produtos(train)
test = processa_produtos(test)

## 4. Seleção de Features e Target

target = 'churn'
id_col = 'id_cliente'
features = [col for col in train.columns if col not in [target, id_col, 'servicos_assinados']]

X = train[features]
y = train[target]
X_test = test[features]
test_ids = test[id_col]

numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_features = X.select_dtypes(include=['object']).columns.tolist()

print(f'Número de features numéricas: {len(numeric_features)}')
print(f'Número de features categóricas: {len(categorical_features)}')

## 5. Pipeline de Pré-processamento

preprocessor = ColumnTransformer([
    ('num', Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ]), numeric_features),
    ('cat', Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ]), categorical_features)
])

## 6. Treinamento e Avaliação de Modelos

X_train, X_val, y_train, y_val = train_test_split(
    X, y, stratify=y, test_size=0.2, random_state=42)

models = {
    'LogisticRegression': LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42),
    'RandomForest': RandomForestClassifier(class_weight='balanced', n_estimators=100, random_state=42)
}

for name, clf in models.items():
    pipe = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', clf)
    ])
    pipe.fit(X_train, y_train)
    score = pipe.score(X_val, y_val)
    print(f'Modelo: {name} | Acurácia no conjunto de validação: {score:.4f}')


## 7. Treinamento do Modelo Final (Random Forest)

final_model = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(class_weight='balanced', n_estimators=100, random_state=42))
])
final_model.fit(X, y)
print('Modelo final treinado com todos os dados de treino.')

## 8. Importância das Features

feature_names_num = numeric_features
feature_names_cat = list(final_model.named_steps['preprocessor']
                        .named_transformers_['cat']
                        .named_steps['onehot']
                        .get_feature_names_out(categorical_features))

feature_names = feature_names_num + feature_names_cat

importances = final_model.named_steps['classifier'].feature_importances_

feat_imp_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
feat_imp_df = feat_imp_df.sort_values(by='importance', ascending=False)

print('\nTop 10 features mais importantes:')
print(feat_imp_df.head(10).to_string(index=False))


## 9. Previsão no Conjunto de Teste e Geração do CSV

predictions = final_model.predict(X_test)

resultado = pd.DataFrame({
    'Id': test_ids,
    'Target': predictions
})

resultado.to_csv('pedro.soares', index=False)
print('\nArquivo "pedro.soares" gerado com sucesso.')