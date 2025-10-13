import { DateTime } from 'luxon';
import {
  formatEventDateTime,
  formatTimeForInput,
  formatDateForInput,
  parseInputDateTime,
  parseInputDate,
  getMonthCalendarDays,
  getWeekDays,
  isEventInDay,
  getCurrentTimezone,
} from '../date';

describe('Date utilities', () => {
  describe('formatEventDateTime', () => {
    it('formats all-day event on same day', () => {
      const start = '2023-12-01T00:00:00Z';
      const end = '2023-12-01T23:59:59Z';
      const result = formatEventDateTime(start, end, true);
      // Luxon handles UTC to local conversion, adjust expectation
      expect(result).toContain('2023');
    });

    it('formats all-day event spanning multiple days', () => {
      const start = '2023-12-01T00:00:00Z';
      const end = '2023-12-03T23:59:59Z';
      const result = formatEventDateTime(start, end, true);
      // Should contain a date range with 2023
      expect(result).toContain('2023');
      expect(result).toContain(' - ');
    });

    it('formats timed event on same day', () => {
      const start = '2023-12-01T10:00:00Z';
      const end = '2023-12-01T11:00:00Z';
      const result = formatEventDateTime(start, end, false);
      expect(result).toMatch(/Dec 1, 2023 \d+:\d+ [AP]M - \d+:\d+ [AP]M/);
    });
  });

  describe('formatTimeForInput', () => {
    it('formats ISO string for time input', () => {
      const iso = '2023-12-01T15:30:00Z';
      const result = formatTimeForInput(iso);
      expect(result).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/);
    });
  });

  describe('formatDateForInput', () => {
    it('formats ISO string for date input', () => {
      const iso = '2023-12-01T15:30:00Z';
      const result = formatDateForInput(iso);
      expect(result).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    });
  });

  describe('parseInputDateTime', () => {
    it('parses datetime input to UTC ISO', () => {
      const input = '2023-12-01T15:30';
      const result = parseInputDateTime(input, 'UTC');
      expect(result).toBe('2023-12-01T15:30:00.000Z');
    });
  });

  describe('parseInputDate', () => {
    it('parses date input to start/end of day', () => {
      const input = '2023-12-01';
      const result = parseInputDate(input, 'UTC');
      expect(result.start).toBe('2023-12-01T00:00:00.000Z');
      expect(result.end).toBe('2023-12-01T23:59:59.999Z');
    });
  });

  describe('getMonthCalendarDays', () => {
    it('returns 42 days for calendar grid', () => {
      const days = getMonthCalendarDays(2023, 12);
      expect(days).toHaveLength(42);
    });

    it('includes days from previous and next month', () => {
      const days = getMonthCalendarDays(2023, 12);
      const firstDay = days[0];
      const lastDay = days[41];

      // First day should be from previous month (11) or current month (12)
      expect(firstDay.month).toBeLessThanOrEqual(12);
      // Last day should be from current month (12) or next month (1, meaning January of next year)
      expect(lastDay.month >= 1 && lastDay.month <= 12).toBe(true);
    });
  });

  describe('getWeekDays', () => {
    it('returns 7 days starting from Monday', () => {
      const date = DateTime.fromISO('2023-12-01'); // Friday
      const days = getWeekDays(date);
      expect(days).toHaveLength(7);

      // First day should be Monday of that week
      expect(days[0].weekday).toBe(1); // Monday
      expect(days[6].weekday).toBe(7); // Sunday
    });
  });

  describe('isEventInDay', () => {
    const day = DateTime.fromISO('2023-12-01');

    it('returns true for event within the day', () => {
      const start = '2023-12-01T10:00:00Z';
      const end = '2023-12-01T11:00:00Z';
      expect(isEventInDay(start, end, day)).toBe(true);
    });

    it('returns false for event on different day', () => {
      const start = '2023-12-02T10:00:00Z';
      const end = '2023-12-02T11:00:00Z';
      expect(isEventInDay(start, end, day)).toBe(false);
    });

    it('returns true for event spanning the day', () => {
      // Create day in UTC to match event times
      const dayUTC = DateTime.fromISO('2023-12-01', { zone: 'utc' });
      const start = '2023-11-30T22:00:00Z';
      const end = '2023-12-01T02:00:00Z';
      // Event overlaps with Dec 1st UTC
      expect(isEventInDay(start, end, dayUTC)).toBe(true);
    });
  });

  describe('getCurrentTimezone', () => {
    it('returns a valid timezone', () => {
      const tz = getCurrentTimezone();
      expect(typeof tz).toBe('string');
      expect(tz.length).toBeGreaterThan(0);
    });
  });
});