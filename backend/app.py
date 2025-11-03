from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np
from typing import List, Optional
import os
import io
from contextlib import asynccontextmanager

# Importar classes de modelos (serão criadas em models.py)
from models import SurveyStateDetector, TurnoverPredictor, generate_synthetic_data

# --- Configuração ---
MODEL_DIR = "models"
DATA_FILE = "employees_data.csv"

# Variáveis globais para os modelos
hmm_model: Optional[SurveyStateDetector] = None
rf_model: Optional[TurnoverPredictor] = None

# --- Lifespan (para carregar modelos na inicialização) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global hmm_model, rf_model
    
    # 1. Tentar carregar modelos existentes
    try:
        hmm_model = joblib.load(os.path.join(MODEL_DIR, 'hmm_model.pkl'))
        rf_model = joblib.load(os.path.join(MODEL_DIR, 'rf_model.pkl'))
        print("Modelos carregados com sucesso.")
    except FileNotFoundError:
        print("Modelos não encontrados. Treine-os via API.")
    except Exception as e:
        print(f"Erro ao carregar modelos: {e}")

    yield
    # 2. Limpeza ao desligar (se necessário)

# --- Definições de Schemas (Pydantic) ---

class EmployeeData(BaseModel):
    employee_id: int
    idade: int
    tempo_empresa: int
    departamento: str
    nivel: str
    faixa_salarial: str
    localizacao: str
    promovido: int
    aumento_salarial: float
    manidader_change: int = Field(alias='manager_change') # Corrigir nome da variável
    treinamentos: int
    avaliacao_performance: float
    avg_engajamento: float = Field(alias='avg_engidadement') # Corrigir nome da variável
    satisfacao_media: float
    reconhecimento_medio: float
    crescimento_medio: float
    avg_manager_rel: float = Field(alias='avg_manidader_rel') # Corrigir nome da variável
    equilibrio_vida_trabalho_medio: float
    survey_history: Optional[List[dict]] = None # Adicionar histórico para HMM

    class Config:
        populate_by_name = True # Permite usar o alias

class TurnoverPredictionResponse(BaseModel):
    employee_id: int
    desligamento_risk: float
    categoria_de_risco: str
    confidence: float

# --- Inicialização do FastAPI ---
app = FastAPI(
    title="People Analytics - Turnover Prediction MVP",
    version="0.1.0",
    lifespan=lifespan
)

# --- Endpoints ---

@app.get("/health")
def health():
    return {"status": "ok", "service": "People Analytics MVP"}

@app.post("/api/train/models")
async def train_models(file: Optional[UploadFile] = File(None)):
    """Treina HMM e Random Forest com dados de histórico. Se nenhum arquivo for enviado, usa dados sintéticos."""
    global hmm_model, rf_model

    try:
        if file:
            # Carregar dados do arquivo CSV
            contents = await file.read()
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
            print(f"Dados carregados do arquivo: {df.shape}")
        else:
            # Gerar dados sintéticos
            df = generate_synthetic_data()
            print(f"Dados sintéticos gerados: {df.shape}")
            # Salvar dados sintéticos para referência
            df.to_csv(os.path.join("data", DATA_FILE), index=False)

        # Treinar HMM
        hmm_model = SurveyStateDetector(n_states=3)
        hmm_model.fit(df)
        state_sequences = hmm_model.predict_states(df)
        df = hmm_model.get_current_state(df, state_sequences)
        state_probs = hmm_model.get_state_probabilities(df)

        # Treinar Random Forest
        rf_model = TurnoverPredictor()
        results = rf_model.train(df, state_probs=state_probs)

        # Salvar modelos
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(hmm_model, os.path.join(MODEL_DIR, 'hmm_model.pkl'))
        joblib.dump(rf_model, os.path.join(MODEL_DIR, 'rf_model.pkl'))

        return {
            "status": "Models trained successfully",
            "test_auc": float(results['auc']),
            "n_employees": len(df),
            "turnover_rate": f"{df['desligamento'].mean():.1%}"
        }
    except Exception as e:
        # Logar o erro completo para debug
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Erro no treinamento: {e}")

