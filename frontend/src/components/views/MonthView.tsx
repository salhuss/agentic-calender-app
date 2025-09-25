import React from 'react';
import { DateTime } from 'luxon';
import { Event } from '@/types/api';
import { useEvents } from '@/hooks/useEvents';
import { getMonthCalendarDays, isEventInDay } from '@/utils/date';

interface MonthViewProps {
  currentDate: DateTime;
  onDateChange: (date: DateTime) => void;
  onNewEvent: (date?: DateTime) => void;
  onEditEvent: (event: Event) => void;
}

const MonthView: React.FC<MonthViewProps> = ({
  currentDate,
  onDateChange,
  onNewEvent,
  onEditEvent,
}) => {
  const startOfMonth = currentDate.startOf('month');
  const endOfMonth = currentDate.endOf('month');

  const { data: eventsData, isLoading } = useEvents({
    from: startOfMonth.toUTC().toISO()!,
    to: endOfMonth.toUTC().toISO()!,
  });

  const days = getMonthCalendarDays(currentDate.year, currentDate.month);
  const today = DateTime.now();
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  const getEventsForDay = (day: DateTime) => {
    if (!eventsData?.events) return [];
    return eventsData.events.filter(event =>
      isEventInDay(event.start_datetime, event.end_datetime, day)
    );
  };

  const handleDateClick = (day: DateTime) => {
    if (day.month !== currentDate.month) {
      onDateChange(day);
    }
    onNewEvent(day);
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
      {/* Day headers */}
      <div className="grid grid-cols-7 border-b border-gray-200">
        {dayNames.map((day) => (
          <div
            key={day}
            className="py-2 px-2 text-center text-sm font-medium text-gray-500 border-r border-gray-200 last:border-r-0"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="flex-1 grid grid-rows-6">
        {Array.from({ length: 6 }, (_, weekIndex) => (
          <div key={weekIndex} className="grid grid-cols-7 border-b border-gray-200 last:border-b-0">
            {days.slice(weekIndex * 7, (weekIndex + 1) * 7).map((day) => {
              const isCurrentMonth = day.month === currentDate.month;
              const isToday = day.hasSame(today, 'day');
              const events = getEventsForDay(day);

              return (
                <div
                  key={day.toISODate()}
                  className="calendar-cell border-r border-gray-200 last:border-r-0 flex flex-col"
                  onClick={() => handleDateClick(day)}
                >
                  {/* Date number */}
                  <div className="flex justify-between items-start">
                    <span
                      className={`text-sm font-medium ${
                        !isCurrentMonth
                          ? 'text-gray-400'
                          : isToday
                          ? 'bg-blue-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs'
                          : 'text-gray-900'
                      }`}
                    >
                      {day.day}
                    </span>
                  </div>

                  {/* Events */}
                  <div className="flex-1 mt-1 space-y-1">
                    {events.slice(0, 3).map((event) => (
                      <div
                        key={event.id}
                        className="calendar-event truncate"
                        onClick={(e) => {
                          e.stopPropagation();
                          onEditEvent(event);
                        }}
                        title={event.title}
                      >
                        {event.title}
                      </div>
                    ))}
                    {events.length > 3 && (
                      <div className="text-xs text-gray-500">
                        +{events.length - 3} more
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
};

export default MonthView;