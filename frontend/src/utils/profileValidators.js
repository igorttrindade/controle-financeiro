const AVATAR_MAX_BYTES = 2 * 1024 * 1024
const ALLOWED_MIME_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp'])

export function validateProfileBasics({ name_user, tel_user }) {
  const errors = {}
  const normalizedName = String(name_user || '').trim()
  const normalizedTel = String(tel_user || '').trim()

  if (normalizedName.length < 2 || normalizedName.length > 120) {
    errors.name_user = 'Nome deve ter entre 2 e 120 caracteres.'
  }

  if (normalizedTel && !/^[0-9+()\-\s]{8,20}$/.test(normalizedTel)) {
    errors.tel_user = 'Telefone inválido.'
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
    normalized: {
      name_user: normalizedName,
      tel_user: normalizedTel,
    },
  }
}

export function validateEmailChange(newEmail) {
  const email = String(newEmail || '').trim().toLowerCase()
  if (!email || !email.includes('@')) {
    return { isValid: false, error: 'Informe um e-mail válido.' }
  }
  return { isValid: true, value: email }
}

export function validatePasswordChange(newPassword) {
  const password = String(newPassword || '')
  const isStrong = /^(?=.*[A-Za-z])(?=.*\d).{8,}$/.test(password)
  if (!isStrong) {
    return {
      isValid: false,
      error: 'Senha deve ter no mínimo 8 caracteres, com letras e números.',
    }
  }
  return { isValid: true, value: password }
}

export function validateAvatarFile(file) {
  if (!file) {
    return { isValid: false, error: 'Selecione uma imagem.' }
  }

  if (!ALLOWED_MIME_TYPES.has(file.type)) {
    return { isValid: false, error: 'Use apenas JPG, PNG ou WebP.' }
  }

  if (file.size > AVATAR_MAX_BYTES) {
    return { isValid: false, error: 'A imagem deve ter no máximo 2MB.' }
  }

  return { isValid: true }
}
