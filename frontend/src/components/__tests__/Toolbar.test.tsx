import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { DateTime } from 'luxon';
import Toolbar from '../Toolbar';
import { ViewType } from '@/App';

describe('Toolbar', () => {
  const mockProps = {
    currentDate: DateTime.fromISO('2023-12-01'),
    viewType: 'month' as ViewType,
    onDateChange: vi.fn(),
    onViewChange: vi.fn(),
    onTodayClick: vi.fn(),
    onNewEvent: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly', () => {
    render(<Toolbar {...mockProps} />);

    expect(screen.getByText('December 2023')).toBeInTheDocument();
    expect(screen.getByText('Today')).toBeInTheDocument();
    expect(screen.getByText('New Event')).toBeInTheDocument();
  });

  it('handles today click', () => {
    render(<Toolbar {...mockProps} />);

    fireEvent.click(screen.getByText('Today'));
    expect(mockProps.onTodayClick).toHaveBeenCalled();
  });

  it('handles new event click', () => {
    render(<Toolbar {...mockProps} />);

    fireEvent.click(screen.getByText('New Event'));
    expect(mockProps.onNewEvent).toHaveBeenCalled();
  });

  it('handles view change', () => {
    render(<Toolbar {...mockProps} />);

    fireEvent.click(screen.getByText('week'));
    expect(mockProps.onViewChange).toHaveBeenCalledWith('week');
  });

  it('handles navigation', () => {
    render(<Toolbar {...mockProps} />);

    const prevButton = screen.getByLabelText('Previous');
    const nextButton = screen.getByLabelText('Next');

    fireEvent.click(prevButton);
    expect(mockProps.onDateChange).toHaveBeenCalled();

    fireEvent.click(nextButton);
    expect(mockProps.onDateChange).toHaveBeenCalled();
  });

  it('displays correct title for week view', () => {
    render(<Toolbar {...mockProps} viewType="week" />);

    // Should show week range - adjust expected text based on actual implementation
    expect(screen.getByText(/Nov 27 - Dec 3, 2023/)).toBeInTheDocument();
  });

  it('displays correct title for day view', () => {
    render(<Toolbar {...mockProps} viewType="day" />);

    expect(screen.getByText('Friday, December 1, 2023')).toBeInTheDocument();
  });
});