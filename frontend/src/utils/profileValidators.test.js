import { describe, expect, it } from 'vitest'
import {
  validateAvatarFile,
  validateEmailChange,
  validatePasswordChange,
  validateProfileBasics,
} from './profileValidators'

describe('validateProfileBasics', () => {
  it('validates valid profile', () => {
    const result = validateProfileBasics({ name_user: 'Igor', tel_user: '11999999999' })
    expect(result.isValid).toBe(true)
    expect(result.normalized.name_user).toBe('Igor')
  })

  it('rejects invalid name/phone', () => {
    const result = validateProfileBasics({ name_user: 'A', tel_user: '12' })
    expect(result.isValid).toBe(false)
    expect(result.errors.name_user).toBeTruthy()
    expect(result.errors.tel_user).toBeTruthy()
  })
})

describe('validateEmailChange', () => {
  it('accepts valid email', () => {
    const result = validateEmailChange('TESTE@EMAIL.COM')
    expect(result.isValid).toBe(true)
    expect(result.value).toBe('teste@email.com')
  })

  it('rejects invalid email', () => {
    const result = validateEmailChange('invalido')
    expect(result.isValid).toBe(false)
  })
})

describe('validatePasswordChange', () => {
  it('accepts strong password', () => {
    const result = validatePasswordChange('Senha1234')
    expect(result.isValid).toBe(true)
  })

  it('rejects weak password', () => {
    const result = validatePasswordChange('1234567')
    expect(result.isValid).toBe(false)
  })
})

describe('validateAvatarFile', () => {
  it('rejects missing file', () => {
    expect(validateAvatarFile(null).isValid).toBe(false)
  })

  it('accepts valid file metadata', () => {
    const file = { type: 'image/png', size: 10_000 }
    expect(validateAvatarFile(file).isValid).toBe(true)
  })

  it('rejects oversize file', () => {
    const file = { type: 'image/png', size: 3 * 1024 * 1024 }
    expect(validateAvatarFile(file).isValid).toBe(false)
  })
})
