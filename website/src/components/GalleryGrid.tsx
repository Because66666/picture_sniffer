import { GalleryItem } from "@/types/gallery";
import { ImageCard } from "./ImageCard";

interface GalleryGridProps {
  items: GalleryItem[];
  onItemClick: (item: GalleryItem) => void;
}

export const GalleryGrid = ({ items, onItemClick }: GalleryGridProps) => {
  return (
    <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 gap-0 space-y-0">
      {items.map((item) => (
        <ImageCard
          key={item.id}
          item={item}
          onClick={onItemClick}
        />
      ))}
    </div>
  );
};
