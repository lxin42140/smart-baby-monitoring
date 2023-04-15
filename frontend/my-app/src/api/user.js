import { baseUrl } from "."

const userUrl = `${baseUrl}/user`

export const login = async (username, password) => {
  console.log(JSON.stringify({
    username: username,
    password: password
  }))
  console.log(`${userUrl}/login`)
  const res = await fetch(`${userUrl}/login`, {
    method: 'POST',
    body: JSON.stringify({
      username: username,
      password: password
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

export const register = async (username, first_name, last_name, password) => {
  const res = await fetch(`${userUrl}/register`, {
    method: 'POST',
    body: JSON.stringify({
      username,
      first_name,
      last_name,
      password
    }),
    header: new Headers({
      "Content-Type": "application/json",
    }),
    mode: 'cors'
  })
  if (res.status === 200) return true;
  else return false;
}

export const logout = async () => {
  const res = await fetch(`${userUrl}/logout`, {
    method: 'GET',
  })
  if (res.status === 200) return true;
  else return false;
}