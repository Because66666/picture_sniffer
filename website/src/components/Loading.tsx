"use client";

import React from "react";

interface LoadingProps {
  progress?: number;
  message?: string;
}

export const Loading = ({ progress, message = "加载中..." }: LoadingProps) => {
  return (
    <div className="fixed inset-0 bg-white bg-opacity-90 flex flex-col items-center justify-center z-[100]">
      <img
        src="/loading_loop.webp"
        alt="Loading"
        className="max-w-32 max-h-32 mb-8 animate-pulse"
      />
      {progress !== undefined ? (
        <div className="w-64">
          <div className="flex justify-between mb-2">
            <span className="text-sm text-gray-600">{message}</span>
            <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gray-900 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      ) : (
        <p className="text-gray-600 text-lg">{message}</p>
      )}
    </div>
  );
};
