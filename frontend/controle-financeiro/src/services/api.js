const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000"

export async function apiRequest(endpoint, method = "GET", data = null) {
  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  }

  if (data) {
    options.body = JSON.stringify(data)
  }

  const response = await fetch(`${API_URL}${endpoint}`, options)
  if (!response.ok) {
    throw new Error(`Erro na requisição: ${response.status}`)
  }

  return await response.json()
}
