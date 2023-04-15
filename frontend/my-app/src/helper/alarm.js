export const isValidDateTime = (date, time) => {
  return (date && date.length > 0 && time && time.length > 0);
}

export const isEmptyDateTime = (date, time) => {
  return ((!date || date.length === 0) && (!time || time.length === 0));
}

export const isBefore = (startDate, startTime, endDate, endTime) => {
  if (!isValidDateTime(startDate, startTime) || !isValidDateTime(endDate, endTime)) return true;
  const startDateString = (new Date(startDate)).getTime();
  const endDateString = (new Date(endDate)).getTime();
  console.log(startDateString)
  console.log(endDateString)
  if (startDateString > endDateString) {
    return false;
  } else if (startDateString === endDateString) {
    const start = getHourMinutes(startTime);
    const end = getHourMinutes(endTime);
    if (start[0] > end[0]) return false;
    if (start[0] === end[0] && start[1] >= end[1]) return false;
    return true;
  } else {
    return true;
  }
}

export const getHourMinutes = (time) => {
  return time.split(":");
}