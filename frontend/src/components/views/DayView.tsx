import React from 'react';
import { DateTime } from 'luxon';
import { Event } from '@/types/api';
import { useEvents } from '@/hooks/useEvents';
import { isEventInDay, formatEventDateTime } from '@/utils/date';

interface DayViewProps {
  currentDate: DateTime;
  onDateChange: (date: DateTime) => void;
  onNewEvent: (date?: DateTime) => void;
  onEditEvent: (event: Event) => void;
}

const DayView: React.FC<DayViewProps> = ({
  currentDate,
  onDateChange,
  onNewEvent,
  onEditEvent,
}) => {
  const dayStart = currentDate.startOf('day');
  const dayEnd = currentDate.endOf('day');

  const { data: eventsData, isLoading } = useEvents({
    from: dayStart.toUTC().toISO()!,
    to: dayEnd.toUTC().toISO()!,
  });

  const today = DateTime.now();
  const isToday = currentDate.hasSame(today, 'day');

  const getEventsForDay = () => {
    if (!eventsData?.events) return [];
    return eventsData.events.filter(event =>
      isEventInDay(event.start_datetime, event.end_datetime, currentDate)
    );
  };

  const events = getEventsForDay();

  // Separate all-day and timed events
  const allDayEvents = events.filter(event => event.all_day);
  const timedEvents = events.filter(event => !event.all_day);

  const handleCreateEvent = () => {
    onNewEvent(currentDate);
  };

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Day header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {currentDate.toFormat('EEEE, MMMM d, yyyy')}
            </h2>
            {isToday && (
              <span className="text-sm text-blue-600 font-medium">Today</span>
            )}
          </div>
          <button
            onClick={handleCreateEvent}
            className="btn-primary text-sm px-3 py-1"
          >
            Add Event
          </button>
        </div>
      </div>

      {/* All-day events */}
      {allDayEvents.length > 0 && (
        <div className="border-b border-gray-200 p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">All Day</h3>
          <div className="space-y-2">
            {allDayEvents.map((event) => (
              <div
                key={event.id}
                className="bg-blue-100 border border-blue-200 rounded-lg p-3 cursor-pointer hover:bg-blue-200 transition-colors"
                onClick={() => onEditEvent(event)}
              >
                <div className="font-medium text-blue-900">{event.title}</div>
                {event.description && (
                  <div className="text-sm text-blue-700 mt-1">{event.description}</div>
                )}
                {event.location && (
                  <div className="text-sm text-blue-600 mt-1">📍 {event.location}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timed events */}
      <div className="flex-1 overflow-y-auto">
        {timedEvents.length === 0 && allDayEvents.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-500">
            <svg className="w-12 h-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="text-lg font-medium mb-2">No events scheduled</p>
            <p className="text-sm mb-4">Create your first event for this day</p>
            <button
              onClick={handleCreateEvent}
              className="btn-primary"
            >
              Create Event
            </button>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {timedEvents
              .sort((a, b) =>
                DateTime.fromISO(a.start_datetime).toMillis() -
                DateTime.fromISO(b.start_datetime).toMillis()
              )
              .map((event) => (
                <div
                  key={event.id}
                  className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm cursor-pointer hover:shadow-md hover:border-gray-300 transition-all"
                  onClick={() => onEditEvent(event)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-1">{event.title}</h4>
                      <div className="text-sm text-gray-600 mb-2">
                        {formatEventDateTime(
                          event.start_datetime,
                          event.end_datetime,
                          event.all_day
                        )}
                      </div>
                      {event.description && (
                        <p className="text-sm text-gray-700 mb-2">{event.description}</p>
                      )}
                      {event.location && (
                        <p className="text-sm text-gray-600">📍 {event.location}</p>
                      )}
                      {event.attendees.length > 0 && (
                        <p className="text-sm text-gray-600 mt-1">
                          👥 {event.attendees.length} attendee{event.attendees.length !== 1 ? 's' : ''}
                        </p>
                      )}
                    </div>
                    <div className="w-4 h-4 bg-blue-500 rounded-full flex-shrink-0 mt-1"></div>
                  </div>
                </div>
              ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DayView;