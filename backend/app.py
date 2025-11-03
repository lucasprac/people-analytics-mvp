from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import joblib
import pandas as pd
import numpy as np
import os
import pickle
from datetime import datetime

# Importar modelos locais
from models import SurveyStateDetector, TurnoverPredictor, generate_synthetic_data
from generate_dataset import generate_synthetic_dataset

app = FastAPI(
    title="People Analytics - Turnover Prediction MVP",
    description="Plataforma MVP de People Analytics com predição de turnover usando HMM e Random Forest",
    version="0.1.0"
)

# CORS - configurar para produção
allowed_origins = [
    "http://localhost:4200",
    "http://localhost:3000", 
    "https://people-analytics-frontend.vercel.app",
    "https://*.vercel.app"
]

if os.getenv('ENVIRONMENT') == 'production':
    cors_origins = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else allowed_origins
else:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos globais
hmm_model: Optional[SurveyStateDetector] = None
rf_model: Optional[TurnoverPredictor] = None
training_status = {"status": "not_trained", "last_trained": None, "metrics": {}}

# --- Pydantic Models ---

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
    manidader_change: int  # Nome corrigido para corresponder ao schema da especificação
    treinamentos: int
    avaliacao_performance: float
    avg_engidadement: float  # Nome corrigido para corresponder ao schema da especificação
    satisfacao_media: float
    reconhecimento_medio: float
    crescimento_medio: float
    avg_manidader_rel: float  # Nome corrigido para corresponder ao schema da especificação
    equilibrio_vida_trabalho_medio: float

class TurnoverPredictionResponse(BaseModel):
    employee_id: int
    desligamento_risk: float
    risk_category: str
    confidence: float

class TrainModelsRequest(BaseModel):
    filepath: Optional[str] = None
    n_employees: Optional[int] = 500
    n_months: Optional[int] = 12
    use_synthetic: Optional[bool] = True

class DashboardMetrics(BaseModel):
    model_status: str
    total_employees: int
    avg_desligamento_risk: float
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    last_trained: Optional[str]
    model_performance: Optional[dict]

# --- Health Check ---

@app.get("/health")
def health():
    return {"status": "ok", "service": "People Analytics MVP", "environment": os.getenv('ENVIRONMENT', 'development')}

# --- Training Endpoints ---

@app.post("/api/train/models")
def train_models(request: TrainModelsRequest):
    """Treina HMM e Random Forest com dados de histórico"""
    global hmm_model, rf_model, training_status

    try:
        print(f"Iniciando treinamento dos modelos...")
        training_status["status"] = "training"
        
        # Carregar ou gerar dados
        if request.use_synthetic:
            print(f"Gerando dados sintéticos: {request.n_employees} colaboradores, {request.n_months} meses")
            df = generate_synthetic_dataset(n_employees=request.n_employees, n_months=request.n_months)
        else:
            if not request.filepath or not os.path.exists(request.filepath):
                raise HTTPException(status_code=400, detail="Arquivo não encontrado")
            
            # Tentar carregar pickle primeiro (com histórico), depois CSV
            if request.filepath.endswith('.pkl'):
                with open(request.filepath, 'rb') as f:
                    df = pickle.load(f)
            else:
                df = pd.read_csv(request.filepath)
                # Para CSV, gerar histórico fake baseado nas médias
                df = add_fake_survey_history(df)

        print(f"Dataset carregado: {len(df)} colaboradores")
        print(f"Taxa de turnover: {df['desligamento'].mean():.1%}")

        # Treinar HMM
        print("Treinando modelo HMM...")
        hmm_model = SurveyStateDetector(n_states=3)
        hmm_model.fit(df)
        state_sequences = hmm_model.predict_states(df)
        df = hmm_model.get_current_state(df, state_sequences)
        state_probs = hmm_model.get_state_probabilities(df)
        print(f"HMM treinado com {hmm_model.n_states} estados")

        # Treinar Random Forest
        print("Treinando modelo Random Forest...")
        rf_model = TurnoverPredictor()
        results = rf_model.train(df, state_probs=state_probs)
        print(f"Random Forest treinado. AUC: {results['auc']:.3f}")

        # Salvar modelos
        os.makedirs('models', exist_ok=True)
        joblib.dump(hmm_model, 'models/hmm_model.pkl')
        joblib.dump(rf_model, 'models/rf_model.pkl')
        print("Modelos salvos em models/")

        # Atualizar status
        training_status = {
            "status": "trained",
            "last_trained": datetime.now().isoformat(),
            "metrics": {
                "test_auc": float(results['auc']),
                "n_employees": len(df),
                "turnover_rate": float(df['desligamento'].mean()),
                "hmm_states": hmm_model.n_states
            }
        }

        return {
            "status": "Models trained successfully",
            "test_auc": float(results['auc']),
            "n_employees": len(df),
            "turnover_rate": float(df['desligamento'].mean()),
            "training_time": training_status["last_trained"]
        }
    except Exception as e:
        training_status["status"] = "error"
        print(f"Erro durante treinamento: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro durante treinamento: {str(e)}")

