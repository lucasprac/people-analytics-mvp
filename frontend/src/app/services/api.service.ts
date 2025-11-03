import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface EmployeeData {
  employee_id: number;
  idade: number;
  tempo_empresa: number;
  departamento: string;
  nivel: string;
  faixa_salarial: string;
  localizacao: string;
  promovido: number;
  aumento_salarial: number;
  manidader_change: number;
  treinamentos: number;
  avaliacao_performance: number;
  avg_engidadement: number;
  satisfacao_media: number;
  reconhecimento_medio: number;
  crescimento_medio: number;
  avg_manidader_rel: number;
  equilibrio_vida_trabalho_medio: number;
}

export interface TurnoverPrediction {
  employee_id: number;
  desligamento_risk: number;
  risk_category: string;
  confidence: number;
}

export interface TrainModelsRequest {
  filepath?: string;
  n_employees?: number;
  n_months?: number;
  use_synthetic?: boolean;
}

export interface DashboardMetrics {
  model_status: string;
  total_employees: number;
  avg_desligamento_risk: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  last_trained?: string;
  model_performance?: any;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  // Training endpoints
  trainModels(request: TrainModelsRequest): Observable<any> {
    return this.http.post(`${this.baseUrl}/train/models`, request);
  }

  getTrainingStatus(): Observable<any> {
    return this.http.get(`${this.baseUrl}/train/status`);
  }

  // Prediction endpoints
  predictTurnover(employees: EmployeeData[]): Observable<TurnoverPrediction[]> {
    return this.http.post<TurnoverPrediction[]>(`${this.baseUrl}/predict/desligamento`, employees);
  }

  predictSingleEmployee(employee: EmployeeData): Observable<TurnoverPrediction> {
    return this.http.post<TurnoverPrediction>(`${this.baseUrl}/predict/single`, employee);
  }

  // Analytics endpoints
  getFeatureImportance(topN: number = 15): Observable<FeatureImportance[]> {
    return this.http.get<FeatureImportance[]>(`${this.baseUrl}/analytics/feature-importance?top_n=${topN}`);
  }

  getDashboardMetrics(): Observable<DashboardMetrics> {
    return this.http.get<DashboardMetrics>(`${this.baseUrl}/analytics/dashboard`);
  }

  // Data generation
  generateSampleDataset(nEmployees: number = 500, nMonths: number = 12): Observable<any> {
    return this.http.post(`${this.baseUrl}/data/generate`, {
      n_employees: nEmployees,
      n_months: nMonths
    });
  }

  // File endpoints
  getRocCurve(): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/files/roc-curve`, { responseType: 'blob' });
  }

  uploadDataset(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.baseUrl}/files/upload`, formData);
  }

  // Health check
  healthCheck(): Observable<any> {
    return this.http.get('http://localhost:8000/health');
  }
}