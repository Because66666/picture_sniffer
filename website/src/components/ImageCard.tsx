import { Sparkles } from "lucide-react";
import { ImageCardProps } from "@/types/gallery";
import { CategoryTag } from "@/components/ui/CategoryTag";
import { useRef, useEffect, useState } from "react";

export const ImageCard = ({ item, onClick, onImageLoaded }: ImageCardProps) => {
  const imgRef = useRef<HTMLImageElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [hasError, setHasError] = useState(false);
  const loadedRef = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.disconnect();
          }
        });
      },
      { threshold: 0.1, rootMargin: '100px' }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  const handleLoad = () => {
    if (!loadedRef.current) {
      loadedRef.current = true;
      setIsLoaded(true);
      onImageLoaded?.(item.id);
    }
  };

  const handleError = () => {
    if (!loadedRef.current) {
      loadedRef.current = true;
      setHasError(true);
      setIsLoaded(true);
      onImageLoaded?.(item.id);
    }
  };

  return (
    <div
      className="group relative overflow-hidden bg-gray-100 cursor-pointer"
      onClick={() => onClick(item)}
    >
      {isInView && !hasError ? (
        <img
          ref={imgRef}
          src={item.src}
          alt={item.description}
          className={`w-full h-auto object-cover transition-transform duration-500 group-hover:scale-110 ${
            isLoaded ? 'opacity-100' : 'opacity-0'
          }`}
          onLoad={handleLoad}
          onError={handleError}
        />
      ) : (
        <div
          ref={imgRef}
          className="w-full aspect-[4/3] bg-gradient-to-br from-gray-200 to-gray-300 animate-pulse"
        />
      )}

      {!isLoaded && isInView && !hasError && (
        <div className="absolute inset-0 bg-gradient-to-br from-gray-200 to-gray-300 animate-pulse" />
      )}

      {hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-200">
          <span className="text-gray-500 text-sm">加载失败</span>
        </div>
      )}

      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100 flex flex-col justify-end p-4">
        <p className="text-white text-sm mb-3 line-clamp-3 font-medium">
          {item.description}
        </p>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onClick(item);
          }}
          className="w-full flex items-center justify-center gap-2 bg-white/20 hover:bg-white/30 backdrop-blur-md text-white py-2 rounded-lg border border-white/30 transition-colors text-sm font-semibold"
        >
          <Sparkles size={16} />
          详情
        </button>
      </div>
    </div>
  );
};
