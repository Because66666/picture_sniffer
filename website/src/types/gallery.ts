export type GalleryItem = {
  id: string;
  src: string;
  category: string;
  description: string;
  aspectRatio?: "square" | "portrait" | "landscape" | "tall";
};

export type ImageCardProps = {
  item: GalleryItem;
  onClick: (item: GalleryItem) => void;
  onImageLoaded?: (id: string) => void;
};

export type ImageModalProps = {
  selectedItem: GalleryItem | null;
  onClose: () => void;
  onDescriptionUpdate?: (itemId: string, description: string) => void;
  onDelete?: (itemId: string) => void;
};

export type ApiImageData = {
  category: string;
  create_time: string;
  description: string;
  image_id: string;
  image_path: string;
  img_webp: string;
};

export type ApiResponse = {
  data: ApiImageData[];
  success: boolean;
};
