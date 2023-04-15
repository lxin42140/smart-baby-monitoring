import { baseUrl } from "."

const babyUrl = `${baseUrl}/baby`;

export const getAllBabies = async () => {
  const res = await fetch(`${babyUrl}/all`, {
    method: "GET"
  });
  if (res.status === 200) {
    const resJson = await res.json();
    return resJson
  }
}

export const createNewBaby = async (newBaby) => {
  console.log(newBaby)
  const res = await fetch(`${babyUrl}/new`, {
    method: "POST",
    body: JSON.stringify(newBaby),
    header: new Headers({
      "Content-Type": "application/json",
    }),
    mode: 'cors'
  });
  if (res.status === 200) return true;
  else return false;
}

export const editBaby = async (newBaby) => {
  const res = await fetch(`${babyUrl}/${newBaby.id}`, {
    method: "POST",
    body: JSON.stringify(newBaby),
    header: new Headers({
      "Content-Type": "application/json",
    }),
    mode: 'cors'
  });
  if (res.status === 200) return true;
  else return false;
}