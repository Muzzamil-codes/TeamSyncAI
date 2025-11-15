import React from 'react';
import { Zap } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-black-custom-900 to-black-custom-800 border-b border-gray-700 py-4 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Welcome to TeamSync</h1>
            <p className="text-gray-400">Boost your productivity with AI-powered task management</p>
          </div>
          <div className="flex items-center gap-3 bg-blue-500/10 border border-blue-500/30 rounded-lg px-4 py-2">
            <Zap size={20} className="text-blue-400" />
            <span className="text-sm text-blue-400 font-medium">AI Ready</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
