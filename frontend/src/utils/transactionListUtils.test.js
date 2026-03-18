import { describe, expect, it } from 'vitest'
import {
  filterTransactionsByCustomRange,
  filterTransactionsByPresetPeriod,
  paginateTransactions,
  searchTransactions,
  sortTransactions,
} from './transactionListUtils'

const NOW = new Date('2026-03-03T10:00:00')
const BASE = [
  { id: 1, data: '2026-03-03 09:00:00', nome: 'Salário', tipo: 'entrada', valor: 5000, descricao: 'Pagamento' },
  { id: 2, data: '2026-03-02 10:00:00', nome: 'Mercado', tipo: 'despesa', valor: 230, descricao: 'Compras' },
  { id: 3, data: '2026-02-15 13:00:00', nome: 'Aluguel', tipo: 'despesa', valor: 1200, descricao: 'Mensal' },
  { id: 4, data: '2026-01-10 12:00:00', nome: 'Freela', tipo: 'entrada', valor: 800, descricao: 'Projeto' },
]

describe('filterTransactionsByPresetPeriod', () => {
  it('filters by hoje', () => {
    const result = filterTransactionsByPresetPeriod(BASE, 'hoje', NOW)
    expect(result.map((item) => item.id)).toEqual([1])
  })

  it('filters by este_mes', () => {
    const result = filterTransactionsByPresetPeriod(BASE, 'este_mes', NOW)
    expect(result.map((item) => item.id)).toEqual([1, 2])
  })

  it('filters by mes_anterior', () => {
    const result = filterTransactionsByPresetPeriod(BASE, 'mes_anterior', NOW)
    expect(result.map((item) => item.id)).toEqual([3])
  })
})

describe('filterTransactionsByCustomRange', () => {
  it('filters by date range', () => {
    const result = filterTransactionsByCustomRange(BASE, '2026-03-01', '2026-03-03')
    expect(result.map((item) => item.id)).toEqual([1, 2])
  })

  it('returns empty when invalid range', () => {
    const result = filterTransactionsByCustomRange(BASE, '2026-03-05', '2026-03-01')
    expect(result).toEqual([])
  })
})

describe('searchTransactions', () => {
  it('searches by nome and descricao', () => {
    expect(searchTransactions(BASE, 'merc').map((item) => item.id)).toEqual([2])
    expect(searchTransactions(BASE, 'mensal').map((item) => item.id)).toEqual([3])
  })
})

describe('sortTransactions', () => {
  it('sorts by date desc default', () => {
    expect(sortTransactions(BASE).map((item) => item.id)).toEqual([1, 2, 3, 4])
  })

  it('sorts by value asc', () => {
    expect(sortTransactions(BASE, 'valor_asc').map((item) => item.id)).toEqual([2, 4, 3, 1])
  })
})

describe('paginateTransactions', () => {
  it('paginates and clamps page', () => {
    const result = paginateTransactions(BASE, 3, 2)
    expect(result.page).toBe(2)
    expect(result.totalPages).toBe(2)
    expect(result.items.map((item) => item.id)).toEqual([3, 4])
  })
})
