import { apiRequest } from '../http/api'

export async function getTransactions(options = {}) {
  return apiRequest('/api/transaction/', 'GET', null, options)
}

export async function getOperations(options = {}) {
  return apiRequest('/api/transaction/operations', 'GET', null, options)
}

export async function createOperation(payload, options = {}) {
  return apiRequest('/api/transaction/operations', 'POST', payload, options)
}

export async function createTransaction(payload, options = {}) {
  return apiRequest('/api/transaction/create', 'POST', payload, options)
}

export async function getTransactionById(idTransacao, options = {}) {
  return apiRequest(`/api/transaction/${idTransacao}`, 'GET', null, options)
}

export async function updateTransaction(idTransacao, payload, options = {}) {
  return apiRequest(`/api/transaction/${idTransacao}`, 'PUT', payload, options)
}

export async function deleteTransaction(idTransacao, options = {}) {
  return apiRequest(`/api/transaction/${idTransacao}`, 'DELETE', null, options)
}
