import { useState } from 'react';
import { Header } from '@/app/components/Header';
import { AIChatSection } from '@/app/components/AIChatSection';
import { PopularCars } from '@/app/components/PopularCars';
import { CatalogSection } from '@/app/components/CatalogSection';
import { AIChatDialog } from '@/app/components/AIChatDialog';
import { ProfileDialog } from '@/app/components/ProfileDialog';
import { Footer } from '@/app/components/Footer';

export default function App() {
  const [isChatDialogOpen, setIsChatDialogOpen] = useState(false);
  const [isProfileDialogOpen, setIsProfileDialogOpen] = useState(false);
  const [showCatalog, setShowCatalog] = useState(false);
  const [favoriteCarIds, setFavoriteCarIds] = useState<number[]>([1, 3]); // Предустановленные избранные

  const handleToggleFavorite = (carId: number) => {
    setFavoriteCarIds(prev =>
      prev.includes(carId) ? prev.filter(id => id !== carId) : [...prev, carId]
    );
  };

  const handleRemoveFavorite = (carId: number) => {
    setFavoriteCarIds(prev => prev.filter(id => id !== carId));
  };

  const handleCatalogClick = () => {
    setShowCatalog(true);
  };

  const handleProfileClick = () => {
    setIsProfileDialogOpen(true);
  };

  const handleOpenChatDialog = () => {
    setIsChatDialogOpen(true);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onCatalogClick={handleCatalogClick} onProfileClick={handleProfileClick} />
      <main>
        <AIChatSection onOpenDialog={handleOpenChatDialog} />

        {showCatalog ? (
          <CatalogSection
            onToggleFavorite={handleToggleFavorite}
            favoriteIds={favoriteCarIds}
          />
        ) : (
          <PopularCars
            onCatalogClick={handleCatalogClick}
            onToggleFavorite={handleToggleFavorite}
            favoriteIds={favoriteCarIds}
          />
        )}
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
