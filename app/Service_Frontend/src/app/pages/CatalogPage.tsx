import { useOutletContext } from 'react-router';
import { CatalogSection } from '@/app/components/CatalogSection';

interface OutletContext {
  favoriteCarIds: string[];
  handleToggleFavorite: (id: string) => void;
}

export function CatalogPage() {
  const { favoriteCarIds, handleToggleFavorite } = useOutletContext<OutletContext>();

  return (
    <CatalogSection
      onToggleFavorite={handleToggleFavorite}
      favoriteIds={favoriteCarIds}
    />
  );
}
