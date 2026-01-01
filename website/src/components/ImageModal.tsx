import { motion, AnimatePresence } from "framer-motion";
import { X, Sparkles, Download } from "lucide-react";
import { ImageModalProps } from "@/types/gallery";
import { Button } from "@/components/ui/Button";
import { CategoryTag } from "@/components/ui/CategoryTag";

export const ImageModal = ({ selectedItem, onClose }: ImageModalProps) => {
  if (!selectedItem) return null;

  return (
    <AnimatePresence>
      {selectedItem && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4 md:p-10 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
            className="relative max-w-7xl max-h-[95vh] flex flex-col md:flex-row bg-zinc-900 rounded-2xl overflow-hidden shadow-2xl"
          >
            <div className="flex-1 relative bg-black flex items-center justify-center">
              <img
                src={selectedItem.src}
                alt={selectedItem.description}
                className="max-w-full max-h-[95vh] object-contain"
              />
            </div>

            <div className="w-full md:w-80 bg-white p-6 flex flex-col justify-between shrink-0">
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <CategoryTag variant="light">{selectedItem.category}</CategoryTag>
                </div>
                <h2 className="text-xl font-bold text-gray-800 mb-2">图片详情</h2>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {selectedItem.description}
                </p>
              </div>

              <div className="mt-6 space-y-3">
                <Button variant="primary" icon={<Sparkles size={18} />} className="w-full">
                  继续创作
                </Button>
                <Button variant="secondary" icon={<Download size={18} />} className="w-full">
                  下载图片
                </Button>
              </div>
            </div>

            <button
              onClick={onClose}
              className="absolute top-4 right-4 md:left-4 md:right-auto bg-black/50 text-white p-2 rounded-full hover:bg-black/70 transition"
            >
              <X size={24} />
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
