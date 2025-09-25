import React from 'react';
import { DateTime } from 'luxon';
import { ViewType } from '@/App';
import { Event } from '@/types/api';
import MonthView from './views/MonthView';
import WeekView from './views/WeekView';
import DayView from './views/DayView';

interface CalendarViewProps {
  currentDate: DateTime;
  viewType: ViewType;
  onDateChange: (date: DateTime) => void;
  onNewEvent: (date?: DateTime) => void;
  onEditEvent: (event: Event) => void;
}

const CalendarView: React.FC<CalendarViewProps> = ({
  currentDate,
  viewType,
  onDateChange,
  onNewEvent,
  onEditEvent,
}) => {
  const renderView = () => {
    const commonProps = {
      currentDate,
      onDateChange,
      onNewEvent,
      onEditEvent,
    };

    switch (viewType) {
      case 'month':
        return <MonthView {...commonProps} />;
      case 'week':
        return <WeekView {...commonProps} />;
      case 'day':
        return <DayView {...commonProps} />;
      default:
        return <MonthView {...commonProps} />;
    }
  };

  return (
    <div className="h-full w-full bg-white rounded-lg border border-gray-200 shadow-sm">
      {renderView()}
    </div>
  );
};

export default CalendarView;