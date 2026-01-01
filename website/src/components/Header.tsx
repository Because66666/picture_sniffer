import { Github } from "lucide-react";

export const Header = () => {
  return (
    <header className="flex flex-col items-center mb-8 px-2">
      <div className="relative w-full max-w-4xl">
        <a
          href="https://github.com/Because66666/picture_sniffer"
          target="_blank"
          rel="noopener noreferrer"
          className="absolute left-0 top-1/2 -translate-y-1/2 flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
        >
          <Github size={20} />
          <span>GitHub</span>
        </a>
        <h1 className="text-2xl font-bold text-gray-800 text-center">探索灵感</h1>
      </div>
      <p className="text-lg text-gray-600 mt-2">我的世界建筑风格展廊</p>
    </header>
  );
};
