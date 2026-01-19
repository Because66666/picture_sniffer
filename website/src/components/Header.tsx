"use client";

import { Github, Search, X } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";

export const Header = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [isExpanded, setIsExpanded] = useState(false);
  const [isMoving, setIsMoving] = useState(false);
  const router = useRouter();
  const searchRef = useRef<HTMLDivElement>(null);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      setIsExpanded(false);
      setSearchQuery("");
    }
  };

  const handleExpand = () => {
    setIsExpanded(true);
  };

  const handleClose = () => {
    setIsExpanded(false);
    setSearchQuery("");
  };

  const handleClickOutside = (event: MouseEvent) => {
    if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
      handleClose();
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <>
      <header className="flex flex-col items-center mb-8 px-2 pt-4 md:pt-0">
        <div className="relative w-full max-w-4xl flex flex-col md:block items-center">
          <a
            href="https://github.com/Because66666/picture_sniffer"
            target="_blank"
            rel="noopener noreferrer"
            className="order-2 mt-4 md:mt-0 md:order-none md:absolute md:left-0 md:top-1/2 md:-translate-y-1/2 flex flex-col items-center md:items-start gap-1 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Github size={20} />
              <span>GitHub</span>
            </div>
            <span className="text-xs text-gray-400">作者：Because66666</span>
          </a>
          <div className="flex items-center justify-center gap-3 md:w-full">
            <img src="/logo.png" alt="Logo" className="h-8 w-8 object-contain" />
            <h1 className="text-2xl font-bold text-gray-800">探索灵感</h1>
          </div>
        </div>
        <p className="text-lg text-gray-600 mt-2 text-center">我的世界建筑风格展廊</p>
      </header>

      <div ref={searchRef} className="fixed right-4 top-4 md:right-6 md:top-6 z-50">
        <div
          className={`transition-all duration-200 ease-in-out ${isExpanded
              ? "w-[calc(100vw-32px)] md:w-[280px]"
              : "w-10 h-10 md:w-12 md:h-12 bg-white rounded-full shadow-lg flex items-center justify-center cursor-pointer hover:shadow-xl hover:scale-105"
          }`}
        >
          {isExpanded ? (
            <form onSubmit={handleSearch} className="relative w-full">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜索图片..."
                className="w-full px-5 py-3 pl-12 pr-12 text-gray-700 bg-white border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-shadow shadow-sm"
                autoFocus
              />
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              <button
                type="button"
                onClick={handleClose}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X size={20} />
              </button>
            </form>
          ) : (
            <Search
              size={24}
              className="text-gray-600"
              onClick={handleExpand}
            />
          )}
        </div>
      </div>
    </>
  );
};
