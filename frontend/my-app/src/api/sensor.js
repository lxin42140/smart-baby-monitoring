import { baseUrl } from "."
const userUrl = `${baseUrl}/data/sensor`

export const fetchData = async () => {
    const API_URL = baseUrl + '/data/sensor';

    // Fetch the data from the API
    const response = await fetch(API_URL);
    const data = await response.json();
    // console.log("Fetching data from sensor: ", data)
    return data;
}

// Function gets the data based on deviceName and date.
export const updateChartByNameAndDate = async (deviceName, sqlStartDate, sqlEndDate) => {
    // Fetch the data from the API using the selected time
    const reset = 'false'; // Set the reset parameter as required (use 'true' or 'false')

    const fogName = deviceName; // Replace with your fog name
    const apiUrl = userUrl + `/${deviceName}?start_time=${sqlStartDate}&end_time=${sqlEndDate}&reset=${reset}`; 

    // Fetch the data from the API
    const response = await fetch(apiUrl);
    const filteredData = await response.json();

    console.log('Received date range data: ', filteredData);
    return filteredData; 
}