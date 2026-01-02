"use client";

import React from "react";
import { useLoading } from "@/contexts/LoadingContext";
import { Loading } from "@/components/Loading";

export function LoadingWrapper({ children }: { children: React.ReactNode }) {
  const { isLoading, progress, message } = useLoading();

  return (
    <>
      {children}
      {isLoading && <Loading progress={progress} message={message} />}
    </>
  );
}
