<template>
  <div>
    <v-card>
      <v-card-title class="text-h5">
        🗑️ База обрезков
      </v-card-title>
    </v-card>

    <v-card class="mt-4">
      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="wastes"
          :loading="loading"
          class="elevation-1"
        >
          <template v-slot:item.area_m2="{ item }">
            {{ item.area_m2.toFixed(4) }} м²
          </template>

          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" size="small">
              {{ item.status }}
            </v-chip>
          </template>

          <template v-slot:item.actions="{ item }">
            <v-btn icon="mdi-eye" size="small" variant="text" />
            <v-btn icon="mdi-delete" size="small" variant="text" color="error" />
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const headers = [
  { title: 'ID', key: 'id' },
  { title: 'Ширина (мм)', key: 'width' },
  { title: 'Высота (мм)', key: 'height' },
  { title: 'Площадь', key: 'area_m2' },
  { title: 'Материал', key: 'material' },
  { title: 'Проект', key: 'project' },
  { title: 'Статус', key: 'status' },
  { title: 'Действия', key: 'actions', sortable: false }
]

const wastes = ref([])
const loading = ref(false)

const getStatusColor = (status) => {
  return status === 'available' ? 'success' : 'grey'
}

const loadWastes = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/wastes')
    wastes.value = response.data.wastes
  } catch (error) {
    console.error('Ошибка загрузки обрезков:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadWastes()
})
</script>

