import React, { useState } from 'react';
import { CheckCircle2, Circle, Trash2 } from 'lucide-react';
import { Todo } from '../types';

interface TodoPageProps {
  todos: Todo[];
  onToggleTodo: (id: number) => void;
  onDeleteTodo: (id: number) => void;
}

const TodoPage: React.FC<TodoPageProps> = ({ todos, onToggleTodo, onDeleteTodo }) => {
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');

  const filteredTodos = todos.filter((todo) => {
    if (filter === 'active' && todo.completed) return false;
    if (filter === 'completed' && !todo.completed) return false;
    return true;
  });

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'bg-red-500/20 text-red-300';
      case 'medium':
        return 'bg-yellow-500/20 text-yellow-300';
      case 'low':
        return 'bg-green-500/20 text-green-300';
      default:
        return 'bg-gray-500/20 text-gray-300';
    }
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
        <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
          <p className="text-gray-500 text-sm mb-2">Total Tasks</p>
          <p className="text-3xl font-bold text-white">{stats.total}</p>
        </div>
        <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
          <p className="text-gray-500 text-sm mb-2">Active</p>
          <p className="text-3xl font-bold text-white">{stats.active}</p>
        </div>
        <div className="bg-gray-950 border border-gray-800 rounded-lg p-4">
          <p className="text-gray-500 text-sm mb-2">Completed</p>
          <p className="text-3xl font-bold text-white">{stats.completed}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {(['all', 'active', 'completed'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filter === f
                ? 'bg-white text-black'
                : 'bg-gray-900 text-gray-300 hover:bg-gray-800'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Todos List */}
      {filteredTodos.length > 0 ? (
        <div className="space-y-3">
          {filteredTodos.map((todo) => (
            <div
              key={todo.id}
              className="bg-gray-950 border border-gray-800 rounded-lg p-4 hover:border-gray-700 transition-all flex items-start gap-4"
            >
              <button
                onClick={() => onToggleTodo(todo.id)}
                className="mt-1 flex-shrink-0 text-gray-400 hover:text-white transition-colors"
              >
                {todo.completed ? (
                  <CheckCircle2 size={24} className="text-white" />
                ) : (
                  <Circle size={24} />
                )}
              </button>

              <div className="flex-1">
                <p className={`font-medium ${todo.completed ? 'line-through text-gray-500' : 'text-white'}`}>
                  {todo.title}
                </p>
                {todo.description && (
                  <p className="text-sm text-gray-400 mt-1">{todo.description}</p>
                )}

                <div className="flex items-center gap-3 mt-3 flex-wrap">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPriorityColor(todo.priority)}`}>
                    {todo.priority}
                  </span>
                  {todo.dueDate && (
                    <span className="text-sm text-gray-500">
                      Due: {new Date(todo.dueDate).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>

              <button
                onClick={() => onDeleteTodo(todo.id)}
                className="flex-shrink-0 text-gray-500 hover:text-red-400 transition-colors"
              >
                <Trash2 size={20} />
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-950 border border-gray-800 rounded-lg">
          <p className="text-gray-400 mb-2">No tasks to display</p>
          <p className="text-sm text-gray-500">Upload files to generate tasks</p>
        </div>
      )}
    </div>
  );
};

export default TodoPage;
