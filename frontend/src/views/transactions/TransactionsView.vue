<template>
  <div class="min-h-screen bg-base-200 text-base-content">
    <Navbar />

    <main class="mx-auto w-full max-w-7xl px-4 pb-12 pt-24 sm:px-6">
      <header class="rounded-2xl border border-base-300 bg-base-100 p-6 shadow-sm">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 class="text-3xl font-bold">Transações</h1>
            <p class="mt-1 text-sm text-base-content/70">Gerencie seus lançamentos com filtros, busca e paginação.</p>
          </div>

          <button class="btn btn-primary" type="button" @click="openCreateModal">Nova transação</button>
        </div>

        <div class="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
          <label class="form-control">
            <span class="label-text text-xs text-base-content/70">Período</span>
            <select v-model="filters.periodPreset" class="select select-bordered select-sm">
              <option value="hoje">Hoje</option>
              <option value="este_mes">Este mês</option>
              <option value="mes_anterior">Mês anterior</option>
              <option value="custom">Personalizado</option>
            </select>
          </label>

          <label v-if="filters.periodPreset === 'custom'" class="form-control">
            <span class="label-text text-xs text-base-content/70">Data inicial</span>
            <input v-model="filters.startDate" type="date" class="input input-bordered input-sm" />
          </label>

          <label v-if="filters.periodPreset === 'custom'" class="form-control">
            <span class="label-text text-xs text-base-content/70">Data final</span>
            <input v-model="filters.endDate" type="date" class="input input-bordered input-sm" />
          </label>

          <label class="form-control" :class="filters.periodPreset === 'custom' ? 'xl:col-span-1' : 'xl:col-span-2'">
            <span class="label-text text-xs text-base-content/70">Busca</span>
            <input
              v-model="filters.search"
              type="text"
              class="input input-bordered input-sm"
              placeholder="Buscar por operação ou descrição"
            />
          </label>

          <label class="form-control">
            <span class="label-text text-xs text-base-content/70">Ordenação</span>
            <select v-model="filters.sortBy" class="select select-bordered select-sm">
              <option value="data_desc">Mais recentes</option>
              <option value="data_asc">Mais antigas</option>
              <option value="valor_desc">Maior valor</option>
              <option value="valor_asc">Menor valor</option>
            </select>
          </label>
        </div>
      </header>

      <section v-if="loadError" class="mt-6">
        <div class="alert alert-error rounded-xl">
          <span>{{ loadError }}</span>
          <button class="btn btn-sm" @click="loadData">Tentar novamente</button>
        </div>
      </section>

      <section class="mt-6 rounded-2xl border border-base-300 bg-base-100 p-4 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <p class="text-sm text-base-content/70">
            {{ pagination.totalItems }} lançamento(s) encontrado(s)
          </p>
          <p class="text-xs text-base-content/60">Página {{ pagination.page }} de {{ pagination.totalPages }}</p>
        </div>

        <div v-if="isLoading" class="space-y-2">
          <div class="skeleton h-12 w-full"></div>
          <div class="skeleton h-12 w-full"></div>
          <div class="skeleton h-12 w-full"></div>
        </div>

        <div v-else-if="pagination.totalItems === 0" class="rounded-xl border border-dashed border-base-300 p-6 text-center">
          <p class="font-medium">Nenhuma transação encontrada</p>
          <p class="text-sm text-base-content/70">Ajuste os filtros ou crie um novo lançamento.</p>
        </div>

        <template v-else>
          <div class="hidden overflow-x-auto md:block">
            <table class="table table-zebra">
              <thead>
                <tr>
                  <th>Data</th>
                  <th>Operação</th>
                  <th>Tipo</th>
                  <th>Valor</th>
                  <th>Descrição</th>
                  <th class="text-right">Ações</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in pagination.items" :key="item.id">
                  <td>{{ formatDate(item.data) }}</td>
                  <td>{{ item.nome || 'Transação' }}</td>
                  <td>
                    <span class="badge" :class="badgeClass(item.tipo)">{{ formatType(item.tipo) }}</span>
                  </td>
                  <td :class="valueClass(item.tipo)">{{ formatCurrency(item.valor) }}</td>
                  <td>{{ item.descricao || '-' }}</td>
                  <td>
                    <div class="flex justify-end gap-2">
                      <button class="btn btn-ghost btn-xs" @click="openEditModal(item)">Editar</button>
                      <button
                        class="btn btn-ghost btn-xs text-error"
                        :class="{ loading: deletingId === item.id }"
                        :disabled="deletingId === item.id"
                        @click="handleDelete(item.id)"
                      >
                        Excluir
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="space-y-3 md:hidden">
            <article v-for="item in pagination.items" :key="`card-${item.id}`" class="rounded-xl border border-base-300 p-4">
              <div class="flex items-center justify-between gap-2">
                <p class="font-medium">{{ item.nome || 'Transação' }}</p>
                <span class="badge" :class="badgeClass(item.tipo)">{{ formatType(item.tipo) }}</span>
              </div>
              <p class="mt-1 text-xs text-base-content/70">{{ formatDate(item.data) }}</p>
              <p class="mt-2 text-sm" :class="valueClass(item.tipo)">{{ formatCurrency(item.valor) }}</p>
              <p class="mt-1 text-sm text-base-content/70">{{ item.descricao || 'Sem descrição' }}</p>
              <div class="mt-3 flex gap-2">
                <button class="btn btn-outline btn-xs flex-1" @click="openEditModal(item)">Editar</button>
                <button
                  class="btn btn-outline btn-xs flex-1 text-error"
                  :class="{ loading: deletingId === item.id }"
                  :disabled="deletingId === item.id"
                  @click="handleDelete(item.id)"
                >
                  Excluir
                </button>
              </div>
            </article>
          </div>

          <div class="mt-4 flex items-center justify-end gap-2">
            <button class="btn btn-sm" :disabled="!pagination.hasPrevious" @click="changePage(pagination.page - 1)">Anterior</button>
            <button class="btn btn-sm" :disabled="!pagination.hasNext" @click="changePage(pagination.page + 1)">Próxima</button>
          </div>
        </template>
      </section>
    </main>

    <dialog ref="transactionModalRef" class="modal">
      <div class="modal-box max-w-2xl">
        <h3 class="text-lg font-semibold">{{ modalMode === 'create' ? 'Nova transação' : 'Editar transação' }}</h3>

        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <label class="form-control">
            <div class="label"><span class="label-text">Tipo da operação</span></div>
            <select v-model="form.tipo_operacao" class="select select-bordered" @change="resetSelectedOperation">
              <option value="entrada">Entrada</option>
              <option value="despesa">Despesa</option>
            </select>
            <span v-if="formErrors.tipo_operacao" class="label-text-alt text-error">{{ formErrors.tipo_operacao }}</span>
          </label>

          <div class="form-control">
            <div class="label justify-between">
              <span class="label-text">Operação</span>
              <button class="btn btn-link btn-xs px-0" type="button" @click="openOperationModal">+ Nova operação</button>
            </div>
            <input v-model="operationSearch" type="text" class="input input-bordered mb-2" placeholder="Buscar operação" />
            <select v-model="form.id_operacao" class="select select-bordered">
              <option value="">Selecione uma operação</option>
              <option v-for="operation in filteredOperations" :key="operation.id_operacao" :value="String(operation.id_operacao)">
                {{ operation.nome_operacao }}
              </option>
            </select>
            <span v-if="formErrors.nome_operacao" class="label-text-alt text-error">{{ formErrors.nome_operacao }}</span>
          </div>

          <label class="form-control">
            <div class="label"><span class="label-text">Valor (R$)</span></div>
            <input v-model="form.valor_transacao" type="text" class="input input-bordered" inputmode="decimal" placeholder="0,00" />
            <span v-if="formErrors.valor_transacao" class="label-text-alt text-error">{{ formErrors.valor_transacao }}</span>
          </label>

          <label class="form-control">
            <div class="label"><span class="label-text">Data da transação</span></div>
            <input v-model="form.dt_transacao" type="datetime-local" class="input input-bordered" />
          </label>

          <label class="form-control md:col-span-2">
            <div class="label"><span class="label-text">Descrição</span></div>
            <textarea v-model="form.descricao_transacao" class="textarea textarea-bordered min-h-24"></textarea>
            <span v-if="formErrors.descricao_transacao" class="label-text-alt text-error">{{ formErrors.descricao_transacao }}</span>
          </label>
        </div>

        <div class="modal-action">
          <button class="btn btn-ghost" type="button" @click="closeTransactionModal">Cancelar</button>
          <button class="btn btn-primary" :class="{ loading: isSubmitting }" :disabled="isSubmitting" @click="submitForm">
            {{ isSubmitting ? 'Salvando...' : modalMode === 'create' ? 'Criar transação' : 'Salvar alterações' }}
          </button>
        </div>
      </div>
    </dialog>

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
            <div class="label"><span class="label-text">Nome</span></div>
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
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '@/components/layout/Navbar.vue'
import { useNotifications } from '@/composables/useNotifications'
import {
  createOperation,
  createTransaction,
  deleteTransaction,
  getOperations,
  getTransactionById,
  getTransactions,
  updateTransaction,
} from '@/services/transactions/transaction.service'
import { normalizeType, parseTransactionDate } from '@/utils/dashboardUtils'
import {
  filterTransactionsByCustomRange,
  filterTransactionsByPresetPeriod,
  paginateTransactions,
  searchTransactions,
  sortTransactions,
} from '@/utils/transactionListUtils'
import { toDatetimeLocalValue, validateTransactionInput } from '@/utils/transactionFormUtils'

