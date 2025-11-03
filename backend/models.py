import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score, roc_curve
from hmmlearn.hmm import GaussianHMM
import matplotlib.pyplot as plt
import os

# --- Geração de Dados Sintéticos ---

def generate_synthetic_data(n_employees=500, n_months=12, seed=42):
    """Gera um DataFrame sintético de dados de colaboradores e surveys."""
    np.random.seed(seed)
    
    employees_data = []
    
    for emp_id in range(n_employees):
        # Demographics
        idade = np.random.randint(22, 65)
        tempo_empresa = np.random.randint(3, 240)  # 3 meses a 20 anos
        departamento = np.random.choice(['Sales', 'Engineering', 'HR', 'Marketing', 'Finance'])
        nivel = np.random.choice(['Junior', 'Pleno', 'Senior'])
        faixa_salarial = np.random.choice(['Entry', 'Mid', 'Senior'])
        localizacao = np.random.choice(['Remoto', 'Híbrido', 'Presencial'])

        # Historical events
        promovido = np.random.choice([0, 1], p=[0.9, 0.1])
        aumento_salarial = np.random.uniform(0, 15)
        manager_change = np.random.choice([0, 1], p=[0.85, 0.15])
        treinamentos = np.random.randint(0, 5)
        avaliacao_performance = np.random.uniform(2.5, 5)

        # Turnover outcome (base probability)
        base_desligamento_prob = 0.15

        # Factors that increase desligamento risk
        if tempo_empresa < 6:
            base_desligamento_prob += 0.1
        if promovido == 0 and tempo_empresa > 24:
            base_desligamento_prob += 0.05
        if aumento_salarial < 3:
            base_desligamento_prob += 0.05
        if manager_change == 1:
            base_desligamento_prob += 0.08
        if avaliacao_performance < 3:
            base_desligamento_prob += 0.1
        if localizacao == 'Presencial' and np.random.random() < 0.3:
            base_desligamento_prob += 0.03

        # Clamp probability
        base_desligamento_prob = min(base_desligamento_prob, 0.8)

        # Generate monthly survey responses + desligamento outcome
        survey_history = []
        desligamento = 0

        # Simular que scores baixos aumentam a probabilidade de desligamento
        low_score_factor = 1.0 if base_desligamento_prob < 0.3 else 0.5
        
        for month in range(1, n_months + 1):
            # Survey scores: Likert scale 1-5
            engajamento = np.random.normal(3.5 * low_score_factor, 0.8)
            satisfaction = np.random.normal(3.5 * low_score_factor, 0.9)
            recognition = np.random.normal(3.2, 0.9)
            growth = np.random.normal(3.0 * low_score_factor, 1.0)
            manager_rel = np.random.normal(3.6, 0.8)
            work_life = np.random.normal(3.3, 1.0)

            # Clamp to 1-5
            engajamento = np.clip(engajamento, 1, 5)
            satisfaction = np.clip(satisfaction, 1, 5)
            recognition = np.clip(recognition, 1, 5)
            growth = np.clip(growth, 1, 5)
            manager_rel = np.clip(manager_rel, 1, 5)
            work_life = np.clip(work_life, 1, 5)

            survey_history.append({
                'month': month,
                'engajamento': engajamento,
                'satisfaction': satisfaction,
                'recognition': recognition,
                'growth': growth,
                'manager_rel': manager_rel,
                'work_life': work_life
            })

            # Decide desligamento at end of period (months 10-12)
            if month >= 10 and np.random.random() < base_desligamento_prob:
                desligamento = 1
                break

        # Average survey scores over 12 months
        survey_df = pd.DataFrame(survey_history)
        avg_engajamento = survey_df['engajamento'].mean()
        satisfacao_media = survey_df['satisfaction'].mean()
        reconhecimento_medio = survey_df['recognition'].mean()
        crescimento_medio = survey_df['growth'].mean()
        avg_manager_rel = survey_df['manager_rel'].mean()
        equilibrio_vida_trabalho_medio = survey_df['work_life'].mean()

        employees_data.append({
            'employee_id': emp_id,
            'idade': idade,
            'tempo_empresa': tempo_empresa,
            'departamento': departamento,
            'nivel': nivel,
            'faixa_salarial': faixa_salarial,
            'localizacao': localizacao,
            'promovido': promovido,
            'aumento_salarial': aumento_salarial,
            'manager_change': manager_change,
            'treinamentos': treinamentos,
            'avaliacao_performance': avaliacao_performance,
            'avg_engajamento': avg_engajamento,
            'satisfacao_media': satisfacao_media,
            'reconhecimento_medio': reconhecimento_medio,
            'crescimento_medio': crescimento_medio,
            'avg_manager_rel': avg_manager_rel,
            'equilibrio_vida_trabalho_medio': equilibrio_vida_trabalho_medio,
            'desligamento': desligamento,
            'survey_history': survey_history
        })

    df = pd.DataFrame(employees_data)
    
    # Renomear colunas para corresponder ao schema da API
    df.rename(columns={
        'avg_engajamento': 'avg_engidadement',
        'manager_change': 'manidader_change',
        'avg_manager_rel': 'avg_manidader_rel'
    }, inplace=True)
    
    return df

