"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

interface LoadingContextType {
  isLoading: boolean;
  progress: number | undefined;
  message: string;
  showLoading: (message?: string) => void;
  showLoadingWithProgress: (message: string) => void;
  updateProgress: (progress: number) => void;
  hideLoading: () => void;
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

export const LoadingProvider = ({ children }: { children: ReactNode }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState<number | undefined>(undefined);
  const [message, setMessage] = useState("加载中...");

  const showLoading = (msg = "加载中...") => {
    setMessage(msg);
    setProgress(undefined);
    setIsLoading(true);
  };

  const showLoadingWithProgress = (msg: string) => {
    setMessage(msg);
    setProgress(0);
    setIsLoading(true);
  };

  const updateProgress = (newProgress: number) => {
    setProgress(newProgress);
  };

  const hideLoading = () => {
    setIsLoading(false);
    setProgress(undefined);
  };

  return (
    <LoadingContext.Provider
      value={{
        isLoading,
        progress,
        message,
        showLoading,
        showLoadingWithProgress,
        updateProgress,
        hideLoading,
      }}
    >
      {children}
    </LoadingContext.Provider>
  );
};

export const useLoading = () => {
  const context = useContext(LoadingContext);
  if (context === undefined) {
    throw new Error("useLoading must be used within a LoadingProvider");
  }
  return context;
};
