import { baseUrl } from ".";

const configUrl = `${baseUrl}/data/config`;

export const getDefaultConfig = async () => {
  const res = await fetch(`${configUrl}/default`, {
    method: "GET",
    // credentials: 'include',
  })

  // const res = await fetch(`${baseUrl}/baby/all`, {
  //   method: "GET",
  //   // credentials: 'include',
  // })

  if (res.status === 200) {
    const data = await res.json();
    return data;
  } else {
    return null;
  }
}

export const getConfig = async (config) => {
  const res = await fetch(`${configUrl}/${config}`, {
    method: "GET",
  })
  if (res.status === 200) {
    const data = await res.json();
    return data;
  } else {
    return null;
  }
}

export const updateConfig = async (config, value) => {
  const res = await fetch(`${configUrl}/${config}`, {
    method: "POST",
    body: JSON.stringify({
      name: config,
      config: value
    }),
    header: new Headers({
      "Content-Type": "application/json",
    }),
    mode: 'cors'
  })
  console.log(res)
  if (res.status === 200) return true;
  else return false;
}

export const getServerConfig = async () => {
  const res = await fetch(`${configUrl}/server`, {
    method: "GET",
    // credentials: 'include',
  })
  if (res.status === 200) {
    const data = await res.json();
    return data;
  } else {
    return null;
  }
}