# --- HMM Model ---

class SurveyStateDetector:
    """Detecta estados latentes a partir de histórico de surveys"""
    def __init__(self, n_states=3, n_iter=100):
        self.model = GaussianHMM(
            n_components=n_states,
            covariance_type="full",
            n_iter=n_iter,
            random_state=42
        )
        self.n_states = n_states
        self.feature_cols = [
            'engajamento', 'satisfaction', 'recognition', 
            'growth', 'manager_rel', 'work_life'
        ]

    def prepare_sequences(self, df_employees):
        """
        Converte dataframe com histórico de surveys em sequências
        Input: df com colunas survey_history (lista de dicts)
        Output: array de sequências (n_employees, n_months, n_features)
        """
        sequences = []
        lengths = []  # Comprimento de cada sequência

        for _, row in df_employees.iterrows():
            survey_hist = row['survey_history']
            
            # Corrigir nomes das chaves no histórico de survey
            sequence = np.array([
                [
                    s.get('engajamento', s.get('engidadement')), # Tenta 'engajamento', se não, 'engidadement'
                    s['satisfaction'],
                    s['recognition'],
                    s['growth'],
                    s.get('manager_rel', s.get('manidader_rel')), # Tenta 'manager_rel', se não, 'manidader_rel'
                    s['work_life']
                ]
                for s in survey_hist
            ])
            sequences.append(sequence)
            lengths.append(len(sequence))

        # Concatenar todas as sequências para treinar HMM
        X = np.concatenate(sequences)

        return X, lengths, sequences

    def fit(self, df_employees):
        """Treina o HMM com histórico de surveys"""
        X, lengths, _ = self.prepare_sequences(df_employees)
        self.model.fit(X, lengths)
        self.lengths = lengths
        return self

    def predict_states(self, df_employees):
        """Prediz sequência de estados para cada colaborador"""
        X, lengths, sequences = self.prepare_sequences(df_employees)
        all_states = self.model.predict(X, lengths)

        # Split de volta por colaborador
        states_by_employee = []
        start = 0
        for length in lengths:
            states_by_employee.append(all_states[start:start+length])
            start += length

        return states_by_employee

    def get_current_state(self, df_employees, state_sequences):
        """Extrai o estado atual (último) para cada colaborador"""
        current_states = [states[-1] for states in state_sequences]
        
        # Adicionar a coluna ao DataFrame original (copiado)
        df_employees['current_hmm_state'] = current_states
        return df_employees

    def get_state_probabilities(self, df_employees):
        """Retorna probabilidade de cada estado para o período recente"""
        X, lengths, sequences = self.prepare_sequences(df_employees)
        
        probs_by_employee = []
        start = 0

        for i, length in enumerate(lengths):
            # Último frame (mês)
            recent_seq = X[start + length - 1 : start + length]
            
            # Calcular log-probabilidades de cada estado ser o estado inicial (start_prob)
            # e a probabilidade de transição para o estado final (transmat)
            # Para simplificar no MVP, vamos usar a probabilidade de emissão (emission probability)
            # que é a probabilidade de observar o dado (recent_seq) dado cada estado.
            
            # Calcular log-probabilidade de emissão
            log_emission_probs = self.model._compute_log_likelihood(recent_seq)
            
            # Converter para probabilidade (exp) e normalizar
            emission_probs = np.exp(log_emission_probs[0])
            normalized_probs = emission_probs / np.sum(emission_probs)
            
            probs_by_employee.append(normalized_probs)
            start += length

        return probs_by_employee

