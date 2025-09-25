import React, { useState } from 'react';
import { DateTime } from 'luxon';
import MiniCalendar from './MiniCalendar';
import SearchBox from './SearchBox';

interface SidebarProps {
  onNewEvent: (date?: DateTime) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onNewEvent }) => {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">AI Calendar</h2>
        <p className="text-sm text-gray-600 mt-1">Intelligent scheduling assistant</p>
      </div>

      {/* Quick Actions */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={() => onNewEvent()}
          className="w-full btn-primary flex items-center justify-center space-x-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>Create Event</span>
        </button>
      </div>

      {/* Search */}
      <div className="p-4 border-b border-gray-200">
        <SearchBox
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search events..."
        />
      </div>

      {/* Mini Calendar */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Calendar</h3>
        <MiniCalendar onDateClick={(date) => onNewEvent(date)} />
      </div>

      {/* AI Assistant */}
      <div className="p-4 flex-1">
        <h3 className="text-sm font-medium text-gray-900 mb-3">AI Assistant</h3>
        <div className="bg-blue-50 rounded-lg p-3">
          <p className="text-xs text-blue-800">
            Try creating events with natural language:
          </p>
          <ul className="text-xs text-blue-700 mt-2 space-y-1">
            <li>• "Meeting with John tomorrow 3pm"</li>
            <li>• "Lunch at Cafe Rio on Friday"</li>
            <li>• "All day conference next week"</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;