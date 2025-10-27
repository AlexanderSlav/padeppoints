import LoginPage from '../pages/LoginPage';
import CallbackPage from '../pages/CallbackPage';
import DashboardPage from '../pages/DashboardPage';
import CreateTournamentPage from '../pages/CreateTournamentPage';
import RegisterPage from '../pages/RegisterPage';
import TournamentDiscoveryPage from '../pages/TournamentDiscoveryPage';
import TournamentDetailPage from '../pages/TournamentDetailPage';
import UserProfilePage from '../pages/UserProfilePage';

export const routes = {
  // Public routes (redirect to dashboard if authenticated)
  public: [
    {
      path: '/login',
      component: LoginPage,
      title: 'Login'
    },
    {
      path: '/register',
      component: RegisterPage,
      title: 'Register'
    }
  ],

  // OAuth callback route (no protection needed)
  callback: [
    {
      path: '/callback',
      component: CallbackPage,
      title: 'OAuth Callback'
    }
  ],

  // Protected routes (require authentication)
  protected: [
    {
      path: '/dashboard',
      component: DashboardPage,
      title: 'Dashboard'
    },
    {
      path: '/create-tournament',
      component: CreateTournamentPage,
      title: 'Create Tournament'
    },
    {
      path: '/tournaments',
      component: TournamentDiscoveryPage,
      title: 'Tournaments'
    },
    {
      path: '/tournaments/:id',
      component: TournamentDetailPage,
      title: 'Tournament Details'
    },
    {
      path: '/users/:userId/profile',
      component: UserProfilePage,
      title: 'User Profile'
    }
  ],

  // Default redirects
  redirects: [
    {
      from: '/',
      to: '/dashboard'
    }
  ]
};