@app.get("/api/train/status")
def get_training_status():
    """Retorna status do treinamento dos modelos"""
    return training_status

# --- Prediction Endpoints ---

@app.post("/api/predict/desligamento", response_model=List[TurnoverPredictionResponse])
def predict_desligamento(employees: List[EmployeeData]):
    """Prediz risco de desligamento para lista de colaboradores"""
    if rf_model is None or hmm_model is None:
        raise HTTPException(status_code=400, detail="Models not trained. Call /api/train/models first")

    try:
        # Converter para DataFrame
        df = pd.DataFrame([emp.dict() for emp in employees])
        print(f"Recebidos {len(df)} colaboradores para predição")

        # Para novas predições, simular um estado HMM baseado nos scores médios
        # Em produção, isso viria de histórico real
        df['current_hmm_state'] = simulate_hmm_states(df)
        
        # Gerar probabilidades de estado fake
        state_probs = simulate_state_probabilities(df, n_states=3)

        # Predições
        df_pred = rf_model.predict_risk(df, state_probs=state_probs)

        # Formatar resposta
        predictions = []
        for _, row in df_pred.iterrows():
            predictions.append(
                TurnoverPredictionResponse(
                    employee_id=int(row['employee_id']),
                    desligamento_risk=float(row['desligamento_risk']),
                    risk_category=str(row['risk_category']),
                    confidence=float(max(row['desligamento_risk'], 1 - row['desligamento_risk']))
                )
            )

        print(f"Predições geradas para {len(predictions)} colaboradores")
        return predictions
    except Exception as e:
        print(f"Erro durante predição: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro durante predição: {str(e)}")

@app.post("/api/predict/single")
def predict_single_employee(employee: EmployeeData):
    """Prediz risco de desligamento para um único colaborador"""
    result = predict_desligamento([employee])
    return result[0] if result else None

# --- Analytics Endpoints ---

@app.get("/api/analytics/feature-importance")
def get_feature_importance(top_n: int = 15):
    """Retorna features mais importantes para desligamento"""
    if rf_model is None:
        raise HTTPException(status_code=400, detail="Model not trained")
    
    try:
        importance_df = rf_model.get_feature_importance(top_n=top_n)
        return importance_df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao obter feature importance: {str(e)}")

