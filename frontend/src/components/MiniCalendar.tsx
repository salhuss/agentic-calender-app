import React, { useState } from 'react';
import { DateTime } from 'luxon';
import { getMonthCalendarDays } from '@/utils/date';

interface MiniCalendarProps {
  onDateClick: (date: DateTime) => void;
}

const MiniCalendar: React.FC<MiniCalendarProps> = ({ onDateClick }) => {
  const [currentMonth, setCurrentMonth] = useState(DateTime.now());
  const today = DateTime.now();

  const days = getMonthCalendarDays(currentMonth.year, currentMonth.month);
  const dayNames = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

  const handlePrevMonth = () => {
    setCurrentMonth(currentMonth.minus({ months: 1 }));
  };

  const handleNextMonth = () => {
    setCurrentMonth(currentMonth.plus({ months: 1 }));
  };

  const handleDateClick = (date: DateTime) => {
    onDateClick(date);
  };

  return (
    <div className="w-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <button
          onClick={handlePrevMonth}
          className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          aria-label="Previous month"
        >
          <svg className="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
          {currentMonth.toFormat('MMM yyyy')}
        </h4>
        <button
          onClick={handleNextMonth}
          className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          aria-label="Next month"
        >
          <svg className="w-4 h-4 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      {/* Day headers */}
      <div className="grid grid-cols-7 gap-1 mb-1">
        {dayNames.map((day) => (
          <div
            key={day}
            className="h-6 flex items-center justify-center text-xs font-medium text-gray-500 dark:text-gray-400"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-1">
        {days.map((day) => {
          const isCurrentMonth = day.month === currentMonth.month;
          const isToday = day.hasSame(today, 'day');

          return (
            <button
              key={day.toISODate()}
              onClick={() => handleDateClick(day)}
              className={`h-8 flex items-center justify-center text-xs rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
                !isCurrentMonth
                  ? 'text-gray-400 dark:text-gray-600'
                  : isToday
                  ? 'bg-blue-600 dark:bg-blue-500 text-white hover:bg-blue-700 dark:hover:bg-blue-600'
                  : 'text-gray-900 dark:text-gray-100'
              }`}
            >
              {day.day}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default MiniCalendar;