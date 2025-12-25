<template>
  <div>
    <v-card>
      <v-card-title class="text-h5">
        📊 Калькулятор раскроя
      </v-card-title>
    </v-card>

    <v-row class="mt-4">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Детали</v-card-title>
          <v-card-text>
            <v-row v-for="(part, index) in parts" :key="index" class="mb-2">
              <v-col cols="4">
                <v-text-field 
                  v-model="part.name" 
                  label="Название" 
                  density="compact"
                />
              </v-col>
              <v-col cols="2">
                <v-text-field 
                  v-model.number="part.width" 
                  label="Ширина" 
                  type="number"
                  density="compact"
                />
              </v-col>
              <v-col cols="2">
                <v-text-field 
                  v-model.number="part.height" 
                  label="Высота" 
                  type="number"
                  density="compact"
                />
              </v-col>
              <v-col cols="2">
                <v-text-field 
                  v-model.number="part.quantity" 
                  label="Кол-во" 
                  type="number"
                  density="compact"
                />
              </v-col>
              <v-col cols="2">
                <v-btn 
                  icon="mdi-delete" 
                  color="error" 
                  size="small"
                  @click="parts.splice(index, 1)"
                />
              </v-col>
            </v-row>

            <v-btn color="primary" @click="addPart" class="mt-2">
              <v-icon>mdi-plus</v-icon> Добавить деталь
            </v-btn>
          </v-card-text>

          <v-card-actions>
            <v-btn 
              color="success" 
              size="large" 
              @click="calculate"
              :loading="loading"
            >
              Рассчитать раскрой
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card v-if="result">
          <v-card-title>Результат</v-card-title>
          <v-card-text>
            <v-alert type="success" class="mb-4">
              <div><strong>Листов требуется:</strong> {{ result.sheets_needed }}</div>
              <div><strong>Использование:</strong> {{ result.utilization_percent }}%</div>
              <div><strong>Обрезки:</strong> {{ result.waste_percent }}%</div>
            </v-alert>

            <div v-for="sheet in result.sheets" :key="sheet.sheet_number" class="mb-3">
              <v-card variant="outlined">
                <v-card-title class="text-subtitle-1">
                  Лист №{{ sheet.sheet_number }}
                </v-card-title>
                <v-card-text>
                  <div>Деталей: {{ sheet.parts_count }}</div>
                  <div>Использование: {{ sheet.utilization_percent }}%</div>
                </v-card-text>
              </v-card>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const parts = ref([
  { name: 'Корпус', width: 1500, height: 400, quantity: 1 },
  { name: 'Крышка', width: 250, height: 150, quantity: 4 }
])

const result = ref(null)
const loading = ref(false)

const addPart = () => {
  parts.value.push({ name: '', width: 0, height: 0, quantity: 1 })
}

const calculate = async () => {
  loading.value = true
  try {
    const response = await axios.post('/api/nesting/calculate', {
      parts: parts.value,
      sheet_width: 2500,
      sheet_height: 1250,
      allow_rotation: true
    })
    result.value = response.data
  } catch (error) {
    console.error('Ошибка расчета:', error)
    alert('Ошибка расчета раскроя')
  } finally {
    loading.value = false
  }
}
</script>

