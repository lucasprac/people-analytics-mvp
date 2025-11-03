import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-training',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatCheckboxModule,
    MatIconModule
  ],
  template: `
    <div class="training-container">
      <h1>Treinamento dos Modelos</h1>
      <p>Configure e execute o treinamento dos modelos HMM + Random Forest</p>
    </div>
  `,
  styles: [`
    .training-container {
      max-width: 800px;
      margin: 0 auto;
    }
  `]
})
export class TrainingComponent implements OnInit {
  trainingForm: FormGroup;
  trainingStatus: any = null;
  isTraining = false;
  isGenerating = false;

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private snackBar: MatSnackBar
  ) {
    this.trainingForm = this.fb.group({
      use_synthetic: [true],
      n_employees: [500, [Validators.required, Validators.min(100), Validators.max(2000)]],
      n_months: [12, [Validators.required, Validators.min(6), Validators.max(24)]],
      filepath: ['data/employees_data.csv']
    });
  }

  ngOnInit() {
    // Implementation here
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

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString('pt-BR');
  }
}