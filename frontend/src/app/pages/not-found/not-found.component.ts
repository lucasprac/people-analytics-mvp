import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-page-not-found',
  standalone: true,
  imports: [CommonModule],
  template: `<div class="not-found"><h2>Página não encontrada</h2></div>`,
  styles: [`.not-found{padding:40px;text-align:center;color:#666}`]
})
export class PageNotFoundComponent {}
