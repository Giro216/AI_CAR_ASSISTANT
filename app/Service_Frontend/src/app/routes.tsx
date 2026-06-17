import { createBrowserRouter } from 'react-router';
import { MainLayout } from './layouts/MainLayout';
import { HomePage } from './pages/HomePage';
import { CatalogPage } from './pages/CatalogPage';
import { CarDetailsPage } from './pages/CarDetailsPage';
import { CarConfiguratorPage } from './pages/CarConfiguratorPage';
import { AIChatPage } from './pages/AIChatPage';
import { RegisterPage } from './pages/RegisterPage';
import { ProfileSetupPage } from './pages/ProfileSetupPage';
import { ProfilePage } from './pages/ProfilePage';

export const router = createBrowserRouter([
  {
    path: '/',
    Component: MainLayout,
    children: [
      { index: true, Component: HomePage },
      { path: 'catalog', Component: CatalogPage },
      { path: 'catalog/:id', Component: CarDetailsPage },
      { path: 'catalog/:id/:generation/:bodyType', Component: CarConfiguratorPage },
      { path: 'chat', Component: AIChatPage },
      { path: 'chat/:chatId', Component: AIChatPage },
      { path: 'register', Component: RegisterPage },
      { path: 'profile-setup', Component: ProfileSetupPage },
      { path: 'profile', Component: ProfilePage },
    ],
  },
]);
