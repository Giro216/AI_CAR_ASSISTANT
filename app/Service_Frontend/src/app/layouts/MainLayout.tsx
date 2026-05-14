import { useState } from 'react';
import { Outlet, useLocation } from 'react-router';
import { Header } from '@/app/components/Header';
import { Footer } from '@/app/components/Footer';
import { ProfileDialog } from '@/app/components/ProfileDialog';

export function MainLayout() {
  const [isProfileDialogOpen, setIsProfileDialogOpen] = useState(false);
  const [favoriteCarIds, setFavoriteCarIds] = useState<string[]>(['1', '3']);

  const handleRemoveFavorite = (carId: string) => {
    setFavoriteCarIds(prev => prev.filter(id => id !== carId));
  };

  const handleToggleFavorite = (carId: string) => {
    setFavoriteCarIds(prev =>
      prev.includes(carId) ? prev.filter(id => id !== carId) : [...prev, carId]
    );
  };

  const isChatPage = location.pathname.startsWith('/chat');

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        onProfileClick={() => setIsProfileDialogOpen(true)}
      />
      <main>
        <Outlet context={{ favoriteCarIds, handleToggleFavorite }} />
      </main>
      {!isChatPage && <Footer />}

      <ProfileDialog
        isOpen={isProfileDialogOpen}
        onClose={() => setIsProfileDialogOpen(false)}
        favoriteCarIds={favoriteCarIds}
        onRemoveFavorite={handleRemoveFavorite}
      />
    </div>
  );
}
