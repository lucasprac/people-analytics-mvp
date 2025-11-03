import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { ApiService, DashboardMetrics } from '../../services/api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatChipsModule
  ],
  template: `
    <div class="dashboard-container">
      <h1>Dashboard - People Analytics</h1>
      
      <div class="metrics-grid" *ngIf="metrics; else loading">
        <!-- Status do Modelo -->
        <mat-card class="metric-card status-card">
          <mat-card-header>
            <mat-icon mat-card-avatar>model_training</mat-icon>
            <mat-card-title>Status do Modelo</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="status-content">
              <mat-chip [color]="getStatusColor(metrics.model_status)" selected>
                {{getStatusText(metrics.model_status)}}
              </mat-chip>
              <p *ngIf="metrics.last_trained" class="last-trained">
                Último treinamento: {{formatDate(metrics.last_trained)}}
              </p>
            </div>
          </mat-card-content>
        </mat-card>

        <!-- Total de Colaboradores -->
        <mat-card class="metric-card">
          <mat-card-header>
            <mat-icon mat-card-avatar>people</mat-icon>
            <mat-card-title>Total de Colaboradores</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="metric-value">{{metrics.total_employees}}</div>
          </mat-card-content>
        </mat-card>

        <!-- Risco Médio -->
        <mat-card class="metric-card">
          <mat-card-header>
            <mat-icon mat-card-avatar>trending_up</mat-icon>
            <mat-card-title>Risco Médio de Turnover</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="metric-value">{{(metrics.avg_desligamento_risk * 100).toFixed(1)}}%</div>
          </mat-card-content>
        </mat-card>

        <!-- Distribuição por Risco -->
        <mat-card class="metric-card risk-distribution">
          <mat-card-header>
            <mat-icon mat-card-avatar>pie_chart</mat-icon>
            <mat-card-title>Distribuição por Nível de Risco</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="risk-bars">
              <div class="risk-item">
                <span class="risk-label high">Alto</span>
                <div class="risk-bar">
                  <div class="risk-fill high" [style.width.%]="getRiskPercentage('high')"></div>
                </div>
                <span class="risk-count">{{metrics.high_risk_count}}</span>
              </div>
              <div class="risk-item">
                <span class="risk-label medium">Médio</span>
                <div class="risk-bar">
                  <div class="risk-fill medium" [style.width.%]="getRiskPercentage('medium')"></div>
                </div>
                <span class="risk-count">{{metrics.medium_risk_count}}</span>
              </div>
              <div class="risk-item">
                <span class="risk-label low">Baixo</span>
                <div class="risk-bar">
                  <div class="risk-fill low" [style.width.%]="getRiskPercentage('low')"></div>
                </div>
                <span class="risk-count">{{metrics.low_risk_count}}</span>
              </div>
            </div>
          </mat-card-content>
        </mat-card>

        <!-- Performance do Modelo -->
        <mat-card class="metric-card performance-card" *ngIf="metrics.model_performance">
          <mat-card-header>
            <mat-icon mat-card-avatar>analytics</mat-icon>
            <mat-card-title>Performance do Modelo</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="performance-metrics">
              <div class="perf-item">
                <span class="perf-label">AUC Score</span>
                <span class="perf-value">{{metrics.model_performance.test_auc?.toFixed(3)}}</span>
              </div>
              <div class="perf-item">
                <span class="perf-label">Taxa de Turnover</span>
                <span class="perf-value">{{(metrics.model_performance.turnover_rate * 100)?.toFixed(1)}}%</span>
              </div>
              <div class="perf-item">
                <span class="perf-label">Estados HMM</span>
                <span class="perf-value">{{metrics.model_performance.hmm_states}}</span>
              </div>
            </div>
          </mat-card-content>
        </mat-card>
      </div>

      <ng-template #loading>
        <div class="loading-container">
          <mat-spinner></mat-spinner>
          <p>Carregando métricas do dashboard...</p>
        </div>
      </ng-template>
    </div>
  `,
  styles: [`
    .dashboard-container {
      max-width: 1200px;
      margin: 0 auto;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin-top: 20px;
    }

    .metric-card {
      height: fit-content;
    }

    .metric-value {
      font-size: 2.5em;
      font-weight: bold;
      color: #1976d2;
      text-align: center;
      margin: 10px 0;
    }

    .status-content {
      text-align: center;
    }

    .last-trained {
      margin-top: 10px;
      color: #666;
      font-size: 0.9em;
    }

    .risk-bars {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .risk-item {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .risk-label {
      width: 60px;
      font-weight: bold;
    }

    .risk-label.high { color: #f44336; }
    .risk-label.medium { color: #ff9800; }
    .risk-label.low { color: #4caf50; }

    .risk-bar {
      flex: 1;
      height: 20px;
      background-color: #e0e0e0;
      border-radius: 10px;
      overflow: hidden;
    }

    .risk-fill {
      height: 100%;
      transition: width 0.5s ease;
    }

    .risk-fill.high { background-color: #f44336; }
    .risk-fill.medium { background-color: #ff9800; }
    .risk-fill.low { background-color: #4caf50; }

    .risk-count {
      width: 40px;
      text-align: right;
      font-weight: bold;
    }

    .performance-metrics {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .perf-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .perf-label {
      font-weight: 500;
    }

    .perf-value {
      font-weight: bold;
      color: #1976d2;
    }

    .loading-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 50px;
    }
  `]
})
export class DashboardComponent implements OnInit {
  metrics: DashboardMetrics | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadDashboardMetrics();
  }

  loadDashboardMetrics() {
    this.apiService.getDashboardMetrics().subscribe({
      next: (data) => {
        this.metrics = data;
      },
      error: (error) => {
        console.error('Erro ao carregar métricas:', error);
      }
    });
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'trained': return 'primary';
      case 'training': return 'accent';
      case 'error': return 'warn';
      default: return 'basic';
    }
  }

  getStatusText(status: string): string {
    switch (status) {
      case 'trained': return 'Treinado';
      case 'training': return 'Treinando';
      case 'error': return 'Erro';
      case 'not_trained': return 'Não Treinado';
      default: return 'Desconhecido';
    }
  }

  getRiskPercentage(riskLevel: string): number {
    if (!this.metrics) return 0;
    
    const total = this.metrics.high_risk_count + this.metrics.medium_risk_count + this.metrics.low_risk_count;
    if (total === 0) return 0;

    switch (riskLevel) {
      case 'high': return (this.metrics.high_risk_count / total) * 100;
      case 'medium': return (this.metrics.medium_risk_count / total) * 100;
      case 'low': return (this.metrics.low_risk_count / total) * 100;
      default: return 0;
    }
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString('pt-BR');
  }
}