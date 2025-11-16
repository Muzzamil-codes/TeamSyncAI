import React from 'react';
import { Zap, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Header: React.FC = () => {
  const navigate = useNavigate();

  const handleSignOut = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <header className="bg-black border-b border-gray-800 py-8 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-4xl font-bold text-white mb-2">TeamSync AI</h2>
            <p className="text-gray-400">WhatsApp Chat Analysis & Productivity Assistant</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 bg-white/10 border border-white/20 rounded-lg px-4 py-2">
              <Zap size={20} className="text-white" />
              <span className="text-sm text-white font-medium">AI Powered</span>
            </div>
            <button
              onClick={handleSignOut}
              className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white rounded-lg px-4 py-2 transition-colors"
              title="Sign out"
            >
              <LogOut size={18} />
              <span className="text-sm font-medium">Sign Out</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