@app.post("/api/predict/desligamento", response_model=List[TurnoverPredictionResponse])
def predict_desligamento(employees: List[EmployeeData]):
    """Prediz risco de desligamento para lista de colaboradores"""
    global hmm_model, rf_model
    
    if rf_model is None or hmm_model is None:
        raise HTTPException(status_code=400, detail="Modelos não treinados. Chame /api/train/models primeiro.")

    try:
        # 1. Converter lista de Pydantic Models para DataFrame
        data = [emp.model_dump(by_alias=True) for emp in employees]
        df = pd.DataFrame(data)
        
        # 2. Inferir estados HMM
        # O HMM precisa do histórico de survey. Se não for fornecido, não podemos inferir o estado.
        # Para o MVP, vamos simular a inferência de estado para dados sem histórico completo.
        # Em um cenário real, a predição seria feita apenas para quem tem histórico de survey.
        
        # Filtrar colaboradores com histórico para HMM
        df_with_history = df[df['survey_history'].apply(lambda x: x is not None and len(x) > 0)]
        df_without_history = df[df['survey_history'].apply(lambda x: x is None or len(x) == 0)]

        # Inferir estados para quem tem histórico
        if not df_with_history.empty:
            state_sequences = hmm_model.predict_states(df_with_history)
            df_with_history = hmm_model.get_current_state(df_with_history, state_sequences)
            state_probs = hmm_model.get_state_probabilities(df_with_history)
        else:
            state_probs = []

        # Para quem não tem histórico, atribuir estado 0 (Neutro/Baixo Risco)
        if not df_without_history.empty:
            df_without_history['current_hmm_state'] = 0
            # Criar probabilidades uniformes para quem não tem histórico
            n_states = hmm_model.n_states if hmm_model else 3
            uniform_probs = [1/n_states] * n_states
            state_probs_without = [uniform_probs] * len(df_without_history)
            
            # Combinar dataframes e probabilidades
            df = pd.concat([df_with_history, df_without_history], ignore_index=True)
            state_probs.extend(state_probs_without)
        else:
            df = df_with_history
        
        # 3. Predições com Random Forest
        df_pred = rf_model.predict_risk(df, state_probs=state_probs)

        # 4. Formatar resposta
        predictions = [
            TurnoverPredictionResponse(
                employee_id=int(row['employee_id']),
                desligamento_risk=float(row['desligamento_risk']),
                categoria_de_risco=str(row['risk_category']),
                # Confiança: quão longe a probabilidade está de 0.5
                confidence=float(abs(row['desligamento_risk'] - 0.5) * 2)
            )
            for _, row in df_pred.iterrows()
        ]

        return predictions
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Erro na predição: {e}")

@app.get("/api/analytics/feature-importance")
def get_feature_importance():
    """Retorna features mais importantes para desligamento"""
    if rf_model is None:
        raise HTTPException(status_code=400, detail="Modelo não treinado.")

    try:
        importance_df = rf_model.get_feature_importance(top_n=15)
        return importance_df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter feature importance: {e}")

@app.get("/api/analytics/dashboard")
def get_dashboard_metrics():
    """Retorna métricas resumidas para o dashboard"""
    if rf_model is None:
        return {
            "model_status": "not_trained",
            "total_employees": 0,
            "average_desligamento_risk": 0.0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0
        }
    
    # Em um cenário real, isso viria de um banco de dados ou cache
    # Para o MVP, vamos ler o CSV sintético e rodar a predição
    try:
        df = pd.read_csv(os.path.join("data", DATA_FILE))
        
        # Treinar HMM e RF (temporariamente para obter estados)
        # O ideal seria ter os estados persistidos
        hmm_temp = SurveyStateDetector(n_states=3)
        hmm_temp.fit(df)
        state_sequences = hmm_temp.predict_states(df)
        df = hmm_temp.get_current_state(df, state_sequences)
        state_probs = hmm_temp.get_state_probabilities(df)
        
        df_pred = rf_model.predict_risk(df, state_probs=state_probs)
        
        total_employees = len(df_pred)
        average_risk = df_pred['desligamento_risk'].mean()
        high_risk_count = len(df_pred[df_pred['risk_category'] == 'Alto'])
        medium_risk_count = len(df_pred[df_pred['risk_category'] == 'Médio'])
        low_risk_count = len(df_pred[df_pred['risk_category'] == 'Baixo'])
        
        return {
            "model_status": "trained",
            "total_employees": total_employees,
            "average_desligamento_risk": float(average_risk),
            "high_risk_count": int(high_risk_count),
            "medium_risk_count": int(medium_risk_count),
            "low_risk_count": int(low_risk_count)
        }
    except FileNotFoundError:
        return {
            "model_status": "trained_no_data",
            "total_employees": 0,
            "average_desligamento_risk": 0.0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar métricas do dashboard: {e}")
