import React from 'react';
import { Calendar, Clock } from 'lucide-react';
import { CalendarEvent } from '../types';

interface CalendarPageProps {
  events: CalendarEvent[];
}

const CalendarPage: React.FC<CalendarPageProps> = ({ events }) => {
  const sortedEvents = [...events]
    .filter(e => e.date !== 'TBD')
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  const tbdEvents = events.filter(e => e.date === 'TBD');

  const groupedEvents = sortedEvents.reduce((acc, event) => {
    const date = event.date;
    if (!acc[date]) acc[date] = [];
    acc[date].push(event);
    return acc;
  }, {} as Record<string, CalendarEvent[]>);

  return (
    <div className="space-y-6">
      {Object.keys(groupedEvents).length > 0 || tbdEvents.length > 0 ? (
        <>
          {/* Scheduled Events */}
          {Object.entries(groupedEvents).map(([date, dateEvents]) => (
            <div key={date}>
              <div className="flex items-center gap-3 mb-3">
                <Calendar size={20} className="text-white" />
                <h3 className="text-lg font-semibold text-white">
                  {new Date(date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </h3>
              </div>
              <div className="space-y-3">
                {dateEvents.map((event) => (
                  <div key={event.id} className="bg-gray-950 border border-gray-800 rounded-lg p-4 hover:border-gray-700 transition-all">
                    <h4 className="font-semibold text-white mb-2">{event.title}</h4>
                    {event.description && (
                      <p className="text-sm text-gray-400 mb-2">{event.description}</p>
                    )}
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Clock size={16} />
                      {event.time}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* TBD Events */}
          {tbdEvents.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-white mb-3">To Be Scheduled</h3>
              <div className="space-y-3">
                {tbdEvents.map((event) => (
                  <div key={event.id} className="bg-gray-950 border border-gray-800 rounded-lg p-4 hover:border-gray-700 transition-all">
                    <h4 className="font-semibold text-white mb-2">{event.title}</h4>
                    {event.description && (
                      <p className="text-sm text-gray-400">{event.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12 bg-gray-950 border border-gray-800 rounded-lg">
          <Calendar size={48} className="mx-auto mb-4 text-gray-600" />
          <p className="text-gray-400 mb-2">No calendar events</p>
          <p className="text-sm text-gray-500">Upload a chat file to extract events</p>
        </div>
      )}
    </div>
  );
};

export default CalendarPage;
