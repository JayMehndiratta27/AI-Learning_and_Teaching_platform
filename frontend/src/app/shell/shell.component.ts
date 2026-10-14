import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { AuthService } from '../core/services/auth.service';
import { ThemeService } from '../core/services/theme.service';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
  ],
  templateUrl: './shell.component.html',
  styleUrl: './shell.component.scss',
})
export class ShellComponent {
  readonly auth = inject(AuthService);
  readonly theme = inject(ThemeService);

  nav = [
    { label: 'Dashboard', icon: 'dashboard', path: '/dashboard' },
    { label: 'Courses', icon: 'school', path: '/courses' },
    { label: 'Videos', icon: 'play_circle', path: '/videos' },
    { label: 'AI Tutor', icon: 'smart_toy', path: '/chat' },
    { label: 'Quizzes', icon: 'quiz', path: '/quizzes' },
    { label: 'Progress', icon: 'insights', path: '/progress' },
    { label: 'Downloads', icon: 'download', path: '/downloads' },
    { label: 'Notifications', icon: 'notifications', path: '/notifications' },
    { label: 'Settings', icon: 'settings', path: '/settings' },
  ];
}
