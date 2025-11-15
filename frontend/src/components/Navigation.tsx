import React from 'react';
import { FileUp, CheckSquare, Calendar, MessageCircle } from 'lucide-react';

interface NavProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const Navigation: React.FC<NavProps> = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'upload', label: 'Upload', icon: FileUp },
    { id: 'todos', label: 'Tasks', icon: CheckSquare },
    { id: 'calendar', label: 'Events', icon: Calendar },
    { id: 'chat', label: 'Chat', icon: MessageCircle }
  ];

  return (
    <nav className="bg-black-custom-800 border-b border-gray-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">TS</span>
            </div>
            <h1 className="text-xl font-bold text-white">TeamSync</h1>
          </div>

          <div className="flex items-center gap-1 bg-black-custom-900 rounded-lg p-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => onTabChange(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'bg-blue-500 text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  <Icon size={18} />
                  <span className="text-sm font-medium">{tab.label}</span>
                </button>
              );
            })}
          </div>

          <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center">
            <span className="text-gray-200 text-sm font-semibold">U</span>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
