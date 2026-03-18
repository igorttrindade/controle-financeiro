import { describe, expect, it } from 'vitest'
import {
  aggregateLineSeriesWithPreviousPeriod,
  aggregateMonthlySeries,
  buildInsights,
  computeAverageExpense,
  computeDashboardKpis,
  computeGoalProgress,
  computeSavingsRate,
  computeTopCategory,
  computeVariationPercent,
  filterTransactionsByPeriod,
} from './dashboardUtils'

const BASE_DATE = new Date('2026-02-24T10:00:00Z')

describe('computeDashboardKpis', () => {
  it('returns zeros for empty list', () => {
    expect(computeDashboardKpis([], BASE_DATE)).toEqual({
      balance: 0,
      monthlyIncome: 0,
      monthlyExpense: 0,
    })
  })

  it('calculates values for income only', () => {
    const transactions = [
      { data: '2026-02-10 10:00:00', tipo: 'entrada', valor: 100 },
      { data: '2026-02-11 10:00:00', tipo: 'receita', valor: 200 },
    ]
    expect(computeDashboardKpis(transactions, BASE_DATE)).toEqual({
      balance: 300,
      monthlyIncome: 300,
      monthlyExpense: 0,
    })
  })

  it('calculates values for expense only', () => {
    const transactions = [
      { data: '2026-02-10 10:00:00', tipo: 'despesa', valor: 120 },
      { data: '2026-02-11 10:00:00', tipo: 'saida', valor: 80 },
    ]
    expect(computeDashboardKpis(transactions, BASE_DATE)).toEqual({
      balance: -200,
      monthlyIncome: 0,
      monthlyExpense: 200,
    })
  })

  it('ignores unknown types in monthly totals while preserving global math', () => {
    const transactions = [
      { data: '2026-02-10 10:00:00', tipo: 'entrada', valor: 300 },
      { data: '2026-02-11 10:00:00', tipo: 'unknown', valor: 500 },
      { data: '2026-01-11 10:00:00', tipo: 'despesa', valor: 100 },
    ]
    expect(computeDashboardKpis(transactions, BASE_DATE)).toEqual({
      balance: 200,
      monthlyIncome: 300,
      monthlyExpense: 0,
    })
  })
})

describe('filterTransactionsByPeriod', () => {
  const transactions = [
    { data: '2026-02-24T08:00:00Z', tipo: 'entrada', valor: 100 },
    { data: '2026-02-01T08:00:00Z', tipo: 'saida', valor: 60 },
    { data: '2025-12-15T08:00:00Z', tipo: 'saida', valor: 20 },
  ]

  it('filters 7d correctly', () => {
    const result = filterTransactionsByPeriod(transactions, '7d', BASE_DATE)
    expect(result).toHaveLength(1)
  })

  it('filters 3m correctly', () => {
    const result = filterTransactionsByPeriod(transactions, '3m', BASE_DATE)
    expect(result).toHaveLength(3)
  })
})

describe('strategic metrics', () => {
  it('computes savings rate', () => {
    expect(computeSavingsRate({ income: 1000, expense: 700 })).toBeCloseTo(30)
    expect(computeSavingsRate({ income: 0, expense: 100 })).toBe(0)
  })

  it('computes variation including division by zero fallback', () => {
    expect(computeVariationPercent(120, 100)).toBeCloseTo(20)
    expect(computeVariationPercent(0, 0)).toBe(0)
    expect(computeVariationPercent(10, 0)).toBe(100)
  })

  it('computes average expense and top category', () => {
    const transactions = [
      { data: '2026-02-20T10:00:00Z', tipo: 'despesa', valor: 100, nome: 'Mercado' },
      { data: '2026-02-21T10:00:00Z', tipo: 'saida', valor: 60, nome: 'Mercado' },
      { data: '2026-02-22T10:00:00Z', tipo: 'despesa', valor: 50, nome: 'Transporte' },
      { data: '2026-02-23T10:00:00Z', tipo: 'entrada', valor: 500, nome: 'Salário' },
    ]

    expect(computeAverageExpense(transactions, BASE_DATE, '30d')).toBeCloseTo(70)
    expect(computeTopCategory(transactions, BASE_DATE, '30d')).toEqual({
      name: 'Mercado',
      amount: 160,
      count: 2,
    })
  })

  it('computes goal progress', () => {
    expect(computeGoalProgress({ monthlyExpense: 500, monthlyGoal: 1000 })).toEqual({
      isConfigured: true,
      percent: 50,
      remaining: 500,
      isExceeded: false,
    })

    expect(computeGoalProgress({ monthlyExpense: 1200, monthlyGoal: 1000 })).toEqual({
      isConfigured: true,
      percent: 100,
      remaining: 0,
      isExceeded: true,
    })

    expect(computeGoalProgress({ monthlyExpense: 1200, monthlyGoal: 0 })).toEqual({
      isConfigured: false,
      percent: 0,
      remaining: 0,
      isExceeded: false,
    })
  })

  it('builds insights from metrics', () => {
    const insights = buildInsights({
      kpis: { income: 1000, expense: 600, balance: 400 },
      variation: 10,
      savingsRate: 40,
      topCategory: { name: 'Mercado', amount: 300, count: 3 },
      goalProgress: { isConfigured: true, isExceeded: false, percent: 60, remaining: 400 },
    })

    expect(insights.length).toBeGreaterThan(0)
    expect(insights[0]).toHaveProperty('id')
    expect(insights[0]).toHaveProperty('title')
  })
})

describe('series aggregation', () => {
  it('builds six months with grouped income/expense values', () => {
    const transactions = [
      { data: '2025-10-10 10:00:00', tipo: 'entrada', valor: 100 },
      { data: '2025-11-10 10:00:00', tipo: 'despesa', valor: 50 },
      { data: '2025-12-10 10:00:00', tipo: 'entrada', valor: 200 },
      { data: '2026-01-10 10:00:00', tipo: 'saida', valor: 75 },
      { data: '2026-02-10 10:00:00', tipo: 'receita', valor: 300 },
      { data: '2026-02-20 10:00:00', tipo: 'expense', valor: 20 },
      { data: '2025-08-10 10:00:00', tipo: 'entrada', valor: 999 },
    ]

    const series = aggregateMonthlySeries(transactions, BASE_DATE, 6)

    expect(series.labels).toHaveLength(6)
    expect(series.income).toEqual([0, 100, 0, 200, 0, 300])
    expect(series.expense).toEqual([0, 0, 50, 0, 75, 20])
  })

  it('builds line series with previous period', () => {
    const transactions = [
      { data: '2026-02-20T10:00:00Z', tipo: 'entrada', valor: 100 },
      { data: '2026-02-21T10:00:00Z', tipo: 'despesa', valor: 60 },
      { data: '2026-02-14T10:00:00Z', tipo: 'entrada', valor: 30 },
      { data: '2026-02-15T10:00:00Z', tipo: 'despesa', valor: 20 },
    ]

    const series = aggregateLineSeriesWithPreviousPeriod(transactions, '7d', BASE_DATE)

    expect(series.labels).toHaveLength(7)
    expect(series.income).toHaveLength(7)
    expect(series.previousIncome).toHaveLength(7)
    expect(series.totals.balance).toBe(40)
    expect(series.previousTotals.balance).toBe(10)
  })
})
