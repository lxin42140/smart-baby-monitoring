import { baseUrl } from "."

const alarmUrl = `${baseUrl}/data/alarm`

export const getAllAlarms = async () => {
  const res = await fetch(`${alarmUrl}`, {
    method: "GET"
  })
  if (res.status === 200) {
    const resJson = await res.json();
    return resJson
  }
}

export const getFilteredAlarms = async (fogName, startDate = '', startTime = '', endDate = '', endTime = '') => {
  let url = `${alarmUrl}/${fogName}`
  if (startDate.length > 0) {
    url += `?start_time=${startDate} ${startTime}:00&end_time=${endDate} ${endTime}:00`
  }
  console.log(url)
  const res = await fetch(url, {
    method: "GET",
  })
  if (res.status === 200) {
    const resJson = await res.json();
    return resJson
  }
}