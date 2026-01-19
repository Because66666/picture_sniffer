import { motion, AnimatePresence } from "framer-motion";
import { X, Sparkles, Download } from "lucide-react";
import { ImageModalProps } from "@/types/gallery";
import { Button } from "@/components/ui/Button";
import { CategoryTag } from "@/components/ui/CategoryTag";
import { describeImage, deleteImage } from "@/lib/api-service";
import { useState, useEffect, useCallback } from "react";

export const ImageModal = ({ selectedItem, onClose, onDescriptionUpdate, onDelete }: ImageModalProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const [enhancedDescription, setEnhancedDescription] = useState<string>("");
  const [displayedDescription, setDisplayedDescription] = useState<string>("");
  const [showEnhanced, setShowEnhanced] = useState(false);

  const handleDownload = async () => {
    try {
      if (!selectedItem) return;
      const response = await fetch(selectedItem.src);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `minecraft-${selectedItem.id}.jpg`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('下载失败:', error);
    }
  };

  // 当切换图片时重置所有状态
  useEffect(() => {
    setIsLoading(false);
    setEnhancedDescription("");
    setDisplayedDescription("");
    setShowEnhanced(false);
  }, [selectedItem?.id]);

  // 逐字渲染文本的效果
  useEffect(() => {
    if (enhancedDescription && showEnhanced) {
      let index = 0;
      setDisplayedDescription("");
      const textToDisplay = enhancedDescription;
      
      const interval = setInterval(() => {
        if (index < textToDisplay.length) {
          const char = textToDisplay[index];
          if (char) { // 确保只添加有效的字符
            setDisplayedDescription(prev => prev + char);
          }
          index++;
        } else {
          clearInterval(interval);
        }
      }, 30); // 每30ms渲染一个字符

      return () => clearInterval(interval);
    }
  }, [enhancedDescription, showEnhanced]);

  // 处理细化描述按钮点击
  const handleEnhanceDescription = async () => {
    if (!selectedItem || isLoading) return;
    
    setIsLoading(true);
    setShowEnhanced(false);
    
    try {
      const newDescription = await describeImage(selectedItem.id);
      setEnhancedDescription(newDescription);
      setShowEnhanced(true);
      
      // 通知父组件更新描述
      if (onDescriptionUpdate) {
        onDescriptionUpdate(selectedItem.id, newDescription);
      }
    } catch (error) {
      console.error('获取细化描述失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedItem || isLoading) return;

    if (window.confirm("确认删除图片？")) {
      setIsLoading(true);
      try {
        await deleteImage(selectedItem.id);
        onDelete?.(selectedItem.id);
        onClose();
      } catch (error) {
        console.error('删除图片失败:', error);
        alert('删除失败');
      } finally {
        setIsLoading(false);
      }
    }
  };


  return (
    <AnimatePresence>
      {selectedItem && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          onClick={onClose}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4 md:p-10 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
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
                
                <AnimatePresence mode="wait">
                  {isLoading ? (
                    <motion.div
                      key="loading"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex items-center justify-center py-4"
                    >
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                        className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full mr-2"
                      />
                      <span className="text-gray-600 text-sm">生成细化描述中...</span>
                    </motion.div>
                  ) : showEnhanced ? (
                    <motion.div
                      key="enhanced"
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <h3 className="text-sm font-semibold text-primary mb-2">细化描述：</h3>
                      <p className="text-gray-600 text-sm leading-relaxed whitespace-pre-line">
                        {displayedDescription}
                      </p>
                    </motion.div>
                  ) : (
                    <motion.p
                      key="original"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="text-gray-600 text-sm leading-relaxed"
                    >
                      {selectedItem.description}
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>

              <div className="mt-6 space-y-3">
                <Button 
                  variant="primary" 
                  icon={<Sparkles size={18} />} 
                  className="w-full"
                  onClick={handleEnhanceDescription}
                  disabled={isLoading}
                >
                  {isLoading ? "生成中..." : "细化描述"}
                </Button>
                <div className="flex gap-2">
                  <Button variant="secondary" icon={<Download size={18} />} className="flex-1" onClick={handleDownload}>
                    下载图片
                  </Button>
                  <Button
                    variant="destructive"
                    className="w-12 px-0"
                    onClick={handleDelete}
                    disabled={isLoading}
                    title="删除图片"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M7 21q-.825 0-1.412-.587T5 19V6H4V4h5V3h6v1h5v2h-1v13q0 .825-.587 1.413T17 21zM17 6H7v13h10zM9 17h2V8H9zm4 0h2V8h-2zM7 6v13z" />
                    </svg>
                  </Button>
                </div>
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
