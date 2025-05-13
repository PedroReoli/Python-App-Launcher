import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pickle
import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import threading
import time

# Bibliotecas de Machine Learning
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, plot_tree
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.feature_selection import SelectKBest, f_classif, f_regression, RFE
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.manifold import TSNE
import seaborn as sns
from scipy import stats

# Configuração de logging
logger = logging.getLogger("JSONMaster.AI")

class AIModelManager:
    """Gerenciador de modelos de IA"""
    def __init__(self):
        self.models = {}
        self.trained_models = {}
        self.feature_importances = {}
        self.model_metrics = {}
        self.encoders = {}
        self.scalers = {}
        self.current_model = None
        self.current_model_name = None
        
        # Inicializar modelos disponíveis
        self._initialize_models()
    
    def _initialize_models(self):
        """Inicializar os modelos disponíveis"""
        # Modelos de classificação
        self.models["classification"] = {
            "Random Forest": RandomForestClassifier(random_state=42),
            "Gradient Boosting": GradientBoostingClassifier(random_state=42),
            "Logistic Regression": LogisticRegression(random_state=42),
            "SVM": SVC(probability=True, random_state=42),
            "K-Nearest Neighbors": KNeighborsClassifier(),
            "Decision Tree": DecisionTreeClassifier(random_state=42),
            "Neural Network": MLPClassifier(random_state=42, max_iter=1000)
        }
        
        # Modelos de regressão
        self.models["regression"] = {
            "Random Forest": RandomForestRegressor(random_state=42),
            "Gradient Boosting": GradientBoostingRegressor(random_state=42),
            "Linear Regression": LinearRegression(),
            "SVR": SVR(),
            "K-Nearest Neighbors": KNeighborsRegressor(),
            "Decision Tree": DecisionTreeRegressor(random_state=42),
            "Neural Network": MLPRegressor(random_state=42, max_iter=1000)
        }
        
        # Modelos de clustering
        self.models["clustering"] = {
            "K-Means": KMeans(random_state=42),
            "DBSCAN": DBSCAN()
        }
    
    def get_available_models(self, task_type):
        """Obter modelos disponíveis para um tipo de tarefa"""
        return list(self.models.get(task_type, {}).keys())
    
    def get_model(self, task_type, model_name):
        """Obter um modelo específico"""
        return self.models.get(task_type, {}).get(model_name)
    
    def train_model(self, task_type, model_name, X, y=None, test_size=0.2, params=None):
        """Treinar um modelo"""
        model = self.get_model(task_type, model_name)
        if not model:
            raise ValueError(f"Modelo {model_name} não encontrado para a tarefa {task_type}")
        
        # Criar uma cópia do modelo para não modificar o original
        model = pickle.loads(pickle.dumps(model))
        
        # Aplicar parâmetros personalizados se fornecidos
        if params:
            model.set_params(**params)
        
        # Preparar os dados
        if task_type in ["classification", "regression"]:
            # Dividir em treino e teste
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
            
            # Treinar o modelo
            model.fit(X_train, y_train)
            
            # Avaliar o modelo
            if task_type == "classification":
                y_pred = model.predict(X_test)
                metrics = {
                    "accuracy": accuracy_score(y_test, y_pred),
                    "precision": precision_score(y_test, y_pred, average='weighted', zero_division=0),
                    "recall": recall_score(y_test, y_pred, average='weighted', zero_division=0),
                    "f1": f1_score(y_test, y_pred, average='weighted', zero_division=0)
                }
                
                # Matriz de confusão
                cm = confusion_matrix(y_test, y_pred)
                metrics["confusion_matrix"] = cm
                
            else:  # regression
                y_pred = model.predict(X_test)
                metrics = {
                    "mse": mean_squared_error(y_test, y_pred),
                    "mae": mean_absolute_error(y_test, y_pred),
                    "r2": r2_score(y_test, y_pred)
                }
            
            # Armazenar dados de teste para uso posterior
            metrics["X_test"] = X_test
            metrics["y_test"] = y_test
            metrics["y_pred"] = y_pred
            
            # Armazenar importância das características se disponível
            if hasattr(model, 'feature_importances_'):
                self.feature_importances[model_name] = model.feature_importances_
            
        else:  # clustering
            # Treinar o modelo
            model.fit(X)
            
            # Avaliar o modelo
            if model_name == "K-Means":
                metrics = {
                    "inertia": model.inertia_,
                    "n_clusters": model.n_clusters
                }
            else:  # DBSCAN
                metrics = {
                    "n_clusters": len(set(model.labels_)) - (1 if -1 in model.labels_ else 0)
                }
            
            # Armazenar rótulos de cluster
            metrics["labels"] = model.labels_
        
        # Armazenar o modelo treinado e métricas
        self.trained_models[model_name] = model
        self.model_metrics[model_name] = metrics
        
        # Definir como modelo atual
        self.current_model = model
        self.current_model_name = model_name
        
        return model, metrics
    
    def predict(self, X):
        """Fazer previsões com o modelo atual"""
        if not self.current_model:
            raise ValueError("Nenhum modelo treinado disponível")
        
        return self.current_model.predict(X)
    
    def save_model(self, file_path):
        """Salvar o modelo atual"""
        if not self.current_model:
            raise ValueError("Nenhum modelo treinado disponível para salvar")
        
        model_data = {
            "model": self.current_model,
            "name": self.current_model_name,
            "metrics": self.model_metrics.get(self.current_model_name, {}),
            "feature_importances": self.feature_importances.get(self.current_model_name, None),
            "encoders": self.encoders,
            "scalers": self.scalers,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(file_path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, file_path):
        """Carregar um modelo salvo"""
        with open(file_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.current_model = model_data["model"]
        self.current_model_name = model_data["name"]
        self.model_metrics[self.current_model_name] = model_data["metrics"]
        
        if "feature_importances" in model_data and model_data["feature_importances"] is not None:
            self.feature_importances[self.current_model_name] = model_data["feature_importances"]
        
        if "encoders" in model_data:
            self.encoders = model_data["encoders"]
        
        if "scalers" in model_data:
            self.scalers = model_data["scalers"]
        
        return self.current_model

class DataPreprocessor:
    """Classe para pré-processamento de dados"""
    def __init__(self):
        self.encoders = {}
        self.scalers = {}
        self.imputers = {}
    
    def preprocess_data(self, df, target_column=None, categorical_columns=None, numerical_columns=None):
        """Pré-processar os dados para modelagem"""
        # Fazer uma cópia para não modificar o original
        df_processed = df.copy()
        
        # Identificar tipos de colunas se não fornecidos
        if categorical_columns is None:
            categorical_columns = df_processed.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if numerical_columns is None:
            numerical_columns = df_processed.select_dtypes(include=['int64', 'float64']).columns.tolist()
            if target_column in numerical_columns:
                numerical_columns.remove(target_column)
        
        # Tratar valores ausentes
        for col in numerical_columns:
            if df_processed[col].isnull().any():
                self.imputers[col] = SimpleImputer(strategy='mean')
                df_processed[col] = self.imputers[col].fit_transform(df_processed[[col]])
        
        for col in categorical_columns:
            if df_processed[col].isnull().any():
                self.imputers[col] = SimpleImputer(strategy='most_frequent')
                df_processed[col] = self.imputers[col].fit_transform(df_processed[[col]])
        
        # Codificar variáveis categóricas
        for col in categorical_columns:
            if col != target_column:
                self.encoders[col] = LabelEncoder()
                df_processed[col] = self.encoders[col].fit_transform(df_processed[col])
        
        # Normalizar variáveis numéricas
        for col in numerical_columns:
            self.scalers[col] = StandardScaler()
            df_processed[col] = self.scalers[col].fit_transform(df_processed[[col]])
        
        # Preparar variável alvo se fornecida
        X = df_processed.drop(columns=[target_column]) if target_column else df_processed
        y = None
        
        if target_column:
            if target_column in categorical_columns:
                self.encoders[target_column] = LabelEncoder()
                y = self.encoders[target_column].fit_transform(df[target_column])
            else:
                y = df[target_column].values
        
        return X, y
    
    def transform_new_data(self, df):
        """Transformar novos dados usando os mesmos preprocessadores"""
        df_processed = df.copy()
        
        # Aplicar imputação
        for col, imputer in self.imputers.items():
            if col in df_processed.columns:
                df_processed[col] = imputer.transform(df_processed[[col]])
        
        # Aplicar codificação
        for col, encoder in self.encoders.items():
            if col in df_processed.columns:
                try:
                    df_processed[col] = encoder.transform(df_processed[col])
                except:
                    # Lidar com valores não vistos durante o treinamento
                    logger.warning(f"Valores não vistos na coluna {col}. Usando valor padrão.")
                    df_processed[col] = 0
        
        # Aplicar normalização
        for col, scaler in self.scalers.items():
            if col in df_processed.columns:
                df_processed[col] = scaler.transform(df_processed[[col]])
        
        return df_processed

class PatternDetector:
    """Classe para detecção de padrões nos dados"""
    def __init__(self):
        self.outliers = {}
        self.correlations = None
        self.clusters = None
        self.anomalies = None
    
    def detect_outliers(self, df, columns=None, method='zscore', threshold=3):
        """Detectar outliers nos dados"""
        if columns is None:
            columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        outliers = {}
        
        for col in columns:
            if method == 'zscore':
                z_scores = stats.zscore(df[col], nan_policy='omit')
                outliers[col] = df.index[abs(z_scores) > threshold].tolist()
            
            elif method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers[col] = df.index[(df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))].tolist()
        
        self.outliers = outliers
        return outliers
    
    def analyze_correlations(self, df, method='pearson'):
        """Analisar correlações entre variáveis"""
        # Selecionar apenas colunas numéricas
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        
        # Calcular matriz de correlação
        self.correlations = numeric_df.corr(method=method)
        
        # Identificar correlações fortes (positivas e negativas)
        strong_correlations = []
        
        for i in range(len(self.correlations.columns)):
            for j in range(i+1, len(self.correlations.columns)):
                col1 = self.correlations.columns[i]
                col2 = self.correlations.columns[j]
                corr = self.correlations.iloc[i, j]
                
                if abs(corr) > 0.7:  # Limiar para correlação forte
                    strong_correlations.append((col1, col2, corr))
        
        return self.correlations, strong_correlations
    
    def perform_clustering(self, df, n_clusters=3, algorithm='kmeans'):
        """Realizar clustering nos dados"""
        # Selecionar apenas colunas numéricas
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        
        # Normalizar os dados
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df)
        
        # Aplicar algoritmo de clustering
        if algorithm == 'kmeans':
            model = KMeans(n_clusters=n_clusters, random_state=42)
            labels = model.fit_predict(scaled_data)
            
            # Calcular centróides
            centroids = model.cluster_centers_
            
            # Transformar centróides de volta para a escala original
            original_centroids = scaler.inverse_transform(centroids)
            
            self.clusters = {
                'labels': labels,
                'centroids': original_centroids,
                'model': model,
                'columns': numeric_df.columns.tolist()
            }
        
        elif algorithm == 'dbscan':
            model = DBSCAN(eps=0.5, min_samples=5)
            labels = model.fit_predict(scaled_data)
            
            self.clusters = {
                'labels': labels,
                'model': model,
                'columns': numeric_df.columns.tolist()
            }
        
        # Adicionar rótulos de cluster ao DataFrame
        df_with_clusters = df.copy()
        df_with_clusters['cluster'] = labels
        
        return df_with_clusters, self.clusters
    
    def detect_anomalies(self, df, contamination=0.05):
        """Detectar anomalias nos dados"""
        from sklearn.ensemble import IsolationForest
        
        # Selecionar apenas colunas numéricas
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        
        # Normalizar os dados
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df)
        
        # Aplicar Isolation Forest
        model = IsolationForest(contamination=contamination, random_state=42)
        labels = model.fit_predict(scaled_data)
        
        # Converter para formato mais intuitivo (1: normal, -1: anomalia)
        anomaly_indices = df.index[labels == -1].tolist()
        
        self.anomalies = {
            'indices': anomaly_indices,
            'count': len(anomaly_indices),
            'percentage': (len(anomaly_indices) / len(df)) * 100
        }
        
        return anomaly_indices, self.anomalies
    
    def find_patterns(self, df):
        """Encontrar padrões interessantes nos dados"""
        patterns = []
        
        # Analisar distribuições
        for col in df.select_dtypes(include=['int64', 'float64']).columns:
            # Verificar se a distribuição é normal
            _, p_value = stats.normaltest(df[col].dropna())
            if p_value > 0.05:
                patterns.append(f"A coluna '{col}' segue uma distribuição aproximadamente normal (p-value: {p_value:.4f})")
            
            # Verificar assimetria
            skewness = df[col].skew()
            if abs(skewness) > 1:
                direction = "positiva" if skewness > 0 else "negativa"
                patterns.append(f"A coluna '{col}' apresenta forte assimetria {direction} ({skewness:.2f})")
        
        # Analisar valores categóricos
        for col in df.select_dtypes(include=['object', 'category']).columns:
            # Verificar se há um valor dominante
            value_counts = df[col].value_counts(normalize=True)
            if value_counts.iloc[0] > 0.8:
                patterns.append(f"A coluna '{col}' é dominada pelo valor '{value_counts.index[0]}' ({value_counts.iloc[0]*100:.1f}%)")
            
            # Verificar cardinalidade
            if len(value_counts) > 100:
                patterns.append(f"A coluna '{col}' tem alta cardinalidade ({len(value_counts)} valores únicos)")
        
        # Analisar valores ausentes
        missing_cols = df.columns[df.isnull().any()].tolist()
        if missing_cols:
            for col in missing_cols:
                missing_pct = df[col].isnull().mean() * 100
                patterns.append(f"A coluna '{col}' tem {missing_pct:.1f}% de valores ausentes")
        
        return patterns

