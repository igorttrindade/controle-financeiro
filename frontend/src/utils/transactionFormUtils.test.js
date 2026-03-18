import { describe, expect, it } from 'vitest'
import {
  normalizeOperationType,
  parseCurrencyToNumber,
  toDatetimeLocalValue,
  toIsoFromDatetimeLocal,
  validateTransactionInput,
} from './transactionFormUtils'

describe('normalizeOperationType', () => {
  it('normalizes income aliases', () => {
    expect(normalizeOperationType('entrada')).toBe('entrada')
    expect(normalizeOperationType('RECEITA')).toBe('entrada')
    expect(normalizeOperationType('income')).toBe('entrada')
  })

  it('normalizes expense aliases', () => {
    expect(normalizeOperationType('despesa')).toBe('despesa')
    expect(normalizeOperationType('saida')).toBe('despesa')
    expect(normalizeOperationType('expense')).toBe('despesa')
  })

  it('returns null for unknown value', () => {
    expect(normalizeOperationType('xpto')).toBeNull()
  })
})

describe('parseCurrencyToNumber', () => {
  it('parses brazilian format values', () => {
    expect(parseCurrencyToNumber('1.234,56')).toBeCloseTo(1234.56)
    expect(parseCurrencyToNumber('100')).toBe(100)
  })

  it('returns NaN for invalid values', () => {
    expect(Number.isNaN(parseCurrencyToNumber('abc'))).toBe(true)
  })
})

describe('datetime helpers', () => {
  it('formats datetime-local default', () => {
    expect(toDatetimeLocalValue(new Date('2026-02-25T14:30:00'))).toBe('2026-02-25T14:30')
  })

  it('converts datetime-local to iso', () => {
    const iso = toIsoFromDatetimeLocal('2026-02-25T14:30')
    expect(typeof iso).toBe('string')
    expect(iso).toContain('2026-02-25')
  })
})

describe('validateTransactionInput', () => {
  it('accepts valid input', () => {
    const result = validateTransactionInput({
      tipo_operacao: 'entrada',
      nome_operacao: 'Freelance',
      valor_transacao: '150,90',
      descricao_transacao: 'Projeto extra',
      dt_transacao: '2026-02-25T14:30',
    })

    expect(result.isValid).toBe(true)
    expect(result.normalized.valor_transacao).toBeCloseTo(150.9)
    expect(result.normalized.nome_operacao).toBe('Freelance')
  })

  it('returns errors for invalid input', () => {
    const result = validateTransactionInput({
      tipo_operacao: 'invalido',
      nome_operacao: 'A',
      valor_transacao: '0',
      descricao_transacao: 'x',
      dt_transacao: 'invalid-date',
    })

    expect(result.isValid).toBe(false)
    expect(result.errors.tipo_operacao).toBeTruthy()
    expect(result.errors.nome_operacao).toBeTruthy()
    expect(result.errors.valor_transacao).toBeTruthy()
    expect(result.errors.descricao_transacao).toBeTruthy()
    expect(result.normalized.dt_transacao).toBeNull()
  })
})