const PAGE_SIZE = 10

const router = useRouter()
const { addNotification } = useNotifications()

const isLoading = ref(true)
const isSubmitting = ref(false)
const isCreatingOperation = ref(false)
const loadError = ref('')
const deletingId = ref(null)

const transactions = ref([])
const operations = ref([])

const filters = ref({
  periodPreset: 'este_mes',
  startDate: '',
  endDate: '',
  search: '',
  sortBy: 'data_desc',
  page: 1,
})

const modalMode = ref('create')
const editingTransactionId = ref(null)
const transactionModalRef = ref(null)
const operationModalRef = ref(null)
const operationSearch = ref('')
const formErrors = ref({})
const operationModalError = ref('')

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

const filteredByPeriod = computed(() => {
  if (filters.value.periodPreset === 'custom') {
    return filterTransactionsByCustomRange(
      transactions.value,
      filters.value.startDate,
      filters.value.endDate,
    )
  }

  return filterTransactionsByPresetPeriod(
    transactions.value,
    filters.value.periodPreset,
    new Date(),
  )
})

const searchedTransactions = computed(() => searchTransactions(filteredByPeriod.value, filters.value.search))
const sortedTransactions = computed(() => sortTransactions(searchedTransactions.value, filters.value.sortBy))

const pagination = computed(() =>
  paginateTransactions(sortedTransactions.value, filters.value.page, PAGE_SIZE),
)

