<template>
  <div>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h4">
            🏭 Калькулятор раскроя ZVD
          </v-card-title>
          <v-card-subtitle>
            Оптимизация раскроя деталей на листы с учетом обрезков
          </v-card-subtitle>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12" md="4">
        <v-card color="primary" dark>
          <v-card-text>
            <div class="text-h2">{{ stats.available }}</div>
            <div class="text-subtitle-1">Обрезков в наличии</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card color="success" dark>
          <v-card-text>
            <div class="text-h2">{{ stats.reuse_percent }}%</div>
            <div class="text-subtitle-1">Переиспользовано</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card color="info" dark>
          <v-card-text>
            <div class="text-h2">{{ stats.total_value_rub.toLocaleString() }}₽</div>
            <div class="text-subtitle-1">Стоимость обрезков</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>📊 Калькулятор раскроя</v-card-title>
          <v-card-text>
            Рассчитайте оптимальный раскрой деталей на листы
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" :to="'/calculator'" size="large">
              Открыть калькулятор
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>🗑️ База обрезков</v-card-title>
          <v-card-text>
            Просмотр и управление базой обрезков
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" :to="'/wastes'" size="large">
              Открыть базу
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref({
  total: 0,
  available: 0,
  used: 0,
  reuse_percent: 0,
  total_value_rub: 0
})

const loadStatistics = async () => {
  try {
    const response = await axios.get('/api/wastes/statistics')
    stats.value = response.data
  } catch (error) {
    console.error('Ошибка загрузки статистики:', error)
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

