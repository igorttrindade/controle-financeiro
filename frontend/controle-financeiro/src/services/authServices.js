import { apiRequest } from "./api";

export async function registerUser(userData) {
    return apiRequest("/api/users/register", "POST", userData)
}

export async function loginUser (userData) {
    return apiRequest("/api/users/login", "POST", userData)
}