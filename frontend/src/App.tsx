import React, { useState } from 'react';
import { DateTime } from 'luxon';
import CalendarView from '@/components/CalendarView';
import Toolbar from '@/components/Toolbar';
import Sidebar from '@/components/Sidebar';
import EventModal from '@/components/EventModal';
import { Event } from '@/types/api';

export type ViewType = 'month' | 'week' | 'day';

function App() {
  const [currentDate, setCurrentDate] = useState(DateTime.now());
  const [viewType, setViewType] = useState<ViewType>('month');
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [isEventModalOpen, setIsEventModalOpen] = useState(false);
  const [eventModalDate, setEventModalDate] = useState<DateTime | null>(null);

  const handleDateChange = (date: DateTime) => {
    setCurrentDate(date);
  };

  const handleViewChange = (view: ViewType) => {
    setViewType(view);
  };

  const handleTodayClick = () => {
    setCurrentDate(DateTime.now());
  };

  const handleNewEvent = (date?: DateTime) => {
    setSelectedEvent(null);
    setEventModalDate(date || currentDate);
    setIsEventModalOpen(true);
  };

  const handleEditEvent = (event: Event) => {
    setSelectedEvent(event);
    setEventModalDate(null);
    setIsEventModalOpen(true);
  };

  const handleCloseEventModal = () => {
    setIsEventModalOpen(false);
    setSelectedEvent(null);
    setEventModalDate(null);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex-shrink-0">
        <Sidebar onNewEvent={handleNewEvent} />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Toolbar */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <Toolbar
            currentDate={currentDate}
            viewType={viewType}
            onDateChange={handleDateChange}
            onViewChange={handleViewChange}
            onTodayClick={handleTodayClick}
            onNewEvent={handleNewEvent}
          />
        </div>

        {/* Calendar Content */}
        <div className="flex-1 p-6">
          <CalendarView
            currentDate={currentDate}
            viewType={viewType}
            onDateChange={handleDateChange}
            onNewEvent={handleNewEvent}
            onEditEvent={handleEditEvent}
          />
        </div>
      </div>

      {/* Event Modal */}
      {isEventModalOpen && (
        <EventModal
          event={selectedEvent}
          defaultDate={eventModalDate}
          onClose={handleCloseEventModal}
        />
      )}
    </div>
  );
}

export default App;