import React from 'react';
import { DateTime } from 'luxon';
import { Sun, Moon } from 'lucide-react';
import { ViewType } from '@/App';
import { useTheme } from '@/contexts/ThemeContext';

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
  const { theme, toggleTheme } = useTheme();

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
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div className="flex items-center space-x-4 w-full sm:w-auto">
        {/* Navigation */}
        <div className="flex items-center space-x-2">
          <button
            onClick={onTodayClick}
            className="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Today
          </button>
          <button
            onClick={handlePrevious}
            className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
            aria-label="Previous"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={handleNext}
            className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
            aria-label="Next"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        {/* Current Date Title */}
        <h1 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-gray-100 truncate">
          {getDateTitle()}
        </h1>
      </div>

      <div className="flex items-center gap-2 sm:gap-4 w-full sm:w-auto justify-between sm:justify-end">
        {/* View Type Selector */}
        <div className="flex bg-gray-100 dark:bg-gray-700 rounded-md p-1">
          {(['month', 'week', 'day'] as ViewType[]).map((view) => (
            <button
              key={view}
              onClick={() => onViewChange(view)}
              className={`px-2 sm:px-3 py-1 text-xs sm:text-sm font-medium rounded-md capitalize transition-colors ${
                viewType === view
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100'
              }`}
            >
              {view}
            </button>
          ))}
        </div>

        {/* Dark Mode Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
          aria-label="Toggle dark mode"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        {/* New Event Button */}
        <button
          onClick={onNewEvent}
          className="btn-primary flex items-center space-x-2 whitespace-nowrap"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span className="hidden sm:inline">New Event</span>
          <span className="sm:hidden">New</span>
        </button>
      </div>
    </div>
  );
};

export default Toolbar;