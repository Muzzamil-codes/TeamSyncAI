import React, { useState } from 'react';
import { CheckCircle2, Circle, Trash2, Filter } from 'lucide-react';
import { Todo } from '../types';

interface TodoPageProps {
  todos: Todo[];
  onToggleTodo: (id: number) => void;
  onDeleteTodo: (id: number) => void;
}

const TodoPage: React.FC<TodoPageProps> = ({ todos, onToggleTodo, onDeleteTodo }) => {
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [priorityFilter, setPriorityFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  const filteredTodos = todos.filter((todo) => {
    if (filter === 'active' && todo.completed) return false;
    if (filter === 'completed' && !todo.completed) return false;
    if (priorityFilter !== 'all' && todo.priority !== priorityFilter) return false;
    return true;
  });

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-500/10 text-red-400 border-red-500/30';
      case 'medium':
        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30';
      case 'low':
        return 'bg-green-500/10 text-green-400 border-green-500/30';
      default:
        return 'bg-gray-500/10 text-gray-400 border-gray-500/30';
    }
  };

  const getDueDateColor = (dueDate: string) => {
    const today = new Date();
    const due = new Date(dueDate);
    const daysLeft = Math.ceil((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

    if (daysLeft < 0) return 'text-red-400';
    if (daysLeft <= 1) return 'text-orange-400';
    if (daysLeft <= 7) return 'text-yellow-400';
    return 'text-gray-400';
  };

  const stats = {
    total: todos.length,
    completed: todos.filter(t => t.completed).length,
    active: todos.filter(t => !t.completed).length,
  };

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-black-custom-800 border border-gray-700 rounded-lg p-4">
          <p className="text-gray-400 text-sm mb-1">Total Tasks</p>
          <p className="text-3xl font-bold text-white">{stats.total}</p>
        </div>
        <div className="bg-black-custom-800 border border-gray-700 rounded-lg p-4">
          <p className="text-gray-400 text-sm mb-1">Active</p>
          <p className="text-3xl font-bold text-yellow-400">{stats.active}</p>
        </div>
        <div className="bg-black-custom-800 border border-gray-700 rounded-lg p-4">
          <p className="text-gray-400 text-sm mb-1">Completed</p>
          <p className="text-3xl font-bold text-green-400">{stats.completed}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        <div className="flex items-center gap-2">
          <Filter size={18} className="text-gray-400" />
          <span className="text-gray-400 font-medium">Filter:</span>
        </div>
        
        <div className="flex flex-wrap gap-2">
          {(['all', 'active', 'completed'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
                filter === f
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap gap-2">
          {(['all', 'high', 'medium', 'low'] as const).map((p) => (
            <button
              key={p}
              onClick={() => setPriorityFilter(p)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
                priorityFilter === p
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Todos List */}
      <div className="space-y-2">
        {filteredTodos.length > 0 ? (
          filteredTodos.map((todo) => (
            <div
              key={todo.id}
              className={`bg-black-custom-800 border border-gray-700 rounded-lg p-4 flex items-start gap-4 hover:border-gray-600 transition-all ${
                todo.completed ? 'opacity-60' : ''
              }`}
            >
              <button
                onClick={() => onToggleTodo(todo.id)}
                className="mt-1 flex-shrink-0 transition-all hover:scale-110"
              >
                {todo.completed ? (
                  <CheckCircle2 size={24} className="text-green-500" />
                ) : (
                  <Circle size={24} className="text-gray-500 hover:text-gray-400" />
                )}
              </button>

              <div className="flex-1 min-w-0">
                <h3
                  className={`font-semibold mb-1 ${
                    todo.completed
                      ? 'text-gray-400 line-through'
                      : 'text-white'
                  }`}
                >
                  {todo.title}
                </h3>
                {todo.description && (
                  <p className="text-sm text-gray-500 mb-2">{todo.description}</p>
                )}
                <div className="flex flex-wrap gap-2 items-center">
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium border ${getPriorityColor(
                      todo.priority
                    )}`}
                  >
                    {todo.priority.charAt(0).toUpperCase() + todo.priority.slice(1)}
                  </span>
                  <span className={`text-xs font-medium ${getDueDateColor(todo.dueDate)}`}>
                    Due: {new Date(todo.dueDate).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <button
                onClick={() => onDeleteTodo(todo.id)}
                className="flex-shrink-0 p-2 text-gray-500 hover:text-red-400 transition-colors"
              >
                <Trash2 size={18} />
              </button>
            </div>
          ))
        ) : (
          <div className="text-center py-12 bg-black-custom-800 border border-gray-700 rounded-lg">
            <p className="text-gray-400 mb-2">No tasks to display</p>
            <p className="text-sm text-gray-500">Upload files to generate tasks with AI</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TodoPage;
