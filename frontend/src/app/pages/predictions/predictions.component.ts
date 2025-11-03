import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService, EmployeeData, TurnoverPrediction } from '../../services/api.service';

@Component({
  selector: 'app-predictions',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatIconModule
  ],
  template: `
    <div class="predictions-container">
      <h1>Predições de Turnover</h1>
      
      <mat-card class="form-card">
        <mat-card-header>
          <mat-card-title>Dados do Colaborador</mat-card-title>
          <mat-card-subtitle>Preencha os dados para obter a predição de risco de desligamento</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <form [formGroup]="employeeForm" class="employee-form">
            <!-- Linha 1: ID e dados pessoais -->
            <div class="form-row">
              <mat-form-field>
                <mat-label>ID do Colaborador</mat-label>
                <input matInput type="number" formControlName="employee_id" required>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Idade</mat-label>
                <input matInput type="number" formControlName="idade" required>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Tempo na Empresa (meses)</mat-label>
                <input matInput type="number" formControlName="tempo_empresa" required>
              </mat-form-field>
            </div>

            <!-- Linha 2: Departamento e nível -->
            <div class="form-row">
              <mat-form-field>
                <mat-label>Departamento</mat-label>
                <mat-select formControlName="departamento" required>
                  <mat-option value="Sales">Vendas</mat-option>
                  <mat-option value="Engineering">Engenharia</mat-option>
                  <mat-option value="HR">Recursos Humanos</mat-option>
                  <mat-option value="Marketing">Marketing</mat-option>
                  <mat-option value="Finance">Financeiro</mat-option>
                </mat-select>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Nível</mat-label>
                <mat-select formControlName="nivel" required>
                  <mat-option value="Junior">Junior</mat-option>
                  <mat-option value="Pleno">Pleno</mat-option>
                  <mat-option value="Senior">Senior</mat-option>
                </mat-select>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Faixa Salarial</mat-label>
                <mat-select formControlName="faixa_salarial" required>
                  <mat-option value="Entry">Inicial</mat-option>
                  <mat-option value="Mid">Média</mat-option>
                  <mat-option value="Senior">Alta</mat-option>
                </mat-select>
              </mat-form-field>
            </div>

            <!-- Linha 3: Localização e eventos -->
            <div class="form-row">
              <mat-form-field>
                <mat-label>Localização</mat-label>
                <mat-select formControlName="localizacao" required>
                  <mat-option value="Remoto">Remoto</mat-option>
                  <mat-option value="Híbrido">Híbrido</mat-option>
                  <mat-option value="Presencial">Presencial</mat-option>
                </mat-select>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Promovido (0=Não, 1=Sim)</mat-label>
                <mat-select formControlName="promovido" required>
                  <mat-option value="0">Não</mat-option>
                  <mat-option value="1">Sim</mat-option>
                </mat-select>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Aumento Salarial (%)</mat-label>
                <input matInput type="number" step="0.1" formControlName="aumento_salarial" required>
              </mat-form-field>
            </div>

            <!-- Linha 4: Histórico e performance -->
            <div class="form-row">
              <mat-form-field>
                <mat-label>Mudança de Gestor (0=Não, 1=Sim)</mat-label>
                <mat-select formControlName="manidader_change" required>
                  <mat-option value="0">Não</mat-option>
                  <mat-option value="1">Sim</mat-option>
                </mat-select>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Treinamentos</mat-label>
                <input matInput type="number" formControlName="treinamentos" required>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Avaliação de Performance (1-5)</mat-label>
                <input matInput type="number" step="0.1" min="1" max="5" formControlName="avaliacao_performance" required>
              </mat-form-field>
            </div>

            <!-- Linha 5: Scores de survey -->
            <div class="form-row">
              <mat-form-field>
                <mat-label>Engajamento Médio (1-5)</mat-label>
                <input matInput type="number" step="0.1" min="1" max="5" formControlName="avg_engidadement" required>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Satisfação Média (1-5)</mat-label>
                <input matInput type="number" step="0.1" min="1" max="5" formControlName="satisfacao_media" required>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Reconhecimento Médio (1-5)</mat-label>
                <input matInput type="number" step="0.1" min="1" max="5" formControlName="reconhecimento_medio" required>
              </mat-form-field>
            </div>

            <!-- Linha 6: Mais scores -->
            <div class="form-row">
              <mat-form-field>
                <mat-label>Crescimento Médio (1-5)</mat-label>
                <input matInput type="number" step="0.1" min="1" max="5" formControlName="crescimento_medio" required>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Relacionamento com Gestor (1-5)</mat-label>
                <input matInput type="number" step="0.1" min="1" max="5" formControlName="avg_manidader_rel" required>
              </mat-form-field>
              <mat-form-field>
                <mat-label>Equilíbrio Vida-Trabalho (1-5)</mat-label>
                <input matInput type="number" step="0.1" min="1" max="5" formControlName="equilibrio_vida_trabalho_medio" required>
              </mat-form-field>
            </div>
          </form>
        </mat-card-content>
        <mat-card-actions>
          <button mat-raised-button color="primary" 
                  (click)="predictTurnover()" 
                  [disabled]="employeeForm.invalid || loading">
            <mat-icon *ngIf="loading">hourglass_empty</mat-icon>
            <mat-icon *ngIf="!loading">psychology</mat-icon>
            {{loading ? 'Analisando...' : 'Prever Risco'}}
          </button>
          <button mat-button (click)="fillSampleData()">Preencher Dados de Exemplo</button>
        </mat-card-actions>
      </mat-card>

      <!-- Resultado da Predição -->
      <mat-card class="result-card" *ngIf="prediction">
        <mat-card-header>
          <mat-icon mat-card-avatar [class]="getRiskIconClass(prediction.risk_category)">{{getRiskIcon(prediction.risk_category)}}</mat-icon>
          <mat-card-title>Resultado da Predição</mat-card-title>
          <mat-card-subtitle>Colaborador ID: {{prediction.employee_id}}</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <div class="prediction-result">
            <div class="risk-level">
              <h3>Nível de Risco</h3>
              <mat-chip [class]="getRiskChipClass(prediction.risk_category)" selected>
                {{prediction.risk_category}}
              </mat-chip>
            </div>
            <div class="risk-probability">
              <h3>Probabilidade de Desligamento</h3>
              <div class="probability-value">{{(prediction.desligamento_risk * 100).toFixed(1)}}%</div>
            </div>
            <div class="confidence">
              <h3>Confiança da Predição</h3>
              <div class="confidence-value">{{(prediction.confidence * 100).toFixed(1)}}%</div>
            </div>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .predictions-container {
      max-width: 1000px;
      margin: 0 auto;
    }

    .form-card, .result-card {
      margin-bottom: 20px;
    }

    .employee-form {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .form-row {
      display: flex;
      gap: 20px;
      flex-wrap: wrap;
    }

    .form-row mat-form-field {
      flex: 1;
      min-width: 200px;
    }

    .prediction-result {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      text-align: center;
    }

    .probability-value, .confidence-value {
      font-size: 2em;
      font-weight: bold;
      margin-top: 10px;
    }

    .probability-value {
      color: #f44336;
    }

    .confidence-value {
      color: #4caf50;
    }

    .risk-level {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 10px;
    }

    .risk-chip-alto {
      background-color: #f44336 !important;
      color: white !important;
    }

    .risk-chip-medio {
      background-color: #ff9800 !important;
      color: white !important;
    }

    .risk-chip-baixo {
      background-color: #4caf50 !important;
      color: white !important;
    }

    .risk-icon-alto {
      background-color: #f44336;
      color: white;
    }

    .risk-icon-medio {
      background-color: #ff9800;
      color: white;
    }

    .risk-icon-baixo {
      background-color: #4caf50;
      color: white;
    }

    @media (max-width: 768px) {
      .form-row {
        flex-direction: column;
      }
      
      .prediction-result {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class PredictionsComponent {
  employeeForm: FormGroup;
  prediction: TurnoverPrediction | null = null;
  loading = false;

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private snackBar: MatSnackBar
  ) {
    this.employeeForm = this.createForm();
  }

  private createForm(): FormGroup {
    return this.fb.group({
      employee_id: [1, [Validators.required, Validators.min(1)]],
      idade: [30, [Validators.required, Validators.min(18), Validators.max(70)]],
      tempo_empresa: [24, [Validators.required, Validators.min(1)]],
      departamento: ['Engineering', Validators.required],
      nivel: ['Pleno', Validators.required],
      faixa_salarial: ['Mid', Validators.required],
      localizacao: ['Híbrido', Validators.required],
      promovido: [0, Validators.required],
      aumento_salarial: [5.0, [Validators.required, Validators.min(0)]],
      manidader_change: [0, Validators.required],
      treinamentos: [2, [Validators.required, Validators.min(0)]],
      avaliacao_performance: [3.5, [Validators.required, Validators.min(1), Validators.max(5)]],
      avg_engidadement: [3.2, [Validators.required, Validators.min(1), Validators.max(5)]],
      satisfacao_media: [3.1, [Validators.required, Validators.min(1), Validators.max(5)]],
      reconhecimento_medio: [3.0, [Validators.required, Validators.min(1), Validators.max(5)]],
      crescimento_medio: [2.8, [Validators.required, Validators.min(1), Validators.max(5)]],
      avg_manidader_rel: [3.4, [Validators.required, Validators.min(1), Validators.max(5)]],
      equilibrio_vida_trabalho_medio: [3.3, [Validators.required, Validators.min(1), Validators.max(5)]]
    });
  }

  fillSampleData() {
    this.employeeForm.patchValue({
      employee_id: Math.floor(Math.random() * 1000) + 1,
      idade: Math.floor(Math.random() * 30) + 25,
      tempo_empresa: Math.floor(Math.random() * 60) + 6,
      departamento: ['Sales', 'Engineering', 'HR', 'Marketing', 'Finance'][Math.floor(Math.random() * 5)],
      nivel: ['Junior', 'Pleno', 'Senior'][Math.floor(Math.random() * 3)],
      faixa_salarial: ['Entry', 'Mid', 'Senior'][Math.floor(Math.random() * 3)],
      localizacao: ['Remoto', 'Híbrido', 'Presencial'][Math.floor(Math.random() * 3)],
      promovido: Math.random() > 0.8 ? 1 : 0,
      aumento_salarial: Math.random() * 15,
      manidader_change: Math.random() > 0.85 ? 1 : 0,
      treinamentos: Math.floor(Math.random() * 5),
      avaliacao_performance: 2.5 + Math.random() * 2.5,
      avg_engidadement: 1 + Math.random() * 4,
      satisfacao_media: 1 + Math.random() * 4,
      reconhecimento_medio: 1 + Math.random() * 4,
      crescimento_medio: 1 + Math.random() * 4,
      avg_manidader_rel: 1 + Math.random() * 4,
      equilibrio_vida_trabalho_medio: 1 + Math.random() * 4
    });
  }

  predictTurnover() {
    if (this.employeeForm.invalid) {
      this.snackBar.open('Por favor, preencha todos os campos corretamente', 'Fechar', { duration: 3000 });
      return;
    }

    this.loading = true;
    const employeeData: EmployeeData = this.employeeForm.value;

    this.apiService.predictSingleEmployee(employeeData).subscribe({
      next: (result) => {
        this.prediction = result;
        this.loading = false;
        this.snackBar.open('Predição realizada com sucesso!', 'Fechar', { duration: 3000 });
      },
      error: (error) => {
        console.error('Erro na predição:', error);
        this.loading = false;
        this.snackBar.open('Erro ao realizar predição. Verifique se o modelo foi treinado.', 'Fechar', { duration: 5000 });
      }
    });
  }

  getRiskChipClass(category: string): string {
    return `risk-chip-${category.toLowerCase()}`;
  }

  getRiskIconClass(category: string): string {
    return `risk-icon-${category.toLowerCase()}`;
  }

  getRiskIcon(category: string): string {
    switch (category.toLowerCase()) {
      case 'alto': return 'warning';
      case 'medio': return 'info';
      case 'baixo': return 'check_circle';
      default: return 'help';
    }
  }
}