import { ReactNode } from "react";

interface CategoryTagProps {
  children: ReactNode;
  variant?: "default" | "light" | "dark";
  className?: string;
}

export const CategoryTag = ({
  children,
  variant = "default",
  className = "",
}: CategoryTagProps) => {
  const variantStyles = {
    default: "bg-black/30 backdrop-blur-md text-white border border-white/20",
    light: "bg-purple-100 text-purple-700",
    dark: "bg-zinc-800 text-white",
  };

  return (
    <span
      className={`inline-block px-2 py-1 rounded-md text-xs font-bold ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
};
