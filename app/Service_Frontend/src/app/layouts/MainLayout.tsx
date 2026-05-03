import { useState } from 'react';
import { Outlet } from 'react-router';
import { Header } from '@/app/components/Header';
import { Footer } from '@/app/components/Footer';
import { AIChatDialog } from '@/app/components/AIChatDialog';
import { ProfileDialog } from '@/app/components/ProfileDialog';

export function MainLayout() {
  const [isChatDialogOpen, setIsChatDialogOpen] = useState(false);
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

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onProfileClick={() => setIsProfileDialogOpen(true)} />
      <main>
        <Outlet context={{ favoriteCarIds, handleToggleFavorite, setIsChatDialogOpen }} />
      </main>
      <Footer />

      <AIChatDialog isOpen={isChatDialogOpen} onClose={() => setIsChatDialogOpen(false)} />
      <ProfileDialog
        isOpen={isProfileDialogOpen}
        onClose={() => setIsProfileDialogOpen(false)}
        favoriteCarIds={favoriteCarIds}
        onRemoveFavorite={handleRemoveFavorite}
      />
    </div>
  );
}
