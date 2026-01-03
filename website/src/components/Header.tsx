"use client";

import { Github, Search, X } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";

export const Header = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [isExpanded, setIsExpanded] = useState(false);
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

  const handleClickOutside = (event: MouseEvent) => {
    if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
      setIsExpanded(false);
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
      <header className="flex flex-col items-center mb-8 px-2">
        <div className="relative w-full max-w-4xl">
          <a
            href="https://github.com/Because66666/picture_sniffer"
            target="_blank"
            rel="noopener noreferrer"
            className="absolute left-0 top-1/2 -translate-y-1/2 flex flex-col items-start gap-1 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Github size={20} />
              <span>GitHub</span>
            </div>
            <span className="text-xs text-gray-400">作者：Because66666</span>
          </a>
          <div className="flex items-center justify-center gap-3">
            <img src="/logo.png" alt="Logo" className="h-8 w-8 object-contain" />
            <h1 className="text-2xl font-bold text-gray-800">探索灵感</h1>
          </div>
        </div>
        <p className="text-lg text-gray-600 mt-2">我的世界建筑风格展廊</p>
      </header>

      <div ref={searchRef} className="fixed right-6 top-6 z-50">
        <div
          className={`transition-all duration-300 ease-in-out ${
            isExpanded
              ? "w-full max-w-2xl"
              : "w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center cursor-pointer hover:shadow-xl hover:scale-105"
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
                onClick={() => {
                  setIsExpanded(false);
                  setSearchQuery("");
                }}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X size={20} />
              </button>
            </form>
          ) : (
            <Search
              size={24}
              className="text-gray-600"
              onClick={() => setIsExpanded(true)}
            />
          )}
        </div>
      </div>
    </>
  );
};
