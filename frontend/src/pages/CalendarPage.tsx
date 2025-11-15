import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Clock } from 'lucide-react';
import { CalendarEvent } from '../types';

interface CalendarPageProps {
  events: CalendarEvent[];
}

const CalendarPage: React.FC<CalendarPageProps> = ({ events }) => {
  const [currentDate, setCurrentDate] = useState(new Date(2025, 10, 15)); // Nov 15, 2025

  const getDaysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const getEventsByDate = (day: number) => {
    const dateStr = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return events.filter(e => e.date === dateStr);
  };

  const previousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  const daysInMonth = getDaysInMonth(currentDate);
  const firstDay = getFirstDayOfMonth(currentDate);
  const monthName = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  const days = Array.from({ length: firstDay }).fill(null);
  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i);
  }

  const upcomingEvents = events
    .filter(e => new Date(e.date) >= new Date())
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .slice(0, 5);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Calendar */}
      <div className="lg:col-span-2 bg-black-custom-800 border border-gray-700 rounded-lg overflow-hidden">
        <div className="bg-black-custom-900 px-6 py-4 border-b border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">{monthName}</h2>
          <div className="flex gap-2">
            <button
              onClick={previousMonth}
              className="p-2 hover:bg-gray-700 rounded transition-colors"
            >
              <ChevronLeft size={20} className="text-gray-400" />
            </button>
            <button
              onClick={nextMonth}
              className="p-2 hover:bg-gray-700 rounded transition-colors"
            >
              <ChevronRight size={20} className="text-gray-400" />
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Day headers */}
          <div className="grid grid-cols-7 gap-2 mb-4">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="text-center text-gray-500 font-semibold text-sm py-2">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar grid */}
          <div className="grid grid-cols-7 gap-2">
            {days.map((day, idx) => {
              const typedDay = day as number | null;
              const dayEvents = typedDay ? getEventsByDate(typedDay) : [];
              const isToday = typedDay === new Date().getDate() && 
                              currentDate.getMonth() === new Date().getMonth() &&
                              currentDate.getFullYear() === new Date().getFullYear();

              return (
                <div
                  key={idx}
                  className={`aspect-square p-2 rounded border transition-all ${
                    typedDay
                      ? isToday
                        ? 'bg-blue-500/20 border-blue-500'
                        : dayEvents.length > 0
                        ? 'bg-green-500/10 border-green-500/30 hover:border-green-500'
                        : 'bg-black-custom-700 border-gray-700 hover:border-gray-600'
                      : 'bg-black-custom-900 border-gray-800'
                  }`}
                >
                  {typedDay && (
                    <div className="flex flex-col h-full">
                      <span className={`text-sm font-semibold ${
                        isToday ? 'text-blue-400' : 'text-white'
                      }`}>
                        {typedDay}
                      </span>
                      {dayEvents.length > 0 && (
                        <div className="mt-1 flex-1 flex items-end">
                          <div className="flex gap-1 flex-wrap">
                            {dayEvents.slice(0, 2).map((event, i) => (
                              <div
                                key={i}
                                className="w-1.5 h-1.5 bg-green-400 rounded-full"
                                title={event.title}
                              />
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Upcoming Events */}
      <div className="bg-black-custom-800 border border-gray-700 rounded-lg overflow-hidden">
        <div className="bg-black-custom-900 px-6 py-4 border-b border-gray-700">
          <h3 className="font-semibold text-white">Upcoming Events</h3>
        </div>

        <div className="divide-y divide-gray-700">
          {upcomingEvents.length > 0 ? (
            upcomingEvents.map((event) => (
              <div key={event.id} className="px-6 py-4 hover:bg-black-custom-700 transition-colors">
                <h4 className="font-semibold text-white text-sm mb-1">{event.title}</h4>
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <Clock size={14} />
                  <span>{new Date(event.date).toLocaleDateString()} at {event.time}</span>
                </div>
                {event.description && (
                  <p className="text-xs text-gray-500 mt-2">{event.description}</p>
                )}
              </div>
            ))
          ) : (
            <div className="px-6 py-8 text-center">
              <p className="text-gray-500 text-sm">No upcoming events</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CalendarPage;
