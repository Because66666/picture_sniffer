"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { GalleryItem } from "@/types/gallery";
import { Header } from "@/components/Header";
import { GalleryGrid } from "@/components/GalleryGrid";
import { ImageModal } from "@/components/ImageModal";
import { fetchRandomImages } from "@/lib/api-service";
import { useLoading } from "@/contexts/LoadingContext";

const PAGE_SIZE = 20;

export default function MasonryGallery() {
  const router = useRouter();
  const { showLoading, hideLoading, showLoadingWithProgress, updateProgress } = useLoading();
  const [selectedItem, setSelectedItem] = useState<GalleryItem | null>(null);
  const [items, setItems] = useState<GalleryItem[]>([]);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const observerRef = useRef<HTMLDivElement | null>(null);
  const offsetRef = useRef(0);
  const isLoadingRef = useRef(false);
  const hasMountedRef = useRef(false);
  const loadedImagesRef = useRef<Set<string>>(new Set());
  const initialLoadRef = useRef(false);

  const handleImageLoaded = (id: string) => {
    loadedImagesRef.current.add(id);
    

      // 在3秒内逐步增加到100
      const startTime = Date.now();
      const duration = 3000; // 3秒
      const animateProgress = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min((elapsed / duration) * 100, 100);
        updateProgress(progress);
        if (progress < 100) {
          requestAnimationFrame(animateProgress);
        }
      };
      requestAnimationFrame(animateProgress);
      setTimeout(() => {
        hideLoading();
        isLoadingRef.current = false;
      }, 300);
    }

  const loadImages = async () => {
    if (isLoadingRef.current) return;
    isLoadingRef.current = true;
    loadedImagesRef.current.clear();
    initialLoadRef.current = false;
    
    try {
      showLoadingWithProgress("加载中...");
      setError(null);
      
      updateProgress(20);
      const data = await fetchRandomImages(0, PAGE_SIZE);
      
      updateProgress(60);
      setItems(data);
      offsetRef.current = PAGE_SIZE;
      setHasMore(data.length >= PAGE_SIZE);
      
      initialLoadRef.current = true;
      
      // 如果没有图片，直接隐藏加载动画
      if (data.length === 0) {
        updateProgress(100);
        setTimeout(() => {
          hideLoading();
        }, 300);
        isLoadingRef.current = false;
      }
    } catch (err) {
      setError('加载图片失败，请稍后重试');
      console.error('Failed to load images:', err);
      hideLoading();
      isLoadingRef.current = false;
    }
  };

  const loadMoreImages = async () => {
    if (loadingMore || !hasMore || isLoadingRef.current) return;
    isLoadingRef.current = true;
    
    try {
      // console.log('loadMoreImages called with offset:', offsetRef.current);
      setLoadingMore(true);
      const data = await fetchRandomImages(offsetRef.current, PAGE_SIZE);
      // console.log('Fetched data length:', data.length);
      
      setItems((prev) => {
        const existingIds = new Set(prev.map(item => item.id));
        const newItems = data.filter(item => !existingIds.has(item.id));
        // console.log('New items after filtering:', newItems.length);
        return [...prev, ...newItems];
      });
      
      offsetRef.current += PAGE_SIZE;
      setHasMore(data.length >= PAGE_SIZE);
      // console.log('Updated hasMore:', data.length >= PAGE_SIZE);
    } catch (err) {
      console.error('Failed to load more images:', err);
    } finally {
      setLoadingMore(false);
      isLoadingRef.current = false;
    }
  };

  useEffect(() => {
    if (hasMountedRef.current) return;
    hasMountedRef.current = true;
    
    const token = localStorage.getItem('auth_token');
    if (!token) {
      router.push('/login');
      return;
    }
    setIsAuthenticated(true);
    loadImages();
  }, [router]);

  useEffect(() => {
    if (!isAuthenticated) return;
    
    const observer = new IntersectionObserver(
      (entries) => {
        // console.log('IntersectionObserver triggered:', entries[0].isIntersecting, 'hasMore:', hasMore, 'loadingMore:', loadingMore);
        if (entries[0].isIntersecting && hasMore && !loadingMore) {
          // console.log('Loading more images...');
          loadMoreImages();
        }
      },
      { threshold: 0.01, rootMargin: '200px' }
    );

    if (observerRef.current) {
      observer.observe(observerRef.current);
    }

    return () => {
      if (observerRef.current) {
        observer.unobserve(observerRef.current);
      }
    };
  }, [isAuthenticated, hasMore, loadingMore]);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">加载失败</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={loadImages}
            className="bg-black text-white px-6 py-3 rounded-xl font-semibold hover:bg-gray-800 transition"
          >
            重新加载
          </button>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <Header />
      <GalleryGrid
        items={items}
        onItemClick={(item) => setSelectedItem(item)}
        onImageLoaded={handleImageLoaded}
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
      <div ref={observerRef} className="h-20" />
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
        onDelete={(itemId) => {
          setItems(prevItems => prevItems.filter(item => item.id !== itemId));
        }}
      />
    </div>
  );
}