const filteredOperations = computed(() => {
  const term = operationSearch.value.trim().toLowerCase()
  return operations.value.filter((operation) => {
    if (operation.tipo_operacao !== form.value.tipo_operacao) return false
    if (!term) return true
    return operation.nome_operacao.toLowerCase().includes(term)
  })
})

watch(
  () => [
    filters.value.periodPreset,
    filters.value.startDate,
    filters.value.endDate,
    filters.value.search,
    filters.value.sortBy,
  ],
  () => {
    filters.value.page = 1
  },
)

function sanitizeTransactions(source) {
  if (!Array.isArray(source)) return []

  return source
    .map((item) => {
      const date = parseTransactionDate(item?.data)
      return {
        id: Number(item?.id) || item?.id,
        nome: String(item?.nome || '').trim(),
        tipo: String(item?.tipo || '').trim(),
        valor: Number(item?.valor) || 0,
        descricao: String(item?.descricao || '').trim(),
        data: date ? date.toISOString() : null,
      }
    })
    .filter((item) => item.data)
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(value) || 0)
}

function formatDate(rawDate) {
  const date = parseTransactionDate(rawDate)
  if (!date) return 'Data inválida'
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(date)
}

function valueClass(type) {
  const normalized = normalizeType(type)
  if (normalized === 'income') return 'text-success'
  if (normalized === 'expense') return 'text-error'
  return 'text-base-content/80'
}

function badgeClass(type) {
  const normalized = normalizeType(type)
  if (normalized === 'income') return 'badge-success badge-outline'
  if (normalized === 'expense') return 'badge-error badge-outline'
  return 'badge-ghost'
}

function formatType(type) {
  const normalized = normalizeType(type)
  if (normalized === 'income') return 'Receita'
  if (normalized === 'expense') return 'Despesa'
  return 'Outro'
}

function selectedOperationName() {
  const selected = operations.value.find((item) => String(item.id_operacao) === String(form.value.id_operacao))
  return selected?.nome_operacao || ''
}

function resetSelectedOperation() {
  form.value.id_operacao = ''
}

function resetForm() {
  formErrors.value = {}
  form.value = {
    tipo_operacao: 'entrada',
    id_operacao: '',
    valor_transacao: '',
    descricao_transacao: '',
    dt_transacao: toDatetimeLocalValue(new Date()),
  }
  operationSearch.value = ''
}

function closeTransactionModal() {
  transactionModalRef.value?.close()
}

function openCreateModal() {
  modalMode.value = 'create'
  editingTransactionId.value = null
  resetForm()
  transactionModalRef.value?.showModal()
}

async function openEditModal(item) {
  const transactionId = Number(item?.id)
  if (!Number.isInteger(transactionId) || transactionId <= 0) return

  modalMode.value = 'edit'
  editingTransactionId.value = transactionId
  formErrors.value = {}

  try {
    const detail = await getTransactionById(transactionId)
    const normalizedType = String(detail?.tipo || '').toLowerCase()
    form.value = {
      tipo_operacao: normalizedType === 'entrada' ? 'entrada' : 'despesa',
      id_operacao: String(detail?.id_operacao || ''),
      valor_transacao: Number(detail?.valor || 0).toFixed(2).replace('.', ','),
      descricao_transacao: String(detail?.descricao || ''),
      dt_transacao: toDatetimeLocalValue(String(detail?.data || '').replace(' ', 'T')),
    }
    transactionModalRef.value?.showModal()
  } catch (error) {
    if (handleUnauthorized(error)) return
    addNotification('Não foi possível carregar os dados da transação.', 'error')
  }
}

function openOperationModal() {
  operationModalError.value = ''
  newOperation.value = {
    tipo_operacao: form.value.tipo_operacao,
    nome_operacao: '',
  }
  operationModalRef.value?.showModal()
}

function closeOperationModal() {
  operationModalRef.value?.close()
}

function handleUnauthorized(error) {
  if (error?.response?.status !== 401) return false
  localStorage.removeItem('token')
  localStorage.removeItem('userId')
  router.push('/login')
  return true
}

async function loadData() {
  isLoading.value = true
  loadError.value = ''

  try {
    const [transactionsResponse, operationsResponse] = await Promise.all([
      getTransactions(),
      getOperations(),
    ])
    transactions.value = sanitizeTransactions(transactionsResponse)
    operations.value = Array.isArray(operationsResponse) ? operationsResponse : []
  } catch (error) {
    if (handleUnauthorized(error)) return
    loadError.value = 'Não foi possível carregar as transações. Tente novamente.'
  } finally {
    isLoading.value = false
  }
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
    if (!exists) operations.value.push(operation)

    form.value.tipo_operacao = operation.tipo_operacao
    form.value.id_operacao = String(operation.id_operacao)
    closeOperationModal()
    addNotification('Operação criada com sucesso.', 'success')
  } catch (error) {
    if (handleUnauthorized(error)) return
    operationModalError.value = error?.response?.data?.error || 'Não foi possível criar a operação.'
  } finally {
    isCreatingOperation.value = false
  }
}

async function submitForm() {
  formErrors.value = {}

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
    formErrors.value = validation.errors
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      id_operacao: Number(form.value.id_operacao),
      valor_transacao: validation.normalized.valor_transacao,
      descricao_transacao: validation.normalized.descricao_transacao,
      dt_transacao: validation.normalized.dt_transacao,
    }

    if (modalMode.value === 'create') {
      await createTransaction(payload)
      addNotification('Transação criada com sucesso.', 'success')
    } else {
      await updateTransaction(editingTransactionId.value, payload)
      addNotification('Transação atualizada com sucesso.', 'success')
    }

    closeTransactionModal()
    await loadData()
  } catch (error) {
    if (handleUnauthorized(error)) return
    const message = error?.response?.data?.error || 'Não foi possível salvar a transação.'
    addNotification(message, 'error')
  } finally {
    isSubmitting.value = false
  }
}

async function handleDelete(id) {
  const transactionId = Number(id)
  if (!Number.isInteger(transactionId) || transactionId <= 0) return

  const confirmed = window.confirm('Deseja realmente excluir esta transação? Esta ação não pode ser desfeita.')
  if (!confirmed) return

  deletingId.value = transactionId
  try {
    await deleteTransaction(transactionId)
    transactions.value = transactions.value.filter((item) => Number(item.id) !== transactionId)
    addNotification('Transação excluída com sucesso.', 'success')
  } catch (error) {
    if (handleUnauthorized(error)) return
    addNotification('Não foi possível excluir a transação.', 'error')
  } finally {
    deletingId.value = null
  }
}

function changePage(nextPage) {
  filters.value.page = nextPage
}

onMounted(loadData)
</script>
