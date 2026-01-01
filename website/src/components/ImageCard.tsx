import { Sparkles } from "lucide-react";
import { ImageCardProps } from "@/types/gallery";
import { CategoryTag } from "@/components/ui/CategoryTag";

export const ImageCard = ({ item, onClick }: ImageCardProps) => {
  return (
    <div
      className="group relative mb-0 break-inside-avoid overflow-hidden bg-gray-100 cursor-pointer"
      onClick={() => onClick(item)}
    >
      <img
        src={item.src}
        alt={item.description}
        className="w-full h-auto object-cover transition-transform duration-500 group-hover:scale-110"
        loading="lazy"
      />

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
