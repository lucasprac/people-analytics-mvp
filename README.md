# People Analytics MVP - Predição de Turnover

Plataforma MVP para predição de risco de desligamento usando **HMM** (Hidden Markov Models) para detectar estados latentes de engajamento + **Random Forest** para predição final.

## 🚀 Demo Online

- **Frontend**: https://people-analytics-frontend.vercel.app *(aguardando deploy)*
- **Backend API**: https://people-analytics-backend.onrender.com *(aguardando deploy)*
- **Documentação da API**: https://people-analytics-backend.onrender.com/docs

## 📋 Funcionalidades

- **Dashboard**: Métricas em tempo real, status do modelo, distribuição de risco
- **Predições**: Interface para inserir dados de colaboradores e obter risco de turnover
- **Treinamento**: Treinamento de modelos com dados sintéticos ou upload de CSV
- **Analytics**: Análise de importância de features, curva ROC, insights do modelo

## 🛠 Stack Tecnológica

### Backend
- **FastAPI** - API moderna e rápida
- **scikit-learn** - Random Forest Classifier
- **hmmlearn** - Hidden Markov Models
- **pandas/numpy** - Processamento de dados
- **uvicorn** - ASGI server

### Frontend
- **Angular 17** - Framework SPA
- **Angular Material** - UI Components
- **TypeScript** - Tipagem estática
- **RxJS** - Programação reativa

## 🏃‍♂️ Como rodar localmente

### Pré-requisitos
- Python 3.9+ 
- Node.js 18+
- npm ou yarn

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt

# Gerar dados de exemplo (opcional)
python generate_dataset.py

# Rodar servidor
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm start
```

Acesse: http://localhost:4200

## 🚀 Deploy

Ver [DEPLOY.md](./DEPLOY.md) para instruções completas de deploy no **Vercel** (frontend) e **Render** (backend).

## 📊 Como usar

1. **Primeira execução**: Vá para "Treinamento" e treine os modelos com dados sintéticos
2. **Dashboard**: Visualize métricas gerais e performance dos modelos
3. **Predições**: Insira dados de um colaborador para obter o risco de turnover
4. **Analytics**: Analise quais fatores mais influenciam o turnover

## 📈 Metodologia

### Dados Utilizados
- **Demografia**: Idade, tempo empresa, departamento, nível, localização
- **Histórico**: Promoções, aumentos, mudança de gestor, treinamentos, performance
- **Surveys**: Engajamento, satisfação, reconhecimento, crescimento, relacionamento, work-life balance

### Modelo HMM
- **3 Estados Latentes**: Engajado, Neutro, Em Risco de Saída
- **Features de Entrada**: Histórico mensal dos surveys (escala Likert 1-5)
- **Saída**: Estado atual + probabilidades de cada estado

### Modelo Random Forest
- **Features**: Demografia + histórico + médias de survey + estado HMM atual
- **Target**: Desligamento (0/1)
- **Saída**: Probabilidade de desligamento + categoria de risco (Alto/Médio/Baixo)

## 📁 Estrutura do Projeto

```
.
├── backend/
│   ├── app.py                 # API FastAPI principal
│   ├── models.py              # Classes HMM + Random Forest
│   ├── generate_dataset.py    # Gerador de dados sintéticos
│   ├── requirements.txt       # Dependências Python
│   └── render.yaml           # Config deploy Render
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── pages/         # Páginas da aplicação
│   │   │   └── services/      # Serviços API
│   │   └── environments/     # Config ambiente
│   ├── angular.json
│   ├── package.json
│   └── vercel.json           # Config deploy Vercel
├── README.md
└── DEPLOY.md                 # Guia de deploy
```

## 🔗 Endpoints da API

- `GET /health` - Health check
- `POST /api/train/models` - Treinar modelos
- `GET /api/train/status` - Status do treinamento
- `POST /api/predict/desligamento` - Predição em lote
- `POST /api/predict/single` - Predição individual
- `GET /api/analytics/feature-importance` - Importância das features
- `GET /api/analytics/dashboard` - Métricas do dashboard
- `POST /api/data/generate` - Gerar dataset sintético
- `GET /api/files/roc-curve` - Download curva ROC

## 🧪 Dados Sintéticos

O sistema gera automaticamente:
- **500 colaboradores** (configurável)
- **12 meses** de histórico de surveys (configurável) 
- **Taxa de turnover realista** (~15-25%)
- **Padrões comportamentais** que influenciam o desligamento

## ⚠️ Limitações do MVP

- Dados sintéticos (não há integração com HRIS reais)
- Modelos simples (3 estados HMM, Random Forest padrão)
- Sem persistência em banco de dados
- Sem autenticação/autorização
- Interface básica (foco na funcionalidade)

## 🎯 Próximos Passos

- [ ] Integração com HRIS (Workday, SAP, etc.)
- [ ] Banco de dados para persistência
- [ ] Autenticação e controle de acesso
- [ ] Modelos mais sofisticados (Deep Learning)
- [ ] Dashboard mais avançado com gráficos interativos
- [ ] Alertas e notificações automáticas
- [ ] Export de relatórios (PDF, Excel)
- [ ] API de integração para outros sistemas

---

**Desenvolvido por**: [Lucas Prado](https://github.com/lucasprac)
