<template>
  <div class="min-h-screen bg-base-200 text-base-content">
    <Navbar />

    <main class="mx-auto w-full max-w-4xl px-4 pb-10 pt-24 md:px-8">
      <div class="mb-6 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 class="text-3xl font-bold">Editar transação</h1>
          <p class="text-sm text-base-content/70">Corrija os dados do lançamento sem perder histórico.</p>
        </div>

        <button class="btn btn-ghost" type="button" @click="goBack">Cancelar</button>
      </div>

      <div v-if="loadError" class="alert alert-error mb-4">
        <span>{{ loadError }}</span>
      </div>

      <div v-if="isLoadingData" class="card border border-base-300 bg-base-100 shadow-card">
        <div class="card-body gap-3">
          <div class="skeleton h-5 w-52"></div>
          <div class="skeleton h-12 w-full"></div>
          <div class="skeleton h-12 w-full"></div>
        </div>
      </div>

      <form v-else class="card border border-base-300 bg-base-100 shadow-card" @submit.prevent="handleSubmit">
        <div class="card-body grid gap-4 md:grid-cols-2">
          <label class="form-control">
            <div class="label"><span class="label-text">Tipo da operação</span></div>
            <select v-model="form.tipo_operacao" class="select select-bordered w-full" @change="resetSelectedOperation">
              <option value="entrada">Entrada</option>
              <option value="despesa">Despesa</option>
            </select>
            <div v-if="errors.tipo_operacao" class="label"><span class="label-text-alt text-error">{{ errors.tipo_operacao }}</span></div>
          </label>

          <div class="form-control">
            <div class="label justify-between">
              <span class="label-text">Operação</span>
              <button class="btn btn-link btn-xs px-0" type="button" @click="openOperationModal">+ Nova operação</button>
            </div>

            <input
              v-model="operationSearch"
              type="text"
              class="input input-bordered mb-2"
              placeholder="Buscar operação"
            />

            <select v-model="form.id_operacao" class="select select-bordered w-full">
              <option value="">Selecione uma operação</option>
              <option v-for="operation in filteredOperations" :key="operation.id_operacao" :value="String(operation.id_operacao)">
                {{ operation.nome_operacao }}
              </option>
            </select>

            <div v-if="errors.nome_operacao" class="label"><span class="label-text-alt text-error">{{ errors.nome_operacao }}</span></div>
          </div>

          <label class="form-control">
            <div class="label"><span class="label-text">Valor (R$)</span></div>
            <input
              v-model="form.valor_transacao"
              type="text"
              class="input input-bordered"
              inputmode="decimal"
              placeholder="0,00"
            />
            <div v-if="errors.valor_transacao" class="label"><span class="label-text-alt text-error">{{ errors.valor_transacao }}</span></div>
          </label>

          <label class="form-control">
            <div class="label"><span class="label-text">Data da transação</span></div>
            <input v-model="form.dt_transacao" type="datetime-local" class="input input-bordered" />
          </label>

          <label class="form-control md:col-span-2">
            <div class="label"><span class="label-text">Descrição</span></div>
            <textarea
              v-model="form.descricao_transacao"
              class="textarea textarea-bordered min-h-24"
              placeholder="Descreva a transação"
            ></textarea>
            <div v-if="errors.descricao_transacao" class="label"><span class="label-text-alt text-error">{{ errors.descricao_transacao }}</span></div>
          </label>

          <div class="md:col-span-2 flex justify-end gap-2">
            <button class="btn btn-ghost" type="button" @click="goBack">Cancelar</button>
            <button class="btn btn-primary" :class="{ loading: isSubmitting }" :disabled="isSubmitting" type="submit">
              {{ isSubmitting ? 'Salvando...' : 'Salvar alterações' }}
            </button>
          </div>
        </div>
      </form>

      <dialog ref="operationModalRef" class="modal">
        <div class="modal-box">
          <h3 class="text-lg font-semibold">Criar nova operação</h3>

          <div class="mt-4 grid gap-3">
            <label class="form-control">
              <div class="label"><span class="label-text">Tipo</span></div>
              <select v-model="newOperation.tipo_operacao" class="select select-bordered">
                <option value="entrada">Entrada</option>
                <option value="despesa">Despesa</option>
              </select>
            </label>

            <label class="form-control">
              <div class="label"><span class="label-text">Nome da operação</span></div>
              <input v-model="newOperation.nome_operacao" class="input input-bordered" type="text" placeholder="Ex: Mercado" />
            </label>

            <p v-if="operationModalError" class="text-sm text-error">{{ operationModalError }}</p>
          </div>

          <div class="modal-action">
            <button class="btn btn-ghost" type="button" @click="closeOperationModal">Fechar</button>
            <button class="btn btn-primary" type="button" :class="{ loading: isCreatingOperation }" :disabled="isCreatingOperation" @click="handleCreateOperation">
              {{ isCreatingOperation ? 'Criando...' : 'Criar operação' }}
            </button>
          </div>
        </div>
      </dialog>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '@/components/layout/Navbar.vue'
import { useNotifications } from '@/composables/useNotifications'
import {
  createOperation,
  getOperations,
  getTransactionById,
  updateTransaction,
} from '@/services/transactions/transaction.service'
import { toDatetimeLocalValue, validateTransactionInput } from '@/utils/transactionFormUtils'

const route = useRoute()
const router = useRouter()
const { addNotification } = useNotifications()

