import pandas as pd
from models import generate_synthetic_data, SurveyStateDetector, TurnoverPredictor
import os

# 1. Geração de Dados
df = generate_synthetic_data()
print(f"Shape do Dataset Sintético: {df.shape}")
print(f"Taxa de Desligamento: {df['desligamento'].mean():.2f}")

# 2. Treinamento HMM
detector = SurveyStateDetector(n_states=3)
detector.fit(df)
state_sequences = detector.predict_states(df)
df = detector.get_current_state(df, state_sequences)
state_probs = detector.get_state_probabilities(df)
print(f"HMM treinado. Colunas adicionadas: {list(df.columns[-1:])}")

# 3. Treinamento Random Forest
predictor = TurnoverPredictor()
results = predictor.train(df, state_probs=state_probs)
print(f"Random Forest treinado. Test AUC: {results['auc']:.3f}")

# 4. Verificar se o arquivo ROC foi criado
roc_path = os.path.join(os.getcwd(), 'roc_curve.png')
if os.path.exists(roc_path):
    print(f"Gráfico ROC criado com sucesso em: {roc_path}")
    os.remove(roc_path) # Limpar o arquivo
else:
    print("ERRO: Gráfico ROC não foi criado.")

print('Teste de modelos concluído com sucesso.')
