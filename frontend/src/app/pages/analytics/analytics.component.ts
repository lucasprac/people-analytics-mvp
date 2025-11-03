import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { ApiService, FeatureImportance } from '../../services/api.service';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatTableModule,
    MatProgressSpinnerModule,
    MatIconModule,
    MatButtonModule
  ],
  template: `
    <div class="analytics-container">
      <h1>Análises Avançadas</h1>
      <p>Análise de importância das features e insights do modelo</p>
    </div>
  `,
  styles: [`
    .analytics-container {
      max-width: 1000px;
      margin: 0 auto;
    }
  `]
})
export class AnalyticsComponent implements OnInit {
  featureImportance: FeatureImportance[] = [];
  displayedColumns: string[] = ['rank', 'feature', 'importance'];
  maxImportance = 0;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    // Implementation here
  }

  translateFeature(feature: string): string {
    const translations: {[key: string]: string} = {
      'idade': 'Idade',
      'tempo_empresa': 'Tempo na Empresa',
      'promovido': 'Promovido',
      'aumento_salarial': 'Aumento Salarial',
      'manager_change': 'Mudança de Gestor',
      'treinamentos': 'Treinamentos',
      'avaliacao_performance': 'Avaliação de Performance',
      'avg_engajamento': 'Engajamento Médio',
      'satisfacao_media': 'Satisfação Média',
      'reconhecimento_medio': 'Reconhecimento Médio',
      'crescimento_medio': 'Crescimento Médio',
      'avg_manager_rel': 'Relacionamento com Gestor',
      'equilibrio_vida_trabalho_medio': 'Equilíbrio Vida-Trabalho',
      'current_hmm_state': 'Estado HMM Atual'
    };
    
    return translations[feature] || feature;
  }
}