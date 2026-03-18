const INCOME_TYPES = new Set(['entrada', 'receita', 'income'])
const EXPENSE_TYPES = new Set(['saida', 'despesa', 'expense'])

export function normalizeOperationType(rawType) {
  const normalized = String(rawType || '').trim().toLowerCase()
  if (INCOME_TYPES.has(normalized)) return 'entrada'
  if (EXPENSE_TYPES.has(normalized)) return 'despesa'
  return null
}

export function parseCurrencyToNumber(rawValue) {
  const value = String(rawValue || '').trim()
  if (!value) return Number.NaN

  const sanitized = value
    .replace(/\s/g, '')
    .replace(/\./g, '')
    .replace(',', '.')
    .replace(/[^\d.-]/g, '')

  if (!sanitized || sanitized === '.' || sanitized === '-' || sanitized === '-.') {
    return Number.NaN
  }

  return Number(sanitized)
}

export function toDatetimeLocalValue(date = new Date()) {
  const dateValue = date instanceof Date ? date : new Date(date)
  if (Number.isNaN(dateValue.getTime())) return ''

  const year = dateValue.getFullYear()
  const month = String(dateValue.getMonth() + 1).padStart(2, '0')
  const day = String(dateValue.getDate()).padStart(2, '0')
  const hours = String(dateValue.getHours()).padStart(2, '0')
  const minutes = String(dateValue.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

export function toIsoFromDatetimeLocal(rawValue) {
  const value = String(rawValue || '').trim()
  if (!value) return null

  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return null
  return parsed.toISOString()
}

export function validateTransactionInput(input) {
  const errors = {}

  const normalizedType = normalizeOperationType(input?.tipo_operacao)
  if (!normalizedType) {
    errors.tipo_operacao = 'Selecione um tipo de operação válido.'
  }

  const operationName = String(input?.nome_operacao || '').trim()
  if (operationName.length < 2 || operationName.length > 120) {
    errors.nome_operacao = 'O nome da operação deve ter entre 2 e 120 caracteres.'
  }

  const amount = parseCurrencyToNumber(input?.valor_transacao)
  if (!Number.isFinite(amount) || amount <= 0) {
    errors.valor_transacao = 'O valor deve ser maior que zero.'
  }

  const description = String(input?.descricao_transacao || '').trim()
  if (description.length < 3 || description.length > 500) {
    errors.descricao_transacao = 'A descrição deve ter entre 3 e 500 caracteres.'
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
    normalized: {
      tipo_operacao: normalizedType,
      nome_operacao: operationName,
      valor_transacao: amount,
      descricao_transacao: description,
      dt_transacao: toIsoFromDatetimeLocal(input?.dt_transacao),
    },
  }
}
