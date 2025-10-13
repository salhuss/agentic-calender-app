import React, { useState } from 'react';
import { DateTime } from 'luxon';
import { Menu, X } from 'lucide-react';
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
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

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
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`
          fixed lg:relative inset-y-0 left-0 z-50
          w-80 bg-white dark:bg-gray-800
          border-r border-gray-200 dark:border-gray-700
          flex-shrink-0 transform transition-transform duration-300 ease-in-out
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        {/* Close button for mobile */}
        <button
          onClick={() => setIsSidebarOpen(false)}
          className="lg:hidden absolute top-4 right-4 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <X className="w-5 h-5 text-gray-600 dark:text-gray-300" />
        </button>
        <Sidebar onNewEvent={handleNewEvent} />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Toolbar */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 lg:px-6 py-4">
          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="lg:hidden mb-4 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <Menu className="w-6 h-6 text-gray-600 dark:text-gray-300" />
          </button>

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
        <div className="flex-1 p-4 lg:p-6 overflow-auto">
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