const transactionId = Number(route.params.id)
const isLoadingData = ref(true)
const isSubmitting = ref(false)
const isCreatingOperation = ref(false)
const loadError = ref('')
const operationModalError = ref('')
const operationSearch = ref('')
const operations = ref([])
const errors = ref({})
const operationModalRef = ref(null)

const form = ref({
  tipo_operacao: 'entrada',
  id_operacao: '',
  valor_transacao: '',
  descricao_transacao: '',
  dt_transacao: toDatetimeLocalValue(new Date()),
})

const newOperation = ref({
  tipo_operacao: 'entrada',
  nome_operacao: '',
})

const filteredOperations = computed(() => {
  const term = operationSearch.value.trim().toLowerCase()
  return operations.value.filter((operation) => {
    if (operation.tipo_operacao !== form.value.tipo_operacao) return false
    if (!term) return true
    return operation.nome_operacao.toLowerCase().includes(term)
  })
})

function selectedOperationName() {
  const selected = operations.value.find((item) => String(item.id_operacao) === String(form.value.id_operacao))
  return selected?.nome_operacao || ''
}

function formatNumberToInput(value) {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return ''
  return numeric.toFixed(2).replace('.', ',')
}

function parseDateToDatetimeLocal(rawDate) {
  if (!rawDate) return toDatetimeLocalValue(new Date())
  const normalized = String(rawDate).replace(' ', 'T')
  return toDatetimeLocalValue(new Date(normalized))
}

function resetSelectedOperation() {
  form.value.id_operacao = ''
}

function goBack() {
  router.push('/dashboard')
}

function handleUnauthorized(error) {
  if (error?.response?.status !== 401) return false
  localStorage.removeItem('token')
  localStorage.removeItem('userId')
  router.push('/login')
  return true
}

async function loadFormData() {
  isLoadingData.value = true
  loadError.value = ''
  try {
    const [operationsResponse, transactionResponse] = await Promise.all([
      getOperations(),
      getTransactionById(transactionId),
    ])

    operations.value = Array.isArray(operationsResponse) ? operationsResponse : []

    const normalizedType = String(transactionResponse.tipo || '').toLowerCase()
    form.value.tipo_operacao = normalizedType === 'entrada' ? 'entrada' : 'despesa'
    form.value.id_operacao = String(transactionResponse.id_operacao)
    form.value.valor_transacao = formatNumberToInput(transactionResponse.valor)
    form.value.descricao_transacao = transactionResponse.descricao || ''
    form.value.dt_transacao = parseDateToDatetimeLocal(transactionResponse.data)
  } catch (error) {
    if (handleUnauthorized(error)) return
    loadError.value = error?.response?.data?.error || 'Não foi possível carregar os dados da transação.'
  } finally {
    isLoadingData.value = false
  }
}

function openOperationModal() {
  operationModalError.value = ''
  newOperation.value.tipo_operacao = form.value.tipo_operacao
  newOperation.value.nome_operacao = ''
  operationModalRef.value?.showModal()
}

function closeOperationModal() {
  operationModalRef.value?.close()
}

async function handleCreateOperation() {
  operationModalError.value = ''
  const name = String(newOperation.value.nome_operacao || '').trim()
  if (name.length < 2 || name.length > 120) {
    operationModalError.value = 'O nome da operação deve ter entre 2 e 120 caracteres.'
    return
  }

  isCreatingOperation.value = true
  try {
    const created = await createOperation({
      nome_operacao: name,
      tipo_operacao: newOperation.value.tipo_operacao,
    })

    const operation = {
      id_operacao: created.id_operacao,
      nome_operacao: created.nome_operacao,
      tipo_operacao: created.tipo_operacao,
    }

    const exists = operations.value.some((item) => item.id_operacao === operation.id_operacao)
    if (!exists) {
      operations.value.push(operation)
    }

    form.value.tipo_operacao = operation.tipo_operacao
    form.value.id_operacao = String(operation.id_operacao)
    addNotification('Operação disponível para uso.', 'success')
    closeOperationModal()
  } catch (error) {
    if (handleUnauthorized(error)) return
    operationModalError.value = error?.response?.data?.error || 'Não foi possível criar a operação.'
  } finally {
    isCreatingOperation.value = false
  }
}

async function handleSubmit() {
  errors.value = {}

  const validation = validateTransactionInput({
    tipo_operacao: form.value.tipo_operacao,
    nome_operacao: selectedOperationName(),
    valor_transacao: form.value.valor_transacao,
    descricao_transacao: form.value.descricao_transacao,
    dt_transacao: form.value.dt_transacao,
  })

  if (!form.value.id_operacao) {
    validation.errors.nome_operacao = 'Selecione uma operação ou crie uma nova.'
    validation.isValid = false
  }

  if (!validation.isValid) {
    errors.value = validation.errors
    return
  }

  isSubmitting.value = true
  try {
    await updateTransaction(transactionId, {
      id_operacao: Number(form.value.id_operacao),
      valor_transacao: validation.normalized.valor_transacao,
      descricao_transacao: validation.normalized.descricao_transacao,
      dt_transacao: validation.normalized.dt_transacao,
    })

    addNotification('Transação atualizada com sucesso.', 'success')
    router.push('/dashboard')
  } catch (error) {
    if (handleUnauthorized(error)) return
    addNotification(error?.response?.data?.error || 'Não foi possível atualizar a transação.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  if (!Number.isInteger(transactionId) || transactionId <= 0) {
    loadError.value = 'ID de transação inválido.'
    isLoadingData.value = false
    return
  }

  loadFormData()
})
</script>
