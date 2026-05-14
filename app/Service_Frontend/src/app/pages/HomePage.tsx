import { useOutletContext } from 'react-router';
import { AIChatSection } from '@/app/components/AIChatSection';
import { PopularCars } from '@/app/components/PopularCars';

interface OutletContext {
  favoriteCarIds: string[];
  handleToggleFavorite: (id: string) => void;
  setIsChatDialogOpen: (open: boolean) => void;
}

export function HomePage() {
  const { favoriteCarIds, handleToggleFavorite } = useOutletContext<OutletContext>();

  return (
    <>
      <AIChatSection />
      <PopularCars
        onToggleFavorite={handleToggleFavorite}
        favoriteIds={favoriteCarIds}
      />
    </>
  );
}