@app.get("/api/analytics/dashboard", response_model=DashboardMetrics)
def get_dashboard_metrics():
    """Retorna métricas resumidas para o dashboard"""
    try:
        # Simular métricas para demo (em produção, viria do banco de dados)
        metrics = DashboardMetrics(
            model_status=training_status["status"],
            total_employees=training_status.get("metrics", {}).get("n_employees", 0),
            avg_desligamento_risk=0.35,  # Média simulada
            high_risk_count=75,
            medium_risk_count=150,
            low_risk_count=275,
            last_trained=training_status.get("last_trained"),
            model_performance=training_status.get("metrics")
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao obter métricas: {str(e)}")

# --- Data Generation Endpoints ---

@app.post("/api/data/generate")
def generate_sample_dataset(n_employees: int = 500, n_months: int = 12):
    """Gera um dataset sintético de exemplo"""
    try:
        df = generate_synthetic_dataset(n_employees=n_employees, n_months=n_months)
        
        # Salvar
        os.makedirs('data', exist_ok=True)
        filepath = f'data/employees_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df_to_save = df.drop('survey_history', axis=1)
        df_to_save.to_csv(filepath, index=False)
        
        return {
            "status": "Dataset generated successfully",
            "filepath": filepath,
            "n_employees": len(df),
            "turnover_rate": float(df['desligamento'].mean()),
            "columns": list(df_to_save.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao gerar dataset: {str(e)}")

# --- File Endpoints ---

@app.get("/api/files/roc-curve")
def get_roc_curve():
    """Retorna o gráfico da curva ROC"""
    roc_path = "roc_curve.png"
    if os.path.exists(roc_path):
        return FileResponse(roc_path, media_type="image/png", filename="roc_curve.png")
    else:
        raise HTTPException(status_code=404, detail="ROC curve not found. Train models first.")

@app.post("/api/files/upload")
def upload_dataset(file: UploadFile = File(...)):
    """Upload de arquivo CSV com dados de colaboradores"""
    try:
        # Salvar arquivo
        os.makedirs('data', exist_ok=True)
        filepath = f"data/{file.filename}"
        
        with open(filepath, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # Verificar conteúdo
        df = pd.read_csv(filepath)
        
        return {
            "status": "File uploaded successfully",
            "filepath": filepath,
            "filename": file.filename,
            "n_rows": len(df),
            "columns": list(df.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro no upload: {str(e)}")

# --- Helper Functions ---

def simulate_hmm_states(df):
    """Simula estados HMM baseado em scores médios (para novas predições)"""
    states = []
    for _, row in df.iterrows():
        # Lógica simples: baseado na média dos scores
        avg_score = np.mean([
            row['avg_engidadement'],
            row['satisfacao_media'],
            row['reconhecimento_medio'],
            row['crescimento_medio'],
            row['avg_manidader_rel'],
            row['equilibrio_vida_trabalho_medio']
        ])
        
        if avg_score >= 4.0:
            state = 0  # Estado "Engajado"
        elif avg_score >= 3.0:
            state = 1  # Estado "Neutro"
        else:
            state = 2  # Estado "Risco de Saída"
        
        states.append(state)
    
    return states

def simulate_state_probabilities(df, n_states=3):
    """Simula probabilidades de estado para novas predições"""
    probs = []
    for _, row in df.iterrows():
        # Lógica simples baseada nos scores
        avg_score = np.mean([
            row['avg_engidadement'],
            row['satisfacao_media'],
            row['reconhecimento_medio'],
            row['crescimento_medio'],
            row['avg_manidader_rel'],
            row['equilibrio_vida_trabalho_medio']
        ])
        
        # Distribuir probabilidade baseada no score médio
        if avg_score >= 4.0:
            prob = [0.7, 0.25, 0.05]  # Mais provável estar engajado
        elif avg_score >= 3.0:
            prob = [0.2, 0.6, 0.2]    # Mais provável estar neutro
        else:
            prob = [0.05, 0.25, 0.7]  # Mais provável estar em risco
        
        probs.append(prob)
    
    return probs

def add_fake_survey_history(df):
    """Adiciona histórico fake de survey baseado nas médias (para CSVs sem histórico)"""
    for idx, row in df.iterrows():
        # Gerar 12 meses de histórico baseado nas médias
        survey_history = []
        for month in range(1, 13):
            survey_history.append({
                'month': month,
                'engajamento': row['avg_engidadement'] + np.random.normal(0, 0.5),
                'satisfaction': row['satisfacao_media'] + np.random.normal(0, 0.5),
                'recognition': row['reconhecimento_medio'] + np.random.normal(0, 0.5),
                'growth': row['crescimento_medio'] + np.random.normal(0, 0.5),
                'manager_rel': row['avg_manidader_rel'] + np.random.normal(0, 0.5),
                'work_life': row['equilibrio_vida_trabalho_medio'] + np.random.normal(0, 0.5)
            })
        
        df.at[idx, 'survey_history'] = survey_history
    
    return df

# Load existing models on startup if they exist
@app.on_event("startup")
def load_models():
    global hmm_model, rf_model, training_status
    
    try:
        if os.path.exists('models/hmm_model.pkl') and os.path.exists('models/rf_model.pkl'):
            hmm_model = joblib.load('models/hmm_model.pkl')
            rf_model = joblib.load('models/rf_model.pkl')
            training_status["status"] = "trained"
            print("Modelos carregados do disco")
        else:
            print("Nenhum modelo encontrado. Execute /api/train/models para treinar.")
    except Exception as e:
        print(f"Erro ao carregar modelos: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)