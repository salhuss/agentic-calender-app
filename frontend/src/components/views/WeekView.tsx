import React from 'react';
import { DateTime } from 'luxon';
import { Event } from '@/types/api';
import { useEvents } from '@/hooks/useEvents';
import { getWeekDays, isEventInDay } from '@/utils/date';

interface WeekViewProps {
  currentDate: DateTime;
  onDateChange: (date: DateTime) => void;
  onNewEvent: (date?: DateTime) => void;
  onEditEvent: (event: Event) => void;
}

const WeekView: React.FC<WeekViewProps> = ({
  currentDate,
  onDateChange,
  onNewEvent,
  onEditEvent,
}) => {
  const weekStart = currentDate.startOf('week');
  const weekEnd = currentDate.endOf('week');

  const { data: eventsData, isLoading } = useEvents({
    from: weekStart.toUTC().toISO()!,
    to: weekEnd.toUTC().toISO()!,
  });

  const days = getWeekDays(currentDate);
  const today = DateTime.now();

  const getEventsForDay = (day: DateTime) => {
    if (!eventsData?.events) return [];
    return eventsData.events.filter(event =>
      isEventInDay(event.start_datetime, event.end_datetime, day)
    );
  };

  const handleDateClick = (day: DateTime) => {
    onNewEvent(day);
  };

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Day headers */}
      <div className="grid grid-cols-7 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        {days.map((day) => {
          const isToday = day.hasSame(today, 'day');

          return (
            <div
              key={day.toISODate()}
              className="py-3 px-2 text-center border-r border-gray-200 dark:border-gray-700 last:border-r-0"
            >
              <div className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                {day.toFormat('EEE')}
              </div>
              <div
                className={`text-lg font-semibold mt-1 ${
                  isToday
                    ? 'bg-blue-600 dark:bg-blue-500 text-white w-8 h-8 rounded-full flex items-center justify-center mx-auto'
                    : 'text-gray-900 dark:text-gray-100'
                }`}
              >
                {day.day}
              </div>
            </div>
          );
        })}
      </div>

      {/* Calendar grid */}
      <div className="flex-1 grid grid-cols-7">
        {days.map((day) => {
          const events = getEventsForDay(day);

          return (
            <div
              key={day.toISODate()}
              className="calendar-cell border-r border-gray-200 dark:border-gray-700 last:border-r-0 flex flex-col"
              onClick={() => handleDateClick(day)}
            >
              {/* Events */}
              <div className="space-y-1">
                {events.map((event) => (
                  <div
                    key={event.id}
                    className="calendar-event"
                    onClick={(e) => {
                      e.stopPropagation();
                      onEditEvent(event);
                    }}
                    title={event.title}
                  >
                    <div className="font-medium truncate">{event.title}</div>
                    {!event.all_day && (
                      <div className="text-xs opacity-75">
                        {DateTime.fromISO(event.start_datetime).toFormat('h:mm a')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default WeekView;