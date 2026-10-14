import { Routes } from '@angular/router';
import { authGuard, guestGuard } from './core/guards/auth.guard';
import { LandingComponent } from './pages/landing/landing.component';
import { LoginComponent } from './pages/auth/login.component';
import { SignupComponent } from './pages/auth/signup.component';
import { ForgotPasswordComponent } from './pages/auth/forgot-password.component';
import { ResetPasswordComponent } from './pages/auth/reset-password.component';
import { ShellComponent } from './shell/shell.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { CoursesComponent } from './pages/courses/courses.component';
import { CourseDetailComponent } from './pages/courses/course-detail.component';
import { VideosComponent } from './pages/videos/videos.component';
import { ChatPageComponent } from './pages/chat/chat-page.component';
import { QuizListComponent } from './pages/quiz/quiz-list.component';
import { QuizTakeComponent } from './pages/quiz/quiz-take.component';
import { ProgressComponent } from './pages/progress/progress.component';
import { DownloadsComponent } from './pages/downloads/downloads.component';
import { SettingsComponent } from './pages/settings/settings.component';
import { NotificationsComponent } from './pages/notifications/notifications.component';
import { SearchPageComponent } from './pages/search/search-page.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', component: LandingComponent },
  { path: 'login', component: LoginComponent, canActivate: [guestGuard] },
  { path: 'signup', component: SignupComponent, canActivate: [guestGuard] },
  { path: 'forgot-password', component: ForgotPasswordComponent, canActivate: [guestGuard] },
  { path: 'reset-password', component: ResetPasswordComponent, canActivate: [guestGuard] },
  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      { path: 'dashboard', component: DashboardComponent },
      { path: 'courses', component: CoursesComponent },
      { path: 'courses/:id', component: CourseDetailComponent },
      { path: 'videos', component: VideosComponent },
      { path: 'chat', component: ChatPageComponent },
      { path: 'quizzes', component: QuizListComponent },
      { path: 'quizzes/:quizId', component: QuizTakeComponent },
      { path: 'progress', component: ProgressComponent },
      { path: 'downloads', component: DownloadsComponent },
      { path: 'settings', component: SettingsComponent },
      { path: 'notifications', component: NotificationsComponent },
      { path: 'search', component: SearchPageComponent },
    ],
  },
  { path: '**', redirectTo: '' },
];