# --- Random Forest Model ---

class TurnoverPredictor:
    def __init__(self, random_state=42):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            random_state=random_state
        )
        self.label_encoders = {}
        self.feature_names = None

    def prepare_features(self, df, state_probs=None, fit=False):
        """
        Prepara features para Random Forest
        Inclui: demografics + contexto + estados HMM
        """
        df_prep = df.copy()

        # Renomear colunas para o padrão correto, caso o input venha da API
        df_prep.rename(columns={
            'avg_engidadement': 'avg_engajamento',
            'manidader_change': 'manager_change',
            'avg_manidader_rel': 'avg_manager_rel'
        }, inplace=True)

        # Categorical features -> encoding
        categorical_cols = ['departamento', 'nivel', 'faixa_salarial', 'localizacao']

        for col in categorical_cols:
            if fit:
                le = LabelEncoder()
                df_prep[col + '_encoded'] = le.fit_transform(df_prep[col])
                self.label_encoders[col] = le
            else:
                # Tratar categorias não vistas no treinamento
                le = self.label_encoders[col]
                df_prep[col + '_encoded'] = df_prep[col].apply(
                    lambda x: le.transform([x])[0] if x in le.classes_ else -1
                )
        
        # Features finais
        feature_cols = [
            'idade', 'tempo_empresa', 'promovido', 'aumento_salarial', 'manager_change',
            'treinamentos', 'avaliacao_performance',
            'avg_engajamento', 'satisfacao_media', 'reconhecimento_medio',
            'crescimento_medio', 'avg_manager_rel', 'equilibrio_vida_trabalho_medio',
            'current_hmm_state',  # Estado latente do HMM
            'departamento_encoded', 'nivel_encoded', 'faixa_salarial_encoded', 'localizacao_encoded'
        ]

        # Opcional: adicionar probabilidades de estados HMM
        if state_probs is not None and len(state_probs) > 0:
            n_states = len(state_probs[0])
            for state_idx in range(n_states):
                df_prep[f'state_prob_{state_idx}'] = [probs[state_idx] for probs in state_probs]
                feature_cols.append(f'state_prob_{state_idx}')

        # Garantir que todas as colunas existam (para predição)
        for col in feature_cols:
            if col not in df_prep.columns:
                df_prep[col] = 0 # Adicionar coluna com valor default 0

        X = df_prep[feature_cols].fillna(0)
        self.feature_names = feature_cols

        return X

    def train(self, df, state_probs=None, test_size=0.2):
        """Treina o modelo com validação cruzada"""
        X = self.prepare_features(df, state_probs, fit=True)
        y = df['desligamento']

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        # Validação cruzada
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5, scoring='roc_auc')
        print(f"CV AUC: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

        # Treinar
        self.model.fit(X_train, y_train)

        # Avaliar
        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]

        auc = roc_auc_score(y_test, y_proba)
        print(f"Test AUC: {auc:.3f}")
        print(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")

        # Plot ROC Curve e salvar
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC (AUC={auc:.3f})')
        plt.plot([0, 1], [0, 1], 'k--', label='Random')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.legend()
        plt.title('ROC Curve - Turnover Prediction')
        
        # Salvar o gráfico em um local acessível
        plot_path = os.path.join(os.getcwd(), 'roc_curve.png')
        plt.savefig(plot_path)
        plt.close()
        print(f"Gráfico ROC salvo em: {plot_path}")

        return {'X_test': X_test, 'y_test': y_test, 'y_proba': y_proba, 'auc': auc}

    def predict_risk(self, df, state_probs=None):
        """Prediz risco de desligamento para novos dados"""
        X = self.prepare_features(df, state_probs, fit=False)
        probabilities = self.model.predict_proba(X)[:, 1]

        df_pred = df.copy()
        df_pred['desligamento_risk'] = probabilities
        df_pred['risk_category'] = pd.cut(
            probabilities,
            bins=[0, 0.3, 0.6, 1.0],
            labels=['Baixo', 'Médio', 'Alto'],
            right=False # Incluir o limite inferior, excluir o superior
        )

        return df_pred

    def get_feature_importance(self, top_n=10):
        """Retorna features mais importantes"""
        importances = self.model.feature_importances_
        feature_importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)

        return feature_importance_df.head(top_n)
