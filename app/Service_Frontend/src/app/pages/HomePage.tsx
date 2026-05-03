import { useOutletContext } from 'react-router';
import { AIChatSection } from '@/app/components/AIChatSection';
import { PopularCars } from '@/app/components/PopularCars';

interface OutletContext {
  favoriteCarIds: string[];
  handleToggleFavorite: (id: string) => void;
  setIsChatDialogOpen: (open: boolean) => void;
}

export function HomePage() {
  const { favoriteCarIds, handleToggleFavorite, setIsChatDialogOpen } = useOutletContext<OutletContext>();

  return (
    <>
      <AIChatSection onOpenDialog={() => setIsChatDialogOpen(true)} />
      <PopularCars
        onToggleFavorite={handleToggleFavorite}
        favoriteIds={favoriteCarIds}
      />
    </>
  );
}
