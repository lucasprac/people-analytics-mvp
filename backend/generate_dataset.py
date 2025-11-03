import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

np.random.seed(42)

def generate_synthetic_dataset(n_employees=500, n_months=12):
    """
    Gera dataset sintético realista para o MVP de People Analytics
    
    Args:
        n_employees: Número de colaboradores
        n_months: Número de meses de histórico
    
    Returns:
        DataFrame com dados dos colaboradores
    """
    print(f"Gerando dataset sintético com {n_employees} colaboradores e {n_months} meses de histórico...")
    
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
            base_desligamento_prob += 0.1  # Novo pode sair mais
        if promovido == 0 and tempo_empresa > 24:
            base_desligamento_prob += 0.05  # Sem promoção há tempo
        if aumento_salarial < 3:
            base_desligamento_prob += 0.05  # Sem aumento salarial
        if manager_change == 1:
            base_desligamento_prob += 0.08  # Mudança de gestor afeta
        if avaliacao_performance < 3:
            base_desligamento_prob += 0.1  # Desempenho baixo
        if localizacao == 'Presencial' and np.random.random() < 0.3:
            base_desligamento_prob += 0.03  # Presencial tem taxa um pouco maior
        
        # Clamp probability
        base_desligamento_prob = min(base_desligamento_prob, 0.8)
        
        # Generate monthly survey responses + desligamento outcome
        survey_history = []
        desligamento = 0
        
        for month in range(1, n_months + 1):
            # Survey scores: Likert scale 1-5
            engajamento = np.random.normal(3.5 if base_desligamento_prob < 0.3 else 2.5, 0.8)
            satisfacao = np.random.normal(3.5 if base_desligamento_prob < 0.3 else 2.3, 0.9)
            reconhecimento = np.random.normal(3.2, 0.9)
            crescimento = np.random.normal(3.0 if base_desligamento_prob < 0.5 else 2.2, 1.0)
            relacionamento_gestor = np.random.normal(3.6, 0.8)
            work_life_balance = np.random.normal(3.3, 1.0)
            
            # Clamp to 1-5
            engajamento = np.clip(engajamento, 1, 5)
            satisfacao = np.clip(satisfacao, 1, 5)
            reconhecimento = np.clip(reconhecimento, 1, 5)
            crescimento = np.clip(crescimento, 1, 5)
            relacionamento_gestor = np.clip(relacionamento_gestor, 1, 5)
            work_life_balance = np.clip(work_life_balance, 1, 5)
            
            survey_history.append({
                'month': month,
                'engajamento': engajamento,
                'satisfacao': satisfacao,
                'reconhecimento': reconhecimento,
                'crescimento': crescimento,
                'relacionamento_gestor': relacionamento_gestor,
                'work_life_balance': work_life_balance
            })
            
            # Decide desligamento at end of period (months 10-12)
            if month >= 10 and np.random.random() < base_desligamento_prob:
                desligamento = 1
                break
        
        # Average survey scores over 12 months
        survey_df = pd.DataFrame(survey_history)
        avg_engajamento = survey_df['engajamento'].mean()
        satisfacao_media = survey_df['satisfacao'].mean()
        reconhecimento_medio = survey_df['reconhecimento'].mean()
        crescimento_medio = survey_df['crescimento'].mean()
        avg_relacionamento_gestor = survey_df['relacionamento_gestor'].mean()
        equilibrio_vida_trabalho_medio = survey_df['work_life_balance'].mean()
        
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
            'avg_relacionamento_gestor': avg_relacionamento_gestor,
            'equilibrio_vida_trabalho_medio': equilibrio_vida_trabalho_medio,
            'desligamento': desligamento,
            'survey_history': survey_history
        })
    
    df = pd.DataFrame(employees_data)
    print(f"Dataset shape: {df.shape}")
    print(f"Turnover rate: {df['desligamento'].mean():.1%}")
    
    return df

def save_dataset(df, filepath='data/employees_data.csv'):
    """
    Salva o dataset em CSV
    """
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Salvar sem a coluna survey_history (muito complexa para CSV)
    df_to_save = df.drop('survey_history', axis=1)
    df_to_save.to_csv(filepath, index=False)
    print(f"Dataset salvo em: {filepath}")
    
    # Salvar também versão com histórico em formato pickle
    import pickle
    pickle_path = filepath.replace('.csv', '_with_history.pkl')
    with open(pickle_path, 'wb') as f:
        pickle.dump(df, f)
    print(f"Dataset completo (com histórico) salvo em: {pickle_path}")

if __name__ == "__main__":
    # Gerar dataset
    df = generate_synthetic_dataset(n_employees=500, n_months=12)
    
    # Salvar
    save_dataset(df)
    
    # Mostrar algumas estatísticas
    print("\n=== ESTATÍSTICAS DO DATASET ===")
    print(f"Total de colaboradores: {len(df)}")
    print(f"Taxa de turnover: {df['desligamento'].mean():.1%}")
    print(f"\nDistribuição por departamento:")
    print(df['departamento'].value_counts())
    print(f"\nDistribuição por nível:")
    print(df['nivel'].value_counts())
    print(f"\nMédias dos scores de survey:")
    survey_cols = ['avg_engajamento', 'satisfacao_media', 'reconhecimento_medio', 
                  'crescimento_medio', 'avg_relacionamento_gestor', 'equilibrio_vida_trabalho_medio']
    for col in survey_cols:
        print(f"{col}: {df[col].mean():.2f}")