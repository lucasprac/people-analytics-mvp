# People Analytics - Predição de Turnover (MVP)

## 1. Visão Geral do Projeto

Este projeto é um **Protótipo MVP (Produto Mínimo Viável)** de uma plataforma de People Analytics focada na **Predição de Risco de Desligamento (Turnover)** de colaboradores.

A solução utiliza uma arquitetura de Machine Learning híbrida, combinando:
1.  **Hidden Markov Model (HMM)** para detectar estados latentes de engajamento e satisfação a partir de dados históricos de *surveys*.
2.  **Random Forest Classifier** para predizer a probabilidade de desligamento, utilizando os estados latentes do HMM e variáveis demográficas/contextuais.

O objetivo é fornecer um dashboard simples e funcional para identificar colaboradores em alto risco e os principais fatores que contribuem para esse risco.

## 2. Arquitetura Técnica

| Componente | Tecnologia | Função |
| :--- | :--- | :--- |
| **Backend** | Python (FastAPI) | API RESTful para servir o modelo de ML, gerenciar dados e fornecer métricas para o dashboard. |
| **Frontend** | Angular (Standalone) | Interface de usuário (Dashboard) para visualização de métricas e interação com o modelo. |
| **Machine Learning** | `hmmlearn`, `scikit-learn` | Implementação dos modelos HMM e Random Forest. |
| **Dados** | Pandas, NumPy | Manipulação e geração de dados sintéticos para o MVP. |

## 3. Estrutura de Pastas

```
people-analytics-mvp/
├── backend/
│   ├── app.py              # Lógica da API FastAPI (endpoints)
│   ├── models.py           # Implementação dos modelos HMM, RF e geração de dados sintéticos
│   ├── requirements.txt    # Dependências Python
│   ├── data/               # Pasta para dados (e.g., employees_data.csv)
│   └── models/             # Pasta para modelos treinados (.pkl)
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.component.ts  # Lógica do Dashboard
│   │   │   ├── app.component.html # Template do Dashboard
│   │   │   ├── app.component.css  # Estilização do Dashboard
│   │   │   ├── app.config.ts      # Configuração do Angular (HttpClient)
│   │   │   └── services/
│   │   │       └── api.service.ts # Serviço de comunicação com o Backend
│   └── ...                 # Arquivos de configuração do Angular
└── README.md
```

## 4. Guia de Configuração e Uso

### 4.1. Pré-requisitos

*   Python 3.11+
*   Node.js e npm (para o Angular)
*   Angular CLI (instalado globalmente: `npm install -g @angular/cli`)

### 4.2. Configuração do Backend (FastAPI)

1.  **Navegue até a pasta do backend:**
    ```bash
    cd people-analytics-mvp/backend
    ```

2.  **Instale as dependências Python:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Inicie o servidor FastAPI:**
    ```bash
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
    ```
    O backend estará acessível em `http://localhost:8000`.

### 4.3. Configuração do Frontend (Angular)

1.  **Navegue até a pasta do frontend:**
    ```bash
    cd people-analytics-mvp/frontend
    ```

2.  **Instale as dependências Node.js:**
    ```bash
    npm install
    ```

3.  **Inicie o servidor de desenvolvimento Angular:**
    ```bash
    ng serve --host 0.0.0.0 --port 4200
    ```
    O frontend estará acessível em `http://localhost:4200`.

### 4.4. Fluxo de Uso do MVP

1.  **Acesse o Dashboard:** Abra `http://localhost:4200` no seu navegador.
2.  **Treine os Modelos:** O dashboard inicialmente mostrará o status "Não Treinado". Clique no botão **"Treinar Modelos"** no canto superior direito.
    *   Esta ação chama o endpoint `/api/train/models` do backend.
    *   O backend gera um dataset sintético de 500 colaboradores.
    *   O HMM e o Random Forest são treinados com esses dados.
    *   Os modelos treinados são salvos na pasta `backend/models/`.
3.  **Visualize os Resultados:** Após o treinamento (que pode levar alguns segundos), o dashboard será recarregado, exibindo:
    *   **Métricas Chave:** Risco Médio, Contagem de Colaboradores por Categoria de Risco.
    *   **Feature Importance:** Um gráfico de barras mostrando os fatores mais importantes na predição de desligamento (baseado no Random Forest).
    *   **Amostra de Colaboradores:** Uma lista de colaboradores (mockada no frontend, mas com base nas métricas do backend) com seu risco de desligamento.

## 5. Endpoints da API (FastAPI)

A documentação completa da API está disponível em `http://localhost:8000/docs` (Swagger UI).

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/health` | Verifica o status do serviço. |
| `POST` | `/api/train/models` | Inicia o treinamento dos modelos HMM e Random Forest. Aceita um arquivo CSV opcionalmente. |
| `GET` | `/api/analytics/dashboard` | Retorna métricas agregadas para o dashboard (risco médio, contagens). |
| `GET` | `/api/analytics/feature-importance` | Retorna a importância das features do modelo Random Forest. |
| `POST` | `/api/predict/desligamento` | Recebe uma lista de dados de colaboradores e retorna a predição de risco. |

## 6. Próximos Passos (Fase 2)

Para evoluir este MVP para um produto completo, as seguintes melhorias são sugeridas:

*   **Persistência de Dados:** Substituir a geração de dados sintéticos por uma conexão real com um banco de dados (e.g., PostgreSQL, conforme sugerido no prompt original).
*   **Autenticação:** Implementar um sistema de login e controle de acesso (e.g., JWT).
*   **Upload de Dados:** Aprimorar o endpoint de treinamento para lidar com o upload de arquivos CSV de forma mais robusta.
*   **Detalhes do Colaborador:** Criar uma tela de detalhes para cada colaborador, mostrando o histórico de surveys e a evolução do estado HMM.

---
**Desenvolvido por:** Manus AI
**Data:** Novembro de 2025
