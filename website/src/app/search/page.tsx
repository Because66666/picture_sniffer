"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { GalleryItem } from "@/types/gallery";
import { Header } from "@/components/Header";
import { GalleryGrid } from "@/components/GalleryGrid";
import { ImageModal } from "@/components/ImageModal";
import { searchImages } from "@/lib/api-service";
import { ArrowLeft } from "lucide-react";
import { useLoading } from "@/contexts/LoadingContext";
import { Suspense } from "react";

const PAGE_SIZE = 10;

function SearchContent() {
  const searchParams = useSearchParams();
  const query = searchParams.get("q") || "";
  const { showLoading, hideLoading, showLoadingWithProgress, updateProgress } = useLoading();
  const [selectedItem, setSelectedItem] = useState<GalleryItem | null>(null);
  const [items, setItems] = useState<GalleryItem[]>([]);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const observerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (query) {
      loadImages();
    }
  }, [query]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loadingMore) {
          loadMoreImages();
        }
      },
      { threshold: 0.1 }
    );

    if (observerRef.current) {
      observer.observe(observerRef.current);
    }

    return () => {
      if (observerRef.current) {
        observer.unobserve(observerRef.current);
      }
    };
  }, [hasMore, loadingMore]);

  const loadImages = async () => {
    try {
      showLoadingWithProgress("搜索中...");
      setError(null);
      
      updateProgress(20);
      const data = await searchImages(query, 0, PAGE_SIZE);
      
      updateProgress(80);
      setItems(data);
      setOffset(PAGE_SIZE);
      setHasMore(data.length >= PAGE_SIZE);
      
      updateProgress(100);
    } catch (err) {
      setError('搜索失败，请稍后重试');
      console.error('Failed to search images:', err);
    } finally {
      setTimeout(() => hideLoading(), 300);
    }
  };

  const loadMoreImages = async () => {
    try {
      setLoadingMore(true);
      const data = await searchImages(query, offset, PAGE_SIZE);
      
      setItems((prev) => {
        const existingIds = new Set(prev.map(item => item.id));
        const newItems = data.filter(item => !existingIds.has(item.id));
        return [...prev, ...newItems];
      });
      
      setOffset((prev) => prev + PAGE_SIZE);
      setHasMore(data.length >= PAGE_SIZE);
    } catch (err) {
      console.error('Failed to load more images:', err);
    } finally {
      setLoadingMore(false);
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">搜索失败</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={loadImages}
            className="bg-black text-white px-6 py-3 rounded-xl font-semibold hover:bg-gray-800 transition"
          >
            重新搜索
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <Header />
      <div className="max-w-4xl mx-auto mb-6">
        <div className="flex items-center gap-3">
          <button
            onClick={() => window.location.href = '/'}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft size={20} />
          </button>
          <h2 className="text-xl font-semibold text-gray-800">
            搜索结果: <span className="text-gray-600">&quot;{query}&quot;</span>
          </h2>
        </div>
      </div>
      {items.length === 0 ? (
        <div className="text-center py-16">
          <img src="/search.png" alt="搜索" className="w-24 h-24 mx-auto mb-4 opacity-60" />
          <p className="text-gray-600 text-lg">没有找到相关图片</p>
        </div>
      ) : (
        <>
          <GalleryGrid
            items={items}
            onItemClick={(item) => setSelectedItem(item)}
          />
          {loadingMore && (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            </div>
          )}
          {!hasMore && items.length > 0 && (
            <div className="text-center py-8 text-gray-500">
              没有更多图片了
            </div>
          )}
          <div ref={observerRef} className="h-1" />
        </>
      )}
      <ImageModal
        selectedItem={selectedItem}
        onClose={() => setSelectedItem(null)}
        onDescriptionUpdate={(itemId, description) => {
          // 更新本地状态中的图片描述
          setItems(prevItems => prevItems.map(item => 
            item.id === itemId ? { ...item, description } : item
          ));
          // 更新当前选中项的描述
          if (selectedItem && selectedItem.id === itemId) {
            setSelectedItem(prev => prev ? { ...prev, description } : null);
          }
        }}
      />
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    }>
      <SearchContent />
    </Suspense>
  );
}
