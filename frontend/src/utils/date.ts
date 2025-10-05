// Date utilities using Luxon
import { DateTime } from 'luxon';

export const formatEventDateTime = (
  start: string,
  end: string,
  allDay: boolean,
  timezone: string = 'local'
): string => {
  const startDt = DateTime.fromISO(start).setZone(timezone);
  const endDt = DateTime.fromISO(end).setZone(timezone);

  if (allDay) {
    if (startDt.hasSame(endDt, 'day')) {
      return startDt.toFormat('MMM d, yyyy');
    }
    return `${startDt.toFormat('MMM d')} - ${endDt.toFormat('MMM d, yyyy')}`;
  }

  if (startDt.hasSame(endDt, 'day')) {
    return `${startDt.toFormat('MMM d, yyyy h:mm a')} - ${endDt.toFormat('h:mm a')}`;
  }

  return `${startDt.toFormat('MMM d, h:mm a')} - ${endDt.toFormat('MMM d, h:mm a')}`;
};

export const formatTimeForInput = (isoString: string): string => {
  const dt = DateTime.fromISO(isoString);
  return dt.toFormat("yyyy-MM-dd'T'HH:mm");
};

export const formatDateForInput = (isoString: string): string => {
  const dt = DateTime.fromISO(isoString);
  return dt.toFormat('yyyy-MM-dd');
};

export const parseInputDateTime = (value: string, timezone: string = 'local'): string => {
  const dt = DateTime.fromISO(value, { zone: timezone });
  return dt.toUTC().toISO()!;
};

export const parseInputDate = (value: string, timezone: string = 'local'): { start: string; end: string } => {
  const dt = DateTime.fromISO(value, { zone: timezone });
  const start = dt.startOf('day').toUTC().toISO()!;
  const end = dt.endOf('day').toUTC().toISO()!;
  return { start, end };
};

export const getMonthCalendarDays = (year: number, month: number): DateTime[] => {
  const firstDay = DateTime.local(year, month, 1);

  // Start from the beginning of the week containing the first day
  const startDate = firstDay.startOf('week');

  const days: DateTime[] = [];
  let current = startDate;

  // Always return exactly 42 days (6 weeks * 7 days)
  for (let i = 0; i < 42; i++) {
    days.push(current);
    current = current.plus({ days: 1 });
  }

  return days;
};

export const getWeekDays = (date: DateTime): DateTime[] => {
  const startOfWeek = date.startOf('week');
  const days: DateTime[] = [];

  for (let i = 0; i < 7; i++) {
    days.push(startOfWeek.plus({ days: i }));
  }

  return days;
};

export const isEventInDay = (
  eventStart: string,
  eventEnd: string,
  day: DateTime
): boolean => {
  const startDt = DateTime.fromISO(eventStart);
  const endDt = DateTime.fromISO(eventEnd);
  // Convert to the same timezone as the day for comparison
  const dayStart = day.startOf('day').toUTC();
  const dayEnd = day.endOf('day').toUTC();

  return startDt.toUTC() < dayEnd && endDt.toUTC() > dayStart;
};

export const getCurrentTimezone = (): string => {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
};