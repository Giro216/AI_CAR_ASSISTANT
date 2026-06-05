import { useState, useCallback } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router';
import { Header } from '@/app/components/Header';
import { Footer } from '@/app/components/Footer';
import { LoginPopup } from '@/app/components/LoginPopup';
import { useAuth } from '@/app/contexts/AuthContext';

export function MainLayout() {
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const { isAuthenticated, favoriteCarIds, toggleFavorite } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleProfileClick = useCallback(() => {
    if (isAuthenticated) {
      navigate('/profile');
    } else {
      setIsLoginOpen(true);
    }
  }, [isAuthenticated, navigate]);

  const handleToggleFavorite = useCallback((carId: string) => {
    if (!isAuthenticated) {
      setIsLoginOpen(true);
      return;
    }
    toggleFavorite(carId);
  }, [isAuthenticated, toggleFavorite]);

  const isChatPage = location.pathname.startsWith('/chat');

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        onProfileClick={handleProfileClick}
        isAuthenticated={isAuthenticated}
      />
      <main>
        <Outlet context={{ favoriteCarIds, handleToggleFavorite }} />
      </main>
      {!isChatPage && <Footer />}

      <LoginPopup
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
      />
    </div>
  );
}