class AIDialog(tk.Toplevel):
    """Diálogo principal para funcionalidades de IA"""
    def __init__(self, parent, data, columns):
        super().__init__(parent)
        self.title("Análise de IA e Aprendizado de Máquina")
        self.geometry("1000x700")
        self.transient(parent)
        
        self.data = data
        self.columns = columns
        self.df = pd.DataFrame(data)
        
        # Inicializar componentes
        self.model_manager = AIModelManager()
        self.preprocessor = DataPreprocessor()
        self.pattern_detector = PatternDetector()
        
        # Variáveis de estado
        self.task_type = tk.StringVar(value="classification")
        self.target_column = tk.StringVar()
        self.selected_model = tk.StringVar()
        self.test_size = tk.DoubleVar(value=0.2)
        self.current_tab = tk.StringVar()
        
        # Configurar a interface
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de análise exploratória
        self.setup_exploratory_tab()
        
        # Aba de detecção de padrões
        self.setup_pattern_detection_tab()
        
        # Aba de modelagem preditiva
        self.setup_predictive_modeling_tab()
        
        # Aba de insights automáticos
        self.setup_insights_tab()
        
        # Barra de status
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        # Vincular evento de mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
    
    def setup_exploratory_tab(self):
        """Configurar a aba de análise exploratória"""
        exploratory_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(exploratory_frame, text="Análise Exploratória")
        
        # Frame superior para controles
        control_frame = ttk.LabelFrame(exploratory_frame, text="Controles", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Seleção de visualização
        viz_frame = ttk.Frame(control_frame)
        viz_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(viz_frame, text="Tipo de Visualização:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.viz_type_var = tk.StringVar(value="histogram")
        viz_types = ["histogram", "boxplot", "scatter", "correlation", "pairplot"]
        viz_combo = ttk.Combobox(viz_frame, textvariable=self.viz_type_var, values=viz_types, state="readonly")
        viz_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Seleção de coluna(s)
        col_frame = ttk.Frame(control_frame)
        col_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(col_frame, text="Coluna(s):").pack(side=tk.LEFT, padx=(0, 5))
        
        self.col1_var = tk.StringVar()
        col1_combo = ttk.Combobox(col_frame, textvariable=self.col1_var, values=self.columns, state="readonly")
        col1_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.col2_var = tk.StringVar()
        col2_combo = ttk.Combobox(col_frame, textvariable=self.col2_var, values=self.columns, state="readonly")
        col2_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botão para gerar visualização
        ttk.Button(control_frame, text="Gerar Visualização", command=self.generate_visualization).pack(pady=10)
        
        # Frame para a visualização
        self.viz_container = ttk.LabelFrame(exploratory_frame, text="Visualização", padding=10)
        self.viz_container.pack(fill=tk.BOTH, expand=True)
        
        # Vincular eventos de mudança
        self.viz_type_var.trace("w", self.update_column_selection)
    
    def setup_pattern_detection_tab(self):
        """Configurar a aba de detecção de padrões"""
        pattern_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(pattern_frame, text="Detecção de Padrões")
        
        # Frame superior para controles
        control_frame = ttk.LabelFrame(pattern_frame, text="Controles", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Seleção de tipo de análise
        analysis_frame = ttk.Frame(control_frame)
        analysis_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(analysis_frame, text="Tipo de Análise:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.analysis_type_var = tk.StringVar(value="outliers")
        analysis_types = ["outliers", "correlations", "clustering", "anomalies", "patterns"]
        analysis_combo = ttk.Combobox(analysis_frame, textvariable=self.analysis_type_var, values=analysis_types, state="readonly")
        analysis_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Frame para opções específicas
        self.pattern_options_frame = ttk.Frame(control_frame)
        self.pattern_options_frame.pack(fill=tk.X, pady=5)
        
        # Botão para executar análise
        ttk.Button(control_frame, text="Executar Análise", command=self.run_pattern_analysis).pack(pady=10)
        
        # Frame para resultados
        results_frame = ttk.Frame(pattern_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para resultados
        self.pattern_notebook = ttk.Notebook(results_frame)
        self.pattern_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de visualização
        self.pattern_viz_frame = ttk.Frame(self.pattern_notebook, padding=10)
        self.pattern_notebook.add(self.pattern_viz_frame, text="Visualização")
        
        # Aba de detalhes
        self.pattern_details_frame = ttk.Frame(self.pattern_notebook, padding=10)
        self.pattern_notebook.add(self.pattern_details_frame, text="Detalhes")
        
        # Vincular eventos de mudança
        self.analysis_type_var.trace("w", self.update_pattern_options)
        
        # Inicializar opções
        self.update_pattern_options()
    
    def setup_predictive_modeling_tab(self):
        """Configurar a aba de modelagem preditiva"""
        modeling_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(modeling_frame, text="Modelagem Preditiva")
        
        # Frame superior para controles
        control_frame = ttk.LabelFrame(modeling_frame, text="Configuração do Modelo", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tipo de tarefa
        task_frame = ttk.Frame(control_frame)
        task_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(task_frame, text="Tipo de Tarefa:").pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Radiobutton(task_frame, text="Classificação", variable=self.task_type, value="classification").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(task_frame, text="Regressão", variable=self.task_type, value="regression").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(task_frame, text="Clustering", variable=self.task_type, value="clustering").pack(side=tk.LEFT)
        
        # Seleção de coluna alvo
        target_frame = ttk.Frame(control_frame)
        target_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(target_frame, text="Coluna Alvo:").pack(side=tk.LEFT, padx=(0, 5))
        
        target_combo = ttk.Combobox(target_frame, textvariable=self.target_column, values=self.columns, state="readonly")
        target_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Seleção de modelo
        model_frame = ttk.Frame(control_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(model_frame, text="Modelo:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.selected_model, state="readonly")
        self.model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Tamanho do conjunto de teste
        test_frame = ttk.Frame(control_frame)
        test_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(test_frame, text="Tamanho do Teste (%):").pack(side=tk.LEFT, padx=(0, 5))
        
        test_scale = ttk.Scale(test_frame, from_=10, to=50, variable=self.test_size, orient=tk.HORIZONTAL)
        test_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        test_label = ttk.Label(test_frame, textvariable=tk.StringVar(value="20%"))
        test_label.pack(side=tk.LEFT)
        
        # Atualizar o rótulo quando o valor mudar
        def update_test_label(*args):
            test_label.config(text=f"{int(self.test_size.get())}%")
        
        self.test_size.trace("w", update_test_label)
        
        # Botões de ação
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Treinar Modelo", command=self.train_model).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Salvar Modelo", command=self.save_model).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Carregar Modelo", command=self.load_model).pack(side=tk.LEFT)
        
        # Frame para resultados
        results_frame = ttk.LabelFrame(modeling_frame, text="Resultados do Modelo", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para resultados
        self.model_notebook = ttk.Notebook(results_frame)
        self.model_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de métricas
        self.metrics_frame = ttk.Frame(self.model_notebook, padding=10)
        self.model_notebook.add(self.metrics_frame, text="Métricas")
        
        # Aba de visualização
        self.model_viz_frame = ttk.Frame(self.model_notebook, padding=10)
        self.model_notebook.add(self.model_viz_frame, text="Visualização")
        
        # Aba de importância de características
        self.feature_importance_frame = ttk.Frame(self.model_notebook, padding=10)
        self.model_notebook.add(self.feature_importance_frame, text="Importância de Características")
        
        # Aba de previsões
        self.predictions_frame = ttk.Frame(self.model_notebook, padding=10)
        self.model_notebook.add(self.predictions_frame, text="Previsões")
        
        # Vincular eventos de mudança
        self.task_type.trace("w", self.update_model_list)
        
        # Inicializar lista de modelos
        self.update_model_list()
    
    def setup_insights_tab(self):
        """Configurar a aba de insights automáticos"""
        insights_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(insights_frame, text="Insights Automáticos")
        
        # Frame superior para controles
        control_frame = ttk.LabelFrame(insights_frame, text="Controles", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botão para gerar insights
        ttk.Button(control_frame, text="Gerar Insights", command=self.generate_insights).pack(pady=5)
        
        # Frame para resultados
        self.insights_container = ttk.LabelFrame(insights_frame, text="Insights Descobertos", padding=10)
        self.insights_container.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto para insights
        self.insights_text = tk.Text(self.insights_container, wrap=tk.WORD, padx=10, pady=10)
        self.insights_text.pack(fill=tk.BOTH, expand=True)
        
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(self.insights_text, command=self.insights_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.insights_text.config(yscrollcommand=scrollbar.set)
        
        # Configurar tags para formatação
        self.insights_text.tag_configure("heading", font=("Helvetica", 12, "bold"))
        self.insights_text.tag_configure("subheading", font=("Helvetica", 10, "bold"))
        self.insights_text.tag_configure("normal", font=("Helvetica", 10))
        self.insights_text.tag_configure("highlight", font=("Helvetica", 10, "bold"), foreground="blue")
        self.insights_text.tag_configure("warning", font=("Helvetica", 10, "bold"), foreground="red")
        self.insights_text.tag_configure("success", font=("Helvetica", 10, "bold"), foreground="green")
    
    def on_tab_change(self, event):
        """Manipular mudança de aba"""
        tab_id = self.notebook.select()
        tab_name = self.notebook.tab(tab_id, "text")
        self.current_tab.set(tab_name)
    
    def update_column_selection(self, *args):
        """Atualizar seleção de colunas com base no tipo de visualização"""
        viz_type = self.viz_type_var.get()
        
        if viz_type in ["histogram", "boxplot"]:
            # Habilitar apenas a primeira coluna
            self.col2_var.set("")
        elif viz_type == "correlation":
            # Desabilitar seleção de colunas
            self.col1_var.set("")
            self.col2_var.set("")
    
    def generate_visualization(self):
        """Gerar visualização com base nas seleções"""
        viz_type = self.viz_type_var.get()
        col1 = self.col1_var.get()
        col2 = self.col2_var.get()
        
        # Limpar o container
        for widget in self.viz_container.winfo_children():
            widget.destroy()
        
        # Criar figura
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        
        try:
            if viz_type == "histogram":
                if not col1:
                    messagebox.showwarning("Aviso", "Selecione uma coluna para o histograma.")
                    return
                
                # Verificar se a coluna é numérica
                if self.df[col1].dtype in ['int64', 'float64']:
                    sns.histplot(data=self.df, x=col1, kde=True, ax=ax)
                    ax.set_title(f"Histograma de {col1}")
                else:
                    # Para colunas categóricas, usar countplot
                    sns.countplot(data=self.df, x=col1, ax=ax)
                    ax.set_title(f"Contagem de {col1}")
                    plt.xticks(rotation=45, ha='right')
            
            elif viz_type == "boxplot":
                if not col1:
                    messagebox.showwarning("Aviso", "Selecione uma coluna para o boxplot.")
                    return
                
                # Verificar se a coluna é numérica
                if self.df[col1].dtype in ['int64', 'float64']:
                    sns.boxplot(data=self.df, y=col1, ax=ax)
                    ax.set_title(f"Boxplot de {col1}")
                else:
                    messagebox.showwarning("Aviso", "Boxplot requer uma coluna numérica.")
                    return
            
            elif viz_type == "scatter":
                if not col1 or not col2:
                    messagebox.showwarning("Aviso", "Selecione duas colunas para o gráfico de dispersão.")
                    return
                
                # Verificar se ambas as colunas são numéricas
                if self.df[col1].dtype in ['int64', 'float64'] and self.df[col2].dtype in ['int64', 'float64']:
                    sns.scatterplot(data=self.df, x=col1, y=col2, ax=ax)
                    ax.set_title(f"Dispersão: {col1} vs {col2}")
                else:
                    messagebox.showwarning("Aviso", "Gráfico de dispersão requer duas colunas numéricas.")
                    return
            
            elif viz_type == "correlation":
                # Selecionar apenas colunas numéricas
                numeric_df = self.df.select_dtypes(include=['int64', 'float64'])
                
                if numeric_df.shape[1] < 2:
                    messagebox.showwarning("Aviso", "São necessárias pelo menos duas colunas numéricas para a matriz de correlação.")
                    return
                
                # Calcular correlação
                corr = numeric_df.corr()
                
                # Criar mapa de calor
                sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, ax=ax)
                ax.set_title("Matriz de Correlação")
            
            elif viz_type == "pairplot":
                # Criar pairplot em uma nova figura
                plt.close(fig)  # Fechar a figura atual
                
                # Selecionar apenas colunas numéricas
                numeric_df = self.df.select_dtypes(include=['int64', 'float64'])
                
                if numeric_df.shape[1] < 2:
                    messagebox.showwarning("Aviso", "São necessárias pelo menos duas colunas numéricas para o pairplot.")
                    return
                
                # Limitar a 5 colunas para evitar gráficos muito grandes
                if numeric_df.shape[1] > 5:
                    numeric_df = numeric_df.iloc[:, :5]
                    messagebox.showinfo("Informação", "Limitando a 5 colunas para melhor visualização.")
                
                # Criar pairplot
                g = sns.pairplot(numeric_df)
                g.fig.suptitle("Matriz de Gráficos de Dispersão", y=1.02)
                
                # Criar canvas para o pairplot
                canvas = FigureCanvasTkAgg(g.fig, master=self.viz_container)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                return  # Retornar para evitar adicionar o canvas padrão
            
            plt.tight_layout()
            
            # Adicionar canvas ao frame
            canvas = FigureCanvasTkAgg(fig, master=self.viz_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.status_var.set(f"Visualização gerada: {viz_type}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar visualização:\n{str(e)}")
            logger.error(f"Erro ao gerar visualização: {str(e)}")
    
    def update_pattern_options(self, *args):
        """Atualizar opções com base no tipo de análise de padrão selecionado"""
        analysis_type = self.analysis_type_var.get()
        
        # Limpar o frame de opções
        for widget in self.pattern_options_frame.winfo_children():
            widget.destroy()
        
        if analysis_type == "outliers":
            # Opções para detecção de outliers
            ttk.Label(self.pattern_options_frame, text="Método:").pack(side=tk.LEFT, padx=(0, 5))
            
            self.outlier_method_var = tk.StringVar(value="zscore")
            methods = ["zscore", "iqr"]
            method_combo = ttk.Combobox(self.pattern_options_frame, textvariable=self.outlier_method_var, values=methods, state="readonly", width=10)
            method_combo.pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Label(self.pattern_options_frame, text="Limiar:").pack(side=tk.LEFT, padx=(0, 5))
            
            self.outlier_threshold_var = tk.DoubleVar(value=3.0)
            threshold_entry = ttk.Entry(self.pattern_options_frame, textvariable=self.outlier_threshold_var, width=5)
            threshold_entry.pack(side=tk.LEFT)
        
        elif analysis_type == "clustering":
            # Opções para clustering
            ttk.Label(self.pattern_options_frame, text="Algoritmo:").pack(side=tk.LEFT, padx=(0, 5))
            
            self.cluster_algorithm_var = tk.StringVar(value="kmeans")
            algorithms = ["kmeans", "dbscan"]
            algorithm_combo = ttk.Combobox(self.pattern_options_frame, textvariable=self.cluster_algorithm_var, values=algorithms, state="readonly", width=10)
            algorithm_combo.pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Label(self.pattern_options_frame, text="Número de Clusters:").pack(side=tk.LEFT, padx=(0, 5))
            
            self.n_clusters_var = tk.IntVar(value=3)
            clusters_entry = ttk.Entry(self.pattern_options_frame, textvariable=self.n_clusters_var, width=5)
            clusters_entry.pack(side=tk.LEFT)
        
        elif analysis_type == "anomalies":
            # Opções para detecção de anomalias
            ttk.Label(self.pattern_options_frame, text="Contaminação (%):").pack(side=tk.LEFT, padx=(0, 5))
            
            self.contamination_var = tk.DoubleVar(value=5.0)
            contamination_entry = ttk.Entry(self.pattern_options_frame, textvariable=self.contamination_var, width=5)
            contamination_entry.pack(side=tk.LEFT)
    
    def run_pattern_analysis(self):
        """Executar análise de padrões com base nas seleções"""
        analysis_type = self.analysis_type_var.get()
        
        # Limpar frames de resultados
        for widget in self.pattern_viz_frame.winfo_children():
            widget.destroy()
        
        for widget in self.pattern_details_frame.winfo_children():
            widget.destroy()
        
        try:
            if analysis_type == "outliers":
                # Obter parâmetros
                method = self.outlier_method_var.get()
                threshold = self.outlier_threshold_var.get()
                
                # Detectar outliers
                outliers = self.pattern_detector.detect_outliers(self.df, method=method, threshold=threshold)
                
                # Criar visualização
                fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
                
                # Selecionar colunas numéricas com outliers
                numeric_cols = [col for col in outliers.keys() if len(outliers[col]) > 0 and self.df[col].dtype in ['int64', 'float64']]
                
                if not numeric_cols:
                    messagebox.showinfo("Informação", "Nenhum outlier encontrado com os parâmetros atuais.")
                    return
                
                # Limitar a 4 colunas para melhor visualização
                if len(numeric_cols) > 4:
                    numeric_cols = numeric_cols[:4]
                
                # Criar subplots
                fig, axes = plt.subplots(len(numeric_cols), 1, figsize=(10, 3*len(numeric_cols)), dpi=100)
                if len(numeric_cols) == 1:
                    axes = [axes]
                
                for i, col in enumerate(numeric_cols):
                    # Criar boxplot
                    sns.boxplot(x=self.df[col], ax=axes[i])
                    axes[i].set_title(f"Outliers em {col}")
                    
                    # Destacar outliers
                    if outliers[col]:
                        outlier_values = self.df.loc[outliers[col], col]
                        axes[i].scatter(outlier_values, [0] * len(outlier_values), color='red', s=20, label='Outliers')
                        axes[i].legend()
                
                plt.tight_layout()
                
                # Adicionar canvas ao frame
                canvas = FigureCanvasTkAgg(fig, master=self.pattern_viz_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                # Adicionar detalhes
                details_text = tk.Text(self.pattern_details_frame, wrap=tk.WORD, padx=10, pady=10)
                details_text.pack(fill=tk.BOTH, expand=True)
                
                details_text.insert(tk.END, f"Método de detecção: {method.upper()}\n")
                details_text.insert(tk.END, f"Limiar: {threshold}\n\n")
                
                total_outliers = sum(len(outliers[col]) for col in outliers)
                details_text.insert(tk.END, f"Total de outliers encontrados: {total_outliers}\n\n")
                
                for col in outliers:
                    if outliers[col]:
                        details_text.insert(tk.END, f"Coluna '{col}': {len(outliers[col])} outliers\n")
                        
                        # Mostrar valores dos outliers
                        outlier_values = self.df.loc[outliers[col], col].tolist()
                        details_text.insert(tk.END, f"Valores: {', '.join(map(str, outlier_values[:10]))}")
                        if len(outlier_values) > 10:
                            details_text.insert(tk.END, f" e mais {len(outlier_values) - 10} valores\n")
                        else:
                            details_text.insert(tk.END, "\n")
                    
                details_text.config(state=tk.DISABLED)
            
            elif analysis_type == "correlations":
                # Analisar correlações
                correlations, strong_correlations = self.pattern_detector.analyze_correlations(self.df)
                
                # Criar visualização
                fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
                
                # Selecionar apenas colunas numéricas
                numeric_df = self.df.select_dtypes(include=['int64', 'float64'])
                
                if numeric_df.shape[1] < 2:
                    messagebox.showwarning("Aviso", "São necessárias pelo menos duas colunas numéricas para a análise de correlação.")
                    return
                
                # Criar mapa de calor
                sns.heatmap(correlations, annot=True, cmap='coolwarm', vmin=-1, vmax=1, ax=ax)
                ax.set_title("Matriz de Correlação")
                
                plt.tight_layout()
                
                # Adicionar canvas ao frame
                canvas = FigureCanvasTkAgg(fig, master=self.pattern_viz_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                # Adicionar detalhes
                details_text = tk.Text(self.pattern_details_frame, wrap=tk.WORD, padx=10, pady=10)
                details_text.pack(fill=tk.BOTH, expand=True)
                
                details_text.insert(tk.END, "Análise de Correlação\n\n")
                
                if strong_correlations:
                    details_text.insert(tk.END, "Correlações Fortes (|r| > 0.7):\n\n")
                    
                    for col1, col2, corr in strong_correlations:
                        corr_type = "positiva" if corr > 0 else "negativa"
                        details_text.insert(tk.END, f"• {col1} e {col2}: {corr:.3f} (correlação {corr_type})\n")
                else:
                    details_text.insert(tk.END, "Nenhuma correlação forte encontrada (|r| > 0.7).\n")
                
                details_text.config(state=tk.DISABLED)
            
            elif analysis_type == "clustering":
                # Obter parâmetros
                algorithm = self.cluster_algorithm_var.get()
                n_clusters = self.n_clusters_var.get()
                
                # Realizar clustering
                df_with_clusters, clusters = self.pattern_detector.perform_clustering(self.df, n_clusters=n_clusters, algorithm=algorithm)
                
                # Criar visualização
                if algorithm == "kmeans":
                    # Usar PCA para reduzir para 2 dimensões
                    numeric_df = self.df.select_dtypes(include=['int64', 'float64'])
                    
                    if numeric_df.shape[1] < 2:
                        messagebox.showwarning("Aviso", "São necessárias pelo menos duas colunas numéricas para clustering.")
                        return
                    
                    # Normalizar os dados
                    scaler = StandardScaler()
                    scaled_data = scaler.fit_transform(numeric_df)
                    
                    # Aplicar PCA
                    pca = PCA(n_components=2)
                    pca_result = pca.fit_transform(scaled_data)
                    
                    # Criar DataFrame com resultados do PCA
                    pca_df = pd.DataFrame(data=pca_result, columns=['PC1', 'PC2'])
                    pca_df['cluster'] = clusters['labels']
                    
                    # Criar visualização
                    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
                    
                    # Plotar pontos
                    sns.scatterplot(data=pca_df, x='PC1', y='PC2', hue='cluster', palette='viridis', ax=ax)
                    
                    # Plotar centróides
                    centroids_pca = pca.transform(scaler.transform(clusters['centroids']))
                    ax.scatter(centroids_pca[:, 0], centroids_pca[:, 1], s=200, marker='X', color='red', edgecolor='black', label='Centróides')
                    
                    ax.set_title(f"Clustering K-Means (k={n_clusters})")
                    ax.legend()
                    
                    plt.tight_layout()
                    
                    # Adicionar canvas ao frame
                    canvas = FigureCanvasTkAgg(fig, master=self.pattern_viz_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                    
                    # Adicionar detalhes
                    details_text = tk.Text(self.pattern_details_frame, wrap=tk.WORD, padx=10, pady=10)
                    details_text.pack(fill=tk.BOTH, expand=True)
                    
                    details_text.insert(tk.END, f"Clustering K-Means (k={n_clusters})\n\n")
                    
                    # Informações sobre os clusters
                    cluster_counts = pd.Series(clusters['labels']).value_counts().sort_index()
                    
                    details_text.insert(tk.END, "Distribuição de Clusters:\n\n")
                    
                    for cluster, count in cluster_counts.items():
                        percentage = (count / len(self.df)) * 100
                        details_text.insert(tk.END, f"• Cluster {cluster}: {count} pontos ({percentage:.1f}%)\n")
                    
                    details_text.insert(tk.END, "\nCentróides dos Clusters:\n\n")
                    
                    for i, centroid in enumerate(clusters['centroids']):
                        details_text.insert(tk.END, f"Cluster {i}:\n")
                        for j, col in enumerate(clusters['columns']):
                            details_text.insert(tk.END, f"  • {col}: {centroid[j]:.3f}\n")
                    
                    details_text.config(state=tk.DISABLED)
                
                else:  # DBSCAN
                    # Usar PCA para reduzir para 2 dimensões
                    numeric_df = self.df.select_dtypes(include=['int64', 'float64'])
                    
                    if numeric_df.shape[1] < 2:
                        messagebox.showwarning("Aviso", "São necessárias pelo menos duas colunas numéricas para clustering.")
                        return
                    
                    # Normalizar os dados
                    scaler = StandardScaler()
                    scaled_data = scaler.fit_transform(numeric_df)
                    
                    # Aplicar PCA
                    pca = PCA(n_components=2)
                    pca_result = pca.fit_transform(scaled_data)
                    
                    # Criar DataFrame com resultados do PCA
                    pca_df = pd.DataFrame(data=pca_result, columns=['PC1', 'PC2'])
                    pca_df['cluster'] = clusters['labels']
                    
                    # Criar visualização
                    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
                    
                    # Plotar pontos
                    sns.scatterplot(data=pca_df, x='PC1', y='PC2', hue='cluster', palette='viridis', ax=ax)
                    
                    ax.set_title(f"Clustering DBSCAN")
                    ax.legend()
                    
                    plt.tight_layout()
                    
                    # Adicionar canvas ao frame
                    canvas = FigureCanvasTkAgg(fig, master=self.pattern_viz_frame)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                    
                    # Adicionar detalhes
                    details_text = tk.Text(self.pattern_details_frame, wrap=tk.WORD, padx=10, pady=10)
                    details_text.pack(fill=tk.BOTH, expand=True)
                    
                    details_text.insert(tk.END, "Clustering DBSCAN\n\n")
                    
                    # Informações sobre os clusters
                    cluster_counts = pd.Series(clusters['labels']).value_counts().sort_index()
                    
                    details_text.insert(tk.END, "Distribuição de Clusters:\n\n")
                    
                    for cluster, count in cluster_counts.items():
                        cluster_name = "Ruído" if cluster == -1 else f"Cluster {cluster}"
                        percentage = (count / len(self.df)) * 100
                        details_text.insert(tk.END, f"• {cluster_name}: {count} pontos ({percentage:.1f}%)\n")
                    
                    details_text.config(state=tk.DISABLED)
            
            elif analysis_type == "anomalies":
                # Obter parâmetros
                contamination = self.contamination_var.get() / 100.0
                
                # Detectar anomalias
                anomaly_indices, anomalies = self.pattern_detector.detect_anomalies(self.df, contamination=contamination)
                
                # Criar visualização
                # Usar PCA para reduzir para 2 dimensões
                numeric_df = self.df.select_dtypes(include=['int64', 'float64'])
                
                if numeric_df.shape[1] < 2:
                    messagebox.showwarning("Aviso", "São necessárias pelo menos duas colunas numéricas para detecção de anomalias.")
                    return
                
                # Normalizar os dados
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(numeric_df)
                
                # Aplicar PCA
                pca = PCA(n_components=2)
                pca_result = pca.fit_transform(scaled_data)
                
                # Criar DataFrame com resultados do PCA
                pca_df = pd.DataFrame(data=pca_result, columns=['PC1', 'PC2'])
                pca_df['anomaly'] = 0
                pca_df.loc[anomaly_indices, 'anomaly'] = 1
                
                # Criar visualização
                fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
                
                # Plotar pontos normais
                normal_df = pca_df[pca_df['anomaly'] == 0]
                ax.scatter(normal_df['PC1'], normal_df['PC2'], c='blue', label='Normal', alpha=0.5)
                
                # Plotar anomalias
                anomaly_df = pca_df[pca_df['anomaly'] == 1]
                ax.scatter(anomaly_df['PC1'], anomaly_df['PC2'], c='red', label='Anomalia', alpha=0.7)
                
                ax.set_title(f"Detecção de Anomalias (Isolation Forest)")
                ax.legend()
                
                plt.tight_layout()
                
                # Adicionar canvas ao frame
                canvas = FigureCanvasTkAgg(fig, master=self.pattern_viz_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                # Adicionar detalhes
                details_text = tk.Text(self.pattern_details_frame, wrap=tk.WORD, padx=10, pady=10)
                details_text.pack(fill=tk.BOTH, expand=True)
                
                details_text.insert(tk.END, "Detecção de Anomalias (Isolation Forest)\n\n")
                details_text.insert(tk.END, f"Contaminação: {contamination*100:.1f}%\n\n")
                
                details_text.insert(tk.END, f"Total de anomalias encontradas: {anomalies['count']} ({anomalies['percentage']:.1f}%)\n\n")
                
                # Mostrar alguns exemplos de anomalias
                if anomaly_indices:
                    details_text.insert(tk.END, "Exemplos de Anomalias:\n\n")
                    
                    # Mostrar até 10 exemplos
                    sample_indices = anomaly_indices[:min(10, len(anomaly_indices))]
                    
                    for i, idx in enumerate(sample_indices):
                        details_text.insert(tk.END, f"Anomalia {i+1} (índice {idx}):\n")
                        
                        # Mostrar valores para colunas numéricas
                        for col in numeric_df.columns:
                            value = self.df.loc[idx, col]
                            details_text.insert(tk.END, f"  • {col}: {value}\n")
                        
                        details_text.insert(tk.END, "\n")
                
                details_text.config(state=tk.DISABLED)
            
            elif analysis_type == "patterns":
                # Encontrar padrões
                patterns = self.pattern_detector.find_patterns(self.df)
                
                # Criar visualização
                # Mostrar distribuições de algumas colunas numéricas
                numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                
                if not numeric_cols:
                    messagebox.showwarning("Aviso", "Nenhuma coluna numérica encontrada para análise de padrões.")
                    return
                
                # Limitar a 4 colunas para melhor visualização
                if len(numeric_cols) > 4:
                    numeric_cols = numeric_cols[:4]
                
                # Criar subplots
                fig, axes = plt.subplots(len(numeric_cols), 1, figsize=(10, 3*len(numeric_cols)), dpi=100)
                if len(numeric_cols) == 1:
                    axes = [axes]
                
                for i, col in enumerate(numeric_cols):
                    # Criar histograma com KDE
                    sns.histplot(self.df[col], kde=True, ax=axes[i])
                    axes[i].set_title(f"Distribuição de {col}")
                
                plt.tight_layout()
                
                # Adicionar canvas ao frame
                canvas = FigureCanvasTkAgg(fig, master=self.pattern_viz_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                # Adicionar detalhes
                details_text = tk.Text(self.pattern_details_frame, wrap=tk.WORD, padx=10, pady=10)
                details_text.pack(fill=tk.BOTH, expand=True)
                
                details_text.insert(tk.END, "Padrões Encontrados\n\n")
                
                if patterns:
                    for pattern in patterns:
                        details_text.insert(tk.END, f"• {pattern}\n")
                else:
                    details_text.insert(tk.END, "Nenhum padrão significativo encontrado.\n")
                
                details_text.config(state=tk.DISABLED)
            
            self.status_var.set(f"Análise concluída: {analysis_type}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar análise:\n{str(e)}")
            logger.error(f"Erro ao executar análise: {str(e)}")
    
    def update_model_list(self, *args):
        """Atualizar lista de modelos com base no tipo de tarefa"""
        task_type = self.task_type.get()
        
        # Obter modelos disponíveis
        models = self.model_manager.get_available_models(task_type)
        
        # Atualizar combobox
        self.model_combo.config(values=models)
        
        # Selecionar o primeiro modelo
        if models:
            self.selected_model.set(models[0])
    
    def train_model(self):
        """Treinar modelo com base nas seleções"""
        task_type = self.task_type.get()
        model_name = self.selected_model.get()
        target_column = self.target_column.get()
        test_size = self.test_size.get() / 100.0
        
        # Validar seleções
        if not model_name:
            messagebox.showwarning("Aviso", "Selecione um modelo para treinar.")
            return
        
        if task_type in ["classification", "regression"] and not target_column:
            messagebox.showwarning("Aviso", "Selecione uma coluna alvo para o modelo.")
            return
        
        # Iniciar treinamento em uma thread separada
        self.status_var.set("Treinando modelo...")
        
        # Limpar frames de resultados
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
        
        for widget in self.model_viz_frame.winfo_children():
            widget.destroy()
        
        for widget in self.feature_importance_frame.winfo_children():
            widget.destroy()
        
        for widget in self.predictions_frame.winfo_children():
            widget.destroy()
        
        # Criar barra de progresso
        progress_frame = ttk.Frame(self.metrics_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, mode="indeterminate")
        progress_bar.pack(fill=tk.X)
        progress_bar.start()
        
        status_label = ttk.Label(progress_frame, text="Preparando dados...")
        status_label.pack(pady=5)
        
        # Função para treinar o modelo em uma thread separada
        def train_thread():
            try:
                # Atualizar status
                self.root.after(0, lambda: status_label.config(text="Pré-processando dados..."))
                
                # Pré-processar dados
                X, y = self.preprocessor.preprocess_data(self.df, target_column=target_column if task_type != "clustering" else None)
                
                # Atualizar status
                self.root.after(0, lambda: status_label.config(text="Treinando modelo..."))
                
                # Treinar modelo
                model, metrics = self.model_manager.train_model(task_type, model_name, X, y, test_size=test_size)
                
                # Atualizar status
                self.root.after(0, lambda: status_label.config(text="Gerando visualizações..."))
                
                # Atualizar interface com resultados
                self.root.after(0, lambda: self.update_model_results(task_type, model_name, metrics))
                
                # Atualizar status
                self.root.after(0, lambda: self.status_var.set(f"Modelo treinado: {model_name}"))
            
            except Exception as e:
                # Mostrar erro
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao treinar modelo:\n{str(e)}"))
                logger.error(f"Erro ao treinar modelo: {str(e)}")
            
            finally:
                # Parar barra de progresso
                self.root.after(0, lambda: progress_bar.stop())
                self.root.after(0, lambda: progress_frame.destroy())
        
        # Iniciar thread
        threading.Thread(target=train_thread, daemon=True).start()
    
    def update_model_results(self, task_type, model_name, metrics):
        """Atualizar interface com resultados do modelo"""
        # Limpar frames de resultados
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
        
        for widget in self.model_viz_frame.winfo_children():
            widget.destroy()
        
        for widget in self.feature_importance_frame.winfo_children():
            widget.destroy()
        
        for widget in self.predictions_frame.winfo_children():
            widget.destroy()
        
        # Mostrar métricas
        if task_type == "classification":
            # Métricas de classificação
            metrics_frame = ttk.Frame(self.metrics_frame)
            metrics_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Criar tabela de métricas
            metrics_table = ttk.Treeview(metrics_frame, columns=["metric", "value"], show="headings")
            metrics_table.heading("metric", text="Métrica")
            metrics_table.heading("value", text="Valor")
            metrics_table.column("metric", width=150)
            metrics_table.column("value", width=100)
            metrics_table.pack(fill=tk.BOTH, expand=True)
            
            # Adicionar métricas
            metrics_table.insert("", tk.END, values=["Acurácia", f"{metrics['accuracy']:.4f}"])
            metrics_table.insert("", tk.END, values=["Precisão", f"{metrics['precision']:.4f}"])
            metrics_table.insert("", tk.END, values=["Recall", f"{metrics['recall']:.4f}"])
            metrics_table.insert("", tk.END, values=["F1-Score", f"{metrics['f1']:.4f}"])
            
            # Visualização - Matriz de confusão
            fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
            
            # Plotar matriz de confusão
            sns.heatmap(metrics['confusion_matrix'], annot=True, fmt="d", cmap="Blues", ax=ax)
            ax.set_title("Matriz de Confusão")
            ax.set_xlabel("Previsto")
            ax.set_ylabel("Real")
            
            plt.tight_layout()
            
            # Adicionar canvas ao frame
            canvas = FigureCanvasTkAgg(fig, master=self.model_viz_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        elif task_type == "regression":
            # Métricas de regressão
            metrics_frame = ttk.Frame(self.metrics_frame)
            metrics_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Criar tabela de métricas
            metrics_table = ttk.Treeview(metrics_frame, columns=["metric", "value"], show="headings")
            metrics_table.heading("metric", text="Métrica")
            metrics_table.heading("value", text="Valor")
            metrics_table.column("metric", width=150)
            metrics_table.column("value", width=100)
            metrics_table.pack(fill=tk.BOTH, expand=True)
            
            # Adicionar métricas
            metrics_table.insert("", tk.END, values=["MSE", f"{metrics['mse']:.4f}"])
            metrics_table.insert("", tk.END, values=["MAE", f"{metrics['mae']:.4f}"])
            metrics_table.insert("", tk.END, values=["R²", f"{metrics['r2']:.4f}"])
            
            # Visualização - Valores reais vs. previstos
            fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
            
            # Plotar valores reais vs. previstos
            ax.scatter(metrics['y_test'], metrics['y_pred'], alpha=0.5)
            
            # Adicionar linha de referência
            min_val = min(metrics['y_test'].min(), metrics['y_pred'].min())
            max_val = max(metrics['y_test'].max(), metrics['y_pred'].max())
            ax.plot([min_val, max_val], [min_val, max_val], 'r--')
            
            ax.set_title("Valores Reais vs. Previstos")
            ax.set_xlabel("Valores Reais")
            ax.set_ylabel("Valores Previstos")
            
            plt.tight_layout()
            
            # Adicionar canvas ao frame
            canvas = FigureCanvasTkAgg(fig, master=self.model_viz_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        elif task_type == "clustering":
            # Métricas de clustering
            metrics_frame = ttk.Frame(self.metrics_frame)
            metrics_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Criar tabela de métricas
            metrics_table = ttk.Treeview(metrics_frame, columns=["metric", "value"], show="headings")
            metrics_table.heading("metric", text="Métrica")
            metrics_table.heading("value", text="Valor")
            metrics_table.column("metric", width=150)
            metrics_table.column("value", width=100)
            metrics_table.pack(fill=tk.BOTH, expand=True)
            
            # Adicionar métricas
            if model_name == "K-Means":
                metrics_table.insert("", tk.END, values=["Inércia", f"{metrics['inertia']:.4f}"])
            
            metrics_table.insert("", tk.END, values=["Número de Clusters", metrics['n_clusters']])
            
            # Distribuição de clusters
            cluster_counts = pd.Series(metrics['labels']).value_counts().sort_index()
            
            for cluster, count in cluster_counts.items():
                cluster_name = "Ruído" if cluster == -1 else f"Cluster {cluster}"
                percentage = (count / len(self.df)) * 100
                metrics_table.insert("", tk.END, values=[cluster_name, f"{count} ({percentage:.1f}%)"])
            
            # Visualização - Distribuição de clusters
            fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
            
            # Plotar distribuição de clusters
            cluster_df = pd.DataFrame({
                'Cluster': [f"Cluster {c}" if c != -1 else "Ruído" for c in cluster_counts.index],
                'Count': cluster_counts.values
            })
            
            sns.barplot(data=cluster_df, x='Cluster', y='Count', ax=ax)
            ax.set_title("Distribuição de Clusters")
            ax.set_xlabel("Cluster")
            ax.set_ylabel("Número de Pontos")
            
            plt.tight_layout()
            
            # Adicionar canvas ao frame
            canvas = FigureCanvasTkAgg(fig, master=self.model_viz_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Mostrar importância de características se disponível
        if model_name in self.model_manager.feature_importances:
            # Obter importância de características
            feature_importances = self.model_manager.feature_importances[model_name]
            
            # Criar visualização
            fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
            
            # Criar DataFrame com importância de características
            if task_type != "clustering":
                features = self.df.drop(columns=[target_column]).columns
            else:
                features = self.df.select_dtypes(include=['int64', 'float64']).columns
            
            importance_df = pd.DataFrame({
                'Feature': features,
                'Importance': feature_importances
            }).sort_values('Importance', ascending=False)
            
            # Plotar importância de características
            sns.barplot(data=importance_df, x='Importance', y='Feature', ax=ax)
            ax.set_title("Importância de Características")
            ax.set_xlabel("Importância")
            ax.set_ylabel("Característica")
            
            plt.tight_layout()
            
            # Adicionar canvas ao frame
            canvas = FigureCanvasTkAgg(fig, master=self.feature_importance_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Mostrar previsões
        if task_type in ["classification", "regression"]:
            # Criar interface para previsões
            predictions_frame = ttk.Frame(self.predictions_frame)
            predictions_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Criar tabela de previsões
            predictions_table = ttk.Treeview(predictions_frame, columns=["index", "real", "pred"], show="headings")
            predictions_table.heading("index", text="Índice")
            predictions_table.heading("real", text="Valor Real")
            predictions_table.heading("pred", text="Valor Previsto")
            predictions_table.column("index", width=80)
            predictions_table.column("real", width=150)
            predictions_table.column("pred", width=150)
            predictions_table.pack(fill=tk.BOTH, expand=True)
            
            # Adicionar barra de rolagem
            scrollbar = ttk.Scrollbar(predictions_table, orient=tk.VERTICAL, command=predictions_table.yview)
            predictions_table.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Adicionar previsões
            for i in range(min(20, len(metrics['y_test']))):
                real = metrics['y_test'][i]
                pred = metrics['y_pred'][i]
                predictions_table.insert("", tk.END, values=[i, real, pred])
    
    def save_model(self):
        """Salvar modelo treinado"""
        if not self.model_manager.current_model:
            messagebox.showwarning("Aviso", "Nenhum modelo treinado para salvar.")
            return
        
        # Abrir diálogo para salvar
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pkl",
            filetypes=[("Pickle Files", "*.pkl"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Salvar modelo
            self.model_manager.save_model(file_path)
            messagebox.showinfo("Sucesso", f"Modelo salvo com sucesso em:\n{file_path}")
            self.status_var.set(f"Modelo salvo: {os.path.basename(file_path)}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar modelo:\n{str(e)}")
            logger.error(f"Erro ao salvar modelo: {str(e)}")
    
    def load_model(self):
        """Carregar modelo salvo"""
        # Abrir diálogo para carregar
        file_path = filedialog.askopenfilename(
            defaultextension=".pkl",
            filetypes=[("Pickle Files", "*.pkl"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Carregar modelo
            model = self.model_manager.load_model(file_path)
            messagebox.showinfo("Sucesso", f"Modelo carregado com sucesso:\n{self.model_manager.current_model_name}")
            self.status_var.set(f"Modelo carregado: {os.path.basename(file_path)}")
            
            # Atualizar interface
            # TODO: Implementar atualização da interface com o modelo carregado
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar modelo:\n{str(e)}")
            logger.error(f"Erro ao carregar modelo: {str(e)}")
    
    def generate_insights(self):
        """Gerar insights automáticos a partir dos dados"""
        # Limpar área de texto
        self.insights_text.delete(1.0, tk.END)
        
        # Iniciar geração de insights
        self.status_var.set("Gerando insights...")
        
        # Função para gerar insights em uma thread separada
        def insights_thread():
            try:
                # Adicionar cabeçalho
                self.root.after(0, lambda: self.insights_text.insert(tk.END, "Insights Automáticos\n\n", "heading"))
                
                # Estatísticas básicas
                self.root.after(0, lambda: self.insights_text.insert(tk.END, "1. Estatísticas Básicas\n\n", "subheading"))
                
                # Número de linhas e colunas
                self.root.after(0, lambda: self.insights_text.insert(tk.END, f"• O conjunto de dados contém {len(self.df)} linhas e {len(self.df.columns)} colunas.\n", "normal"))
                
                # Tipos de dados
                dtypes = self.df.dtypes.value_counts()
                dtype_text = "• Tipos de dados: "
                for dtype, count in dtypes.items():
                    dtype_text += f"{count} colunas do tipo {dtype}, "
                dtype_text = dtype_text[:-2] + ".\n"
                self.root.after(0, lambda: self.insights_text.insert(tk.END, dtype_text, "normal"))
                
                # Valores ausentes
                missing_cols = self.df.columns[self.df.isnull().any()].tolist()
                if missing_cols:
                    missing_text = "• Valores ausentes encontrados em "
                    for col in missing_cols[:3]:
                        missing_pct = self.df[col].isnull().mean() * 100
                        missing_text += f"{col} ({missing_pct:.1f}%), "
                    
                    if len(missing_cols) > 3:
                        missing_text += f"e {len(missing_cols) - 3} outras colunas.\n"
                    else:
                        missing_text = missing_text[:-2] + ".\n"
                    
                    self.root.after(0, lambda: self.insights_text.insert(tk.END, missing_text, "warning"))
                else:
                    self.root.after(0, lambda: self.insights_text.insert(tk.END, "• Não foram encontrados valores ausentes no conjunto de dados.\n", "success"))
                
                # Detecção de outliers
                self.root.after(0, lambda: self.insights_text.insert(tk.END, "\n2. Detecção de Outliers\n\n", "subheading"))
                
                # Detectar outliers
                outliers = self.pattern_detector.detect_outliers(self.df, method='zscore', threshold=3)
                
                outlier_cols = [col for col in outliers if outliers[col]]
                if outlier_cols:
                    outlier_text = "• Outliers encontrados em "
                    for col in outlier_cols[:3]:
                        outlier_text += f"{col} ({len(outliers[col])} outliers), "
                    
                    if len(outlier_cols) > 3:
                        outlier_text += f"e {len(outlier_cols) - 3} outras colunas.\n"
                    else:
                        outlier_text = outlier_text[:-2] + ".\n"
                    
                    self.root.after(0, lambda: self.insights_text.insert(tk.END, outlier_text, "warning"))
                else:
                    self.root.after(0, lambda: self.insights_text.insert(tk.END, "• Não foram encontrados outliers significativos no conjunto de dados.\n", "success"))
                
                # Correlações
                self.root.after(0, lambda: self.insights_text.insert(tk.END, "\n3. Correlações\n\n", "subheading"))
                
                # Analisar correlações
                numeric_df = self.df.select_dtypes(include=['int64', 'float64'])
                if numeric_df.shape[1] >= 2:
                    correlations, strong_correlations = self.pattern_detector.analyze_correlations(self.df)
                    
                    if strong_correlations:
                        corr_text = "• Correlações fortes encontradas:\n"
                        for col1, col2, corr in strong_correlations[:5]:
                            corr_type = "positiva" if corr > 0 else "negativa"
                            corr_text += f"  - {col1} e {col2}: {corr:.3f} (correlação {corr_type})\n"
                        
                        if len(strong_correlations) > 5:
                            corr_text += f"  - E mais {len(strong_correlations) - 5} outras correlações fortes.\n"
                        
                        self.root.after(0, lambda: self.insights_text.insert(tk.END, corr_text, "highlight"))
                    else:
                        self.root.after(0, lambda: self.insights_text.insert(tk.END, "• Não foram encontradas correlações fortes entre as variáveis.\n", "normal"))
                else:
                    self.root.after(0, lambda: self.insights_text.insert(tk.END, "• Não há colunas numéricas suficientes para análise de correlação.\n", "normal"))
                
                # Padrões
                self.root.after(0, lambda: self.insights_text.insert(tk.END, "\n4. Padrões Identificados\n\n", "subheading"))
                
                # Encontrar padrões
                patterns = self.pattern_detector.find_patterns(self.df)
                
                if patterns:
                    for pattern in patterns[:10]:
                        self.root.after(0, lambda: self.insights_text.insert(tk.END, f"• {pattern}\n", "normal"))
                    
                    if len(patterns) > 10:
                        self.root.after(0, lambda: self.insights_text.insert(tk.END, f"• E mais {len(patterns) - 10} outros padrões identificados.\n", "normal"))
                else:
                    self.root.after(0, lambda: self.insights_text.insert(tk.END, "• Nenhum padrão significativo identificado.\n", "normal"))
                
                # Recomendações
                self.root.after(0, lambda: self.insights_text.insert(tk.END, "\n5. Recomendações\n\n", "subheading"))
                
                # Gerar recomendações com base nos insights
                recommendations = []
                
                # Recomendações para valores ausentes
                if missing_cols:
                    recommendations.append("Considere tratar os valores ausentes antes de aplicar modelos de machine learning.")
                
                # Recomendações para outliers
                if outlier_cols:
                    recommendations.append("Avalie o impacto dos outliers nos seus modelos e considere tratá-los se necessário.")
                
                # Recomendações para correlações
                if strong_correlations:
                    recommendations.append("Considere a multicolinearidade ao construir modelos preditivos, pois há variáveis fortemente correlacionadas.")
                
                # Recomendações gerais
                recommendations.append("Explore técnicas de redução de dimensionalidade como PCA se houver muitas variáveis numéricas.")
                
                if self.df.select_dtypes(include=['object', 'category']).shape[1] > 0:
                    recommendations.append("Codifique variáveis categóricas antes de aplicar algoritmos de machine learning.")
                
                for recommendation in recommendations:
                    self.root.after(0, lambda: self.insights_text.insert(tk.END, f"• {recommendation}\n", "highlight"))
                
                # Atualizar status
                self.root.after(0, lambda: self.status_var.set("Insights gerados com sucesso"))
            
            except Exception as e:
                # Mostrar erro
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao gerar insights:\n{str(e)}"))
                logger.error(f"Erro ao gerar insights: {str(e)}")
        
        # Iniciar thread
        threading.Thread(target=insights_thread, daemon=True).start()

class AIIntegration:
    """Classe principal para integração de IA no JSONMaster Pro"""
    def __init__(self, parent):
        self.parent = parent
        self.data = None
        self.columns = None
    
    def show_ai_dialog(self, data, columns):
        """Mostrar diálogo principal de IA"""
        self.data = data
        self.columns = columns
        
        dialog = AIDialog(self.parent, data, columns)
        self.parent.wait_window(dialog)

def integrate_ai_to_jsonmaster(jsonmaster_app):
    """Integrar funcionalidades de IA ao JSONMaster Pro"""
    # Criar instância da integração de IA
    ai_integration = AIIntegration(jsonmaster_app.root)
    
    # Adicionar menu de IA
    menubar = jsonmaster_app.root.config("menu")[-1]
    
    ai_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Inteligência Artificial", menu=ai_menu)
    
    ai_menu.add_command(label="Análise Preditiva e Detecção de Padrões", 
                       command=lambda: ai_integration.show_ai_dialog(jsonmaster_app.extracted_data, jsonmaster_app.selected_fields))
    
    # Adicionar botão de IA à interface principal
    ai_btn = ttk.Button(jsonmaster_app.extract_frame, text="Análise de IA", 
                       command=lambda: ai_integration.show_ai_dialog(jsonmaster_app.extracted_data, jsonmaster_app.selected_fields))
    ai_btn.pack(side=tk.LEFT, padx=(10, 0))
    
    return ai_integration