import React from 'react';
import { DateTime } from 'luxon';
import { ViewType } from '@/App';

interface ToolbarProps {
  currentDate: DateTime;
  viewType: ViewType;
  onDateChange: (date: DateTime) => void;
  onViewChange: (view: ViewType) => void;
  onTodayClick: () => void;
  onNewEvent: () => void;
}

const Toolbar: React.FC<ToolbarProps> = ({
  currentDate,
  viewType,
  onDateChange,
  onViewChange,
  onTodayClick,
  onNewEvent,
}) => {
  const handlePrevious = () => {
    const amount = viewType === 'month' ? { months: -1 } :
                   viewType === 'week' ? { weeks: -1 } : { days: -1 };
    onDateChange(currentDate.plus(amount));
  };

  const handleNext = () => {
    const amount = viewType === 'month' ? { months: 1 } :
                   viewType === 'week' ? { weeks: 1 } : { days: 1 };
    onDateChange(currentDate.plus(amount));
  };

  const getDateTitle = () => {
    switch (viewType) {
      case 'month':
        return currentDate.toFormat('MMMM yyyy');
      case 'week':
        const startWeek = currentDate.startOf('week');
        const endWeek = currentDate.endOf('week');
        return `${startWeek.toFormat('MMM d')} - ${endWeek.toFormat('MMM d, yyyy')}`;
      case 'day':
        return currentDate.toFormat('EEEE, MMMM d, yyyy');
      default:
        return '';
    }
  };

  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-4">
        {/* Navigation */}
        <div className="flex items-center space-x-2">
          <button
            onClick={onTodayClick}
            className="px-3 py-1 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Today
          </button>
          <button
            onClick={handlePrevious}
            className="p-1 text-gray-500 hover:text-gray-700"
            aria-label="Previous"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={handleNext}
            className="p-1 text-gray-500 hover:text-gray-700"
            aria-label="Next"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        {/* Current Date Title */}
        <h1 className="text-xl font-semibold text-gray-900">{getDateTitle()}</h1>
      </div>

      <div className="flex items-center space-x-4">
        {/* View Type Selector */}
        <div className="flex bg-gray-100 rounded-md p-1">
          {(['month', 'week', 'day'] as ViewType[]).map((view) => (
            <button
              key={view}
              onClick={() => onViewChange(view)}
              className={`px-3 py-1 text-sm font-medium rounded-md capitalize transition-colors ${
                viewType === view
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {view}
            </button>
          ))}
        </div>

        {/* New Event Button */}
        <button
          onClick={onNewEvent}
          className="btn-primary flex items-center space-x-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>New Event</span>
        </button>
      </div>
    </div>
  );
};

export default Toolbar;