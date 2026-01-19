import { GalleryItem } from "@/types/gallery";
import { ImageCard } from "./ImageCard";
import { useState, useEffect } from "react";

interface GalleryGridProps {
  items: GalleryItem[];
  onItemClick: (item: GalleryItem) => void;
  onImageLoaded?: (id: string) => void;
  currentClass?: boolean;
}

export const GalleryGrid = ({ items, onItemClick, onImageLoaded, currentClass = true }: GalleryGridProps) => {
  const [columnCount, setColumnCount] = useState(1);

  useEffect(() => {
    const updateColumnCount = () => {
      if (typeof window !== 'undefined') {
        const width = window.innerWidth;
        if (width >= 1024) {
          setColumnCount(4);
        } else if (width >= 768) {
          setColumnCount(3);
        } else if (width >= 640) {
          setColumnCount(2);
        } else {
          setColumnCount(1);
        }
      }
    };

    updateColumnCount();
    window.addEventListener('resize', updateColumnCount);
    return () => window.removeEventListener('resize', updateColumnCount);
  }, []);

  const columns = Array.from({ length: columnCount }, () => [] as GalleryItem[]);
  
  // 如果 currentClass 为 false，按时间倒序排列
  const displayItems = [...items];
  if (!currentClass) {
    displayItems.sort((a, b) => {
      if (!a.create_time || !b.create_time) return 0;
      return new Date(b.create_time).getTime() - new Date(a.create_time).getTime();
    });
  }

  displayItems.forEach((item, index) => {
    columns[index % columnCount].push(item);
  });

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-0">
      {columns.map((columnItems, colIndex) => (
        <div key={colIndex} className="flex flex-col gap-0">
          {columnItems.map((item) => (
            <ImageCard
              key={item.id}
              item={item}
              onClick={onItemClick}
              onImageLoaded={onImageLoaded}
            />
          ))}
        </div>
      ))}
    </div>
  );
};
