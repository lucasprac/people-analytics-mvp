# People Analytics MVP (Turnover)

Plataforma MVP para predição de risco de desligamento usando HMM (estados latentes de engajamento) + Random Forest.

## Stack
- Backend: FastAPI, scikit-learn, hmmlearn
- Frontend: Angular 17 + Angular Material

## Como rodar localmente

### Backend
1. cd backend
2. python -m venv .venv && source .venv/bin/activate  (Windows: .venv\Scripts\activate)
3. pip install -r requirements.txt
4. python generate_dataset.py  (opcional para gerar dataset de exemplo)
5. uvicorn app:app --reload --host 0.0.0.0 --port 8000

Endpoints úteis:
- GET /health
- POST /api/train/models
- GET /api/train/status
- POST /api/predict/desligamento
- GET /api/analytics/feature-importance
- GET /api/files/roc-curve

### Frontend
1. cd frontend
2. npm install
3. npm start
4. Acesse http://localhost:4200

## Estrutura
- backend/
  - app.py (API FastAPI)
  - models.py (HMM + RandomForest)
  - generate_dataset.py (gerador sintético)
  - requirements.txt
- frontend/
  - angular.json, tsconfig.json, package.json
  - src/
    - index.html, main.ts, styles.scss
    - app/
      - app.component.ts, app.routes.ts
      - services/api.service.ts
      - pages/
        - dashboard/
        - predictions/
        - training/
        - analytics/

## Observações
- Evitamos Docker conforme seu pedido.
- O frontend espera o backend em http://localhost:8000
- Para produção, configurar CORS restrito e variáveis de ambiente.
