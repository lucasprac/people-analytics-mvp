# Guia de Deploy

## Deploy do Frontend no Vercel

1. **Conectar repositório ao Vercel**
   - Acesse [vercel.com](https://vercel.com)
   - Conecte sua conta GitHub
   - Importe o repositório `lucasprac/people-analytics-mvp`

2. **Configurar projeto**
   - Root Directory: `frontend`
   - Framework Preset: Angular
   - Build Command: `npm run build`
   - Output Directory: `dist/people-analytics-frontend`
   - Install Command: `npm install`

3. **Variáveis de ambiente (opcional)**
   ```
   NODE_ENV=production
   ```

4. **Deploy automático**
   - O Vercel irá fazer deploy automaticamente a cada push na branch `master`
   - URL final será algo como: `https://people-analytics-frontend.vercel.app`

## Deploy do Backend no Render

1. **Conectar repositório ao Render**
   - Acesse [render.com](https://render.com)
   - Conecte sua conta GitHub
   - Crie um novo Web Service
   - Conecte ao repositório `lucasprac/people-analytics-mvp`

2. **Configurar serviço**
   - Name: `people-analytics-backend`
   - Environment: `Python 3`
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

3. **Variáveis de ambiente**
   ```
   ENVIRONMENT=production
   CORS_ORIGINS=https://people-analytics-frontend.vercel.app
   ```

4. **Configurações adicionais**
   - Plan: Free
   - Health Check Path: `/health`
   - Auto-Deploy: Yes

5. **URL final**
   - Será algo como: `https://people-analytics-backend.onrender.com`

## Após o Deploy

1. **Atualizar URL do backend no frontend**
   - Editar `frontend/src/environments/environment.prod.ts`
   - Colocar a URL real do Render: `https://people-analytics-backend.onrender.com/api`

2. **Testar aplicação**
   - Acesse a URL do frontend no Vercel
   - Teste os endpoints principais:
     - Dashboard
     - Treinamento de modelos
     - Predições
     - Analytics

3. **Primeira execução**
   - Vá para a página "Treinamento"
   - Execute o treinamento com dados sintéticos (500 colaboradores, 12 meses)
   - Aguarde alguns minutos para o treinamento completar
   - Acesse o Dashboard para ver as métricas
   - Teste uma predição na página "Predições"

## Troubleshooting

- **CORS errors**: Verificar se a URL do frontend está nas variáveis `CORS_ORIGINS` do backend
- **Build errors**: Verificar se todos os arquivos necessários estão commitados
- **API errors**: Verificar logs no Render dashboard
- **Frontend não conecta**: Verificar se a URL do backend está correta no `environment.prod.ts`

## Monitoramento

- **Backend**: Logs disponíveis no Render dashboard
- **Frontend**: Logs disponíveis no Vercel dashboard  
- **Health check**: `https://people-analytics-backend.onrender.com/health`
