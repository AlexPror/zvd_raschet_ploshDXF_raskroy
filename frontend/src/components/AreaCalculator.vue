<template>
  <div>
    <!-- Заголовок -->
    <v-card class="mb-4">
      <v-card-title class="text-h5">
        📐 Расчет площадей разверток из DXF
      </v-card-title>
      <v-card-subtitle>
        Загрузите DXF файлы → выберите материал → введите количество → получите площадь
      </v-card-subtitle>
    </v-card>

    <!-- Номер заказа -->
    <v-card class="mb-4">
      <v-card-text>
        <v-text-field
          v-model="orderNumber"
          label="Номер заказа"
          prepend-icon="mdi-tag"
          density="compact"
          hint="Номер заказа будет автоматически извлечен из названий DXF файлов, если не указан"
          persistent-hint
        />
      </v-card-text>
    </v-card>

    <!-- Выбор материала -->
    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-select
              v-model="selectedMaterial"
              :items="materials"
              item-title="name"
              item-value="name"
              label="Выберите материал"
              prepend-icon="mdi-file-document-multiple"
              return-object
            >
              <template v-slot:item="{ props, item }">
                <v-list-item v-bind="props">
                  <template v-slot:title>
                    {{ item.raw.name }}
                  </template>
                  <template v-slot:subtitle>
                    {{ item.raw.price_per_m2 }} ₽/м²
                  </template>
                </v-list-item>
              </template>
            </v-select>
          </v-col>
          <v-col cols="12" md="6" v-if="selectedMaterial">
            <v-text-field
              v-model.number="selectedMaterial.price_per_m2"
              label="Цена за м²"
              type="number"
              suffix="₽/м²"
              prepend-icon="mdi-currency-rub"
              density="compact"
              min="0"
              step="0.01"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Загрузка файлов -->
    <v-card class="mb-4">
      <v-card-text>
        <v-file-input
          v-model="files"
          label="Выберите DXF файлы (можно из разных папок)"
          accept=".dxf"
          multiple
          prepend-icon="mdi-file-cad"
          @change="uploadFiles"
          :loading="uploading"
          chips
          show-size
        />
        <v-alert type="info" density="compact" class="mt-2">
          Можно выбирать файлы из разных папок - просто добавляйте их по одному или несколько сразу
        </v-alert>
        
        <v-divider class="my-4"></v-divider>
        
        <!-- Импорт из Excel и PDF (скрыто, используется только экспорт) -->
        <v-row v-if="false">
          <v-col cols="12" md="6">
            <v-file-input
              v-model="excelFile"
              label="Импорт из Excel"
              accept=".xlsx,.xls"
              prepend-icon="mdi-file-excel"
              @change="importExcel"
              :loading="importingExcel"
              chips
              show-size
              clearable
            />
            <v-alert type="info" density="compact" class="mt-2">
              Формат: колонки "Название", "Ширина (мм)", "Высота (мм)", "Количество" (опционально)
            </v-alert>
          </v-col>
          <v-col cols="12" md="6">
            <v-file-input
              v-model="pdfFile"
              label="Импорт из PDF"
              accept=".pdf"
              prepend-icon="mdi-file-pdf-box"
              @change="importPDF"
              :loading="importingPDF"
              chips
              show-size
              clearable
            />
            <v-alert type="info" density="compact" class="mt-2">
              PDF должен содержать таблицу с колонками: Название, Ширина, Высота
            </v-alert>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Таблица деталей -->
    <v-card v-if="parts.length > 0">
      <v-card-title>Детали</v-card-title>
      <v-card-text>
        <v-table class="parts-table">
          <thead>
            <tr>
              <th style="min-width: 450px; max-width: 600px;">Название</th>
              <th>Ширина (мм)</th>
              <th>Высота (мм)</th>
              <th>Площадь 1шт (м²)</th>
              <th>Количество</th>
              <th>Итого (м²)</th>
              <th v-if="selectedMaterial">Стоимость 1шт (₽)</th>
              <th v-if="selectedMaterial">Итого стоимость (₽)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(part, index) in parts" :key="index">
              <td class="part-name-cell" :title="part.name">
                {{ part.name }}
              </td>
              <td>{{ part.width }}</td>
              <td>{{ part.height }}</td>
              <td>{{ part.area_m2 }}</td>
              <td>
                <v-text-field
                  v-model.number="part.quantity"
                  type="number"
                  min="1"
                  density="compact"
                  hide-details
                  style="width: 100px"
                />
              </td>
              <td>{{ (part.area_m2 * part.quantity).toFixed(4) }}</td>
              <td v-if="selectedMaterial">
                {{ (part.area_m2 * selectedMaterial.price_per_m2).toFixed(2) }}
              </td>
              <td v-if="selectedMaterial">
                {{ (part.area_m2 * part.quantity * selectedMaterial.price_per_m2).toFixed(2) }}
              </td>
            </tr>
            <tr v-if="selectedMaterial && parts.length > 0" style="background-color: #f5f5f5; font-weight: bold;">
              <td colspan="6" style="text-align: right;">
                <strong>ИТОГО:</strong>
              </td>
              <td v-if="selectedMaterial" colspan="2" style="text-align: left;">
                <strong>{{ totalPartsCost.toFixed(2) }} ₽</strong>
              </td>
            </tr>
          </tbody>
        </v-table>

        <v-divider class="my-4"></v-divider>
        
        <!-- Кнопки расчета -->
        <v-row>
          <v-col cols="12" md="6">
            <v-btn
              color="success"
              size="large"
              @click="calculate"
              :loading="calculating"
              block
            >
              <v-icon>mdi-calculator</v-icon>
              Рассчитать площадь
            </v-btn>
          </v-col>
          <v-col cols="12" md="6">
            <v-btn
              color="primary"
              size="large"
              @click="calculateNesting"
              :loading="calculatingNesting"
              block
            >
              <v-icon>mdi-view-grid</v-icon>
              Раскрой на лист {{ sheetWidth }}×{{ sheetHeight }} мм
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Результат -->
    <v-card v-if="result" class="mt-4">
      <v-card-title>Результат</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-card color="primary" dark>
              <v-card-text>
                <div class="text-h4">{{ result.parts_count }}</div>
                <div>Всего деталей</div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card color="success" dark>
              <v-card-text>
                <div class="text-h4">{{ result.total_area_m2 }} м²</div>
                <div>Чистая площадь</div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card color="info" dark>
              <v-card-text>
                <div class="text-h4">{{ result.total_area_with_gaps_m2 }} м²</div>
                <div>С зазорами (резка)</div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4" v-if="selectedMaterial">
            <v-card color="warning" dark>
              <v-card-text>
                <div class="text-h4">{{ cost.toFixed(2) }} ₽</div>
                <div>Стоимость материала</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <v-alert type="info" class="mt-4">
          <strong>Зазоры:</strong> резка 5 мм, края 10 мм
        </v-alert>
      </v-card-text>
    </v-card>

        <!-- Результат раскроя -->
    <v-card v-if="nestingResult" class="mt-4">
      <v-card-title>
        Результат раскроя на лист {{ nestingResult.sheet_width || 2500 }}×{{ nestingResult.sheet_height || 1250 }} мм
      </v-card-title>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="info"
          @click="printPage"
          class="mr-2"
          size="large"
        >
          <v-icon>mdi-printer</v-icon>
          Печать в PDF
        </v-btn>
        <v-btn
          color="success"
          @click="exportToExcel"
          :loading="exportingExcel"
          class="mr-2"
          size="large"
        >
          <v-icon>mdi-file-excel</v-icon>
          Экспорт в Excel
        </v-btn>
        <v-btn
          color="error"
          @click="exportToPDF"
          :loading="exportingPDF"
          size="large"
        >
          <v-icon>mdi-file-pdf-box</v-icon>
          Экспорт в PDF
        </v-btn>
      </v-card-actions>
      <v-card-text>
        <!-- Компактная таблица результатов -->
        <v-table density="compact" class="results-summary-table">
          <thead>
            <tr>
              <th>Параметр</th>
              <th>Значение</th>
              <th>Параметр</th>
              <th>Значение</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Листов требуется</strong></td>
              <td>{{ nestingResult.sheets_needed }}</td>
              <td><strong>Использование материала</strong></td>
              <td>{{ nestingResult.utilization_percent }}%</td>
            </tr>
            <tr>
              <td><strong>Обрезки (остаток)</strong></td>
              <td>{{ nestingResult.waste_percent }}%</td>
              <td><strong>Площадь деталей</strong></td>
              <td>{{ nestingResult.total_parts_area_m2.toFixed(4) }} м²</td>
            </tr>
            <tr>
              <td><strong>Площадь листов</strong></td>
              <td>{{ nestingResult.total_sheet_area_m2.toFixed(4) }} м²</td>
              <td><strong>Площадь обрезков</strong></td>
              <td>{{ nestingResult.total_waste_area_m2.toFixed(4) }} м²</td>
            </tr>
            <tr v-if="selectedMaterial">
              <td><strong>Стоимость материала</strong></td>
              <td>{{ nestingCost.toFixed(2) }} ₽</td>
              <td><strong>Стоимость обрезков</strong></td>
              <td>{{ wasteCost.toFixed(2) }} ₽</td>
            </tr>
          </tbody>
        </v-table>

        <v-divider class="my-4"></v-divider>

        <!-- Таблица позиций -->
        <v-card v-if="nestingResult.positions_summary && nestingResult.positions_summary.length > 0" class="mb-4">
          <v-card-title>Таблица позиций</v-card-title>
          <v-card-text>
            <v-table>
              <thead>
                <tr>
                  <th>№ поз.</th>
                  <th style="min-width: 450px; max-width: 600px;">Наименование</th>
                  <th>Ширина (мм)</th>
                  <th>Высота (мм)</th>
                  <th>Площадь 1шт (м²)</th>
                  <th>Количество</th>
                  <th>Итого площадь (м²)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="pos in nestingResult.positions_summary" :key="pos.position_number">
                  <td><strong>{{ pos.position_number }}</strong></td>
                  <td class="part-name-cell" :title="pos.name">
                    {{ pos.name }}
                  </td>
                  <td>{{ pos.width }}</td>
                  <td>{{ pos.height }}</td>
                  <td>{{ pos.area_m2.toFixed(4) }}</td>
                  <td>{{ pos.quantity }}</td>
                  <td>{{ pos.total_area_m2.toFixed(4) }}</td>
                </tr>
              </tbody>
            </v-table>
          </v-card-text>
        </v-card>

        <!-- Результаты валидации -->
        <v-card v-if="validationResult" class="mb-4">
          <v-card-title>
            <v-icon :color="validationResult.valid ? 'success' : 'error'" class="mr-2">
              {{ validationResult.valid ? 'mdi-check-circle' : 'mdi-alert-circle' }}
            </v-icon>
            Проверка раскроя
          </v-card-title>
          <v-card-text>
            <v-alert 
              :type="validationResult.valid ? 'success' : 'error'" 
              :density="validationResult.valid ? 'compact' : 'default'"
              class="mb-2"
            >
              <div v-if="validationResult.valid">
                <strong>✓ Раскрой валиден!</strong> Все детали размещены корректно.
              </div>
              <div v-else>
                <strong>✗ Обнаружены ошибки в раскрое:</strong>
                <ul class="mt-2">
                  <li v-for="(error, idx) in validationResult.errors" :key="idx">
                    {{ error }}
                  </li>
                </ul>
              </div>
            </v-alert>
            
            <!-- Детальная таблица пересечений -->
            <v-card v-if="validationResult.details.intersections && validationResult.details.intersections.length > 0" class="mb-2">
              <v-card-title class="text-subtitle-1 text-error">
                🔴 Пересечения деталей ({{ validationResult.details.intersections.length }})
              </v-card-title>
              <v-card-text>
                <v-table density="compact">
                  <thead>
                    <tr>
                      <th>Деталь 1</th>
                      <th>Координаты 1</th>
                      <th>Деталь 2</th>
                      <th>Координаты 2</th>
                      <th>Площадь пересечения</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(intersection, idx) in validationResult.details.intersections" :key="idx">
                      <td class="text-error">
                        <strong>{{ intersection.part1 }}</strong>
                      </td>
                      <td>
                        X:{{ intersection.part1_coords.x.toFixed(1) }}, Y:{{ intersection.part1_coords.y.toFixed(1) }}<br>
                        X2:{{ intersection.part1_coords.x2.toFixed(1) }}, Y2:{{ intersection.part1_coords.y2.toFixed(1) }}
                      </td>
                      <td class="text-error">
                        <strong>{{ intersection.part2 }}</strong>
                      </td>
                      <td>
                        X:{{ intersection.part2_coords.x.toFixed(1) }}, Y:{{ intersection.part2_coords.y.toFixed(1) }}<br>
                        X2:{{ intersection.part2_coords.x2.toFixed(1) }}, Y2:{{ intersection.part2_coords.y2.toFixed(1) }}
                      </td>
                      <td class="text-error">
                        <strong>{{ intersection.intersection_area_mm2.toFixed(1) }} мм²</strong><br>
                        <span class="text-caption">({{ (intersection.intersection_area_mm2 / 1000000).toFixed(4) }} м²)</span>
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card-text>
            </v-card>
            
            <!-- Детали выхода за границы -->
            <v-card v-if="validationResult.details.out_of_bounds && validationResult.details.out_of_bounds.length > 0" class="mb-2">
              <v-card-title class="text-subtitle-1 text-warning">
                ⚠️ Выход за границы листа ({{ validationResult.details.out_of_bounds.length }})
              </v-card-title>
              <v-card-text>
                <v-table density="compact">
                  <thead>
                    <tr>
                      <th>Деталь</th>
                      <th>Проблема</th>
                      <th>Координаты</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(out, idx) in validationResult.details.out_of_bounds" :key="idx">
                      <td><strong>{{ out.part }}</strong></td>
                      <td>{{ out.issue === 'negative_coords' ? 'Отрицательные координаты' : 'Выход за границы' }}</td>
                      <td>
                        X:{{ out.x.toFixed(1) }}, Y:{{ out.y.toFixed(1) }}
                        <span v-if="out.x2"> → X2:{{ out.x2.toFixed(1) }}, Y2:{{ out.y2.toFixed(1) }}</span>
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card-text>
            </v-card>
            
            <v-alert 
              v-if="validationResult.warnings && validationResult.warnings.length > 0"
              type="warning" 
              density="compact"
              class="mb-2"
            >
              <strong>Предупреждения:</strong>
              <ul class="mt-2">
                <li v-for="(warning, idx) in validationResult.warnings" :key="idx">
                  {{ warning }}
                </li>
              </ul>
            </v-alert>
            
            <v-alert type="info" density="compact">
              <strong>Статистика:</strong> 
              {{ validationResult.details.total_parts }} деталей на {{ validationResult.details.total_sheets }} листах,
              {{ validationResult.details.errors_count }} ошибок, {{ validationResult.details.warnings_count }} предупреждений
            </v-alert>
          </v-card-text>
        </v-card>

        <!-- Визуализация раскроя -->
        <div v-for="sheet in nestingResult.sheets" :key="sheet.sheet_number" class="mb-4">
          <NestingVisualization
            :sheet="sheet"
            :sheet-width="nestingResult.sheet_width"
            :sheet-height="nestingResult.sheet_height"
            :intersections="validationResult ? validationResult.details.intersections : []"
          />
          
          <!-- Таблица координат для этого листа -->
          <v-card class="mt-2">
            <v-card-title class="text-subtitle-1">
              📍 Координаты размещения деталей на листе №{{ sheet.sheet_number }}
            </v-card-title>
            <v-card-text>
              <v-table density="compact">
                <thead>
                  <tr>
                    <th>№ поз.</th>
                    <th style="min-width: 300px;">Наименование</th>
                    <th>X (мм)</th>
                    <th>Y (мм)</th>
                    <th>Ширина (мм)</th>
                    <th>Высота (мм)</th>
                    <th>X2 (мм)</th>
                    <th>Y2 (мм)</th>
                    <th>Поворот</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(part, idx) in sheet.parts" :key="idx">
                    <td><strong>{{ part.position_number || '-' }}</strong></td>
                    <td class="part-name-cell" :title="part.name">
                      {{ part.name }}
                    </td>
                    <td>{{ part.x.toFixed(1) }}</td>
                    <td>{{ part.y.toFixed(1) }}</td>
                    <td>{{ part.width.toFixed(1) }}</td>
                    <td>{{ part.height.toFixed(1) }}</td>
                    <td>{{ (part.x + part.width).toFixed(1) }}</td>
                    <td>{{ (part.y + part.height).toFixed(1) }}</td>
                    <td>
                      <v-chip v-if="part.rotated" color="warning" size="small">↻ 90°</v-chip>
                      <span v-else>-</span>
                    </td>
                  </tr>
                </tbody>
              </v-table>
              <v-alert type="info" density="compact" class="mt-2">
                <strong>Пояснение:</strong> X, Y - координаты левого верхнего угла детали. 
                X2, Y2 - координаты правого нижнего угла. 
                Все координаты относительно левого верхнего угла листа (0, 0).
              </v-alert>
            </v-card-text>
          </v-card>
        </div>

      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'
import NestingVisualization from './NestingVisualization.vue'

const files = ref([])
const parts = ref([])
const result = ref(null)
const nestingResult = ref(null)
const validationResult = ref(null)
const uploading = ref(false)
const calculating = ref(false)
const calculatingNesting = ref(false)
const orderNumber = ref('')

// Импорт из Excel и PDF
const excelFile = ref(null)
const pdfFile = ref(null)
const importingExcel = ref(false)
const importingPDF = ref(false)

// Экспорт в Excel и PDF
const exportingExcel = ref(false)
const exportingPDF = ref(false)

// Материалы с фиксированными ценами
// TODO: Можно добавить загрузку цен из Excel файла через API
const materials = ref([
  {
    name: 'Оцинковка: Оц. Б-ПН-О-1,0х1250х2500 ГОСТ 19904-2015/ 08ПС ГОСТ 14918-2020',
    thickness: 1.0,
    price_per_m2: 450.0,
    type: 'galvanized'
  },
  {
    name: 'Нержавейка: Лист 1,0х1250х2500 ГОСТ 5582-75/ 08Х18Н10 ГОСТ 5632-2014',
    thickness: 1.0,
    price_per_m2: 1200.0,
    type: 'stainless'
  }
])

const selectedMaterial = ref(materials.value[0]) // По умолчанию первый материал

// Фиксированные размеры листа для раскроя (ширина x длина)
const sheetWidth = ref(2500)
const sheetHeight = ref(1250)

// Функция для загрузки материалов из API (если будет реализовано)
const loadMaterials = async () => {
  try {
    // const response = await axios.get('/api/materials')
    // materials.value = response.data
  } catch (error) {
    console.warn('Не удалось загрузить материалы, используем фиксированные цены')
  }
}

/**
 * Извлекает номер заказа из названия файла
 * Форматы: "001 - Корпус короба прямой 1600 1шт (А-151025-1235)" -> "А-151025-1235"
 *          "001_-_2200_1_-151025-1235" -> "151025-1235"
 */
const extractOrderNumberFromFilename = (filename) => {
  if (!filename) return null
  
  const nameWithoutExt = filename.replace(/\.dxf$/i, '')
  
  // Паттерн для формата с скобками: "(А-151025-1235)" или "(151025-1235)"
  const pattern1 = /\(([А-Яа-яA-Za-z0-9\-]+)\)/
  const match1 = nameWithoutExt.match(pattern1)
  if (match1) {
    return match1[1]
  }
  
  // Паттерн для формата с подчеркиваниями: "_-151025-1235" или "_-А-151025-1235"
  const pattern2 = /[_-]([А-Яа-яA-Za-z0-9\-]+)$/
  const match2 = nameWithoutExt.match(pattern2)
  if (match2) {
    const potential = match2[1]
    // Проверяем, что это похоже на номер заказа (содержит дефис или буквы)
    if (potential.includes('-') || /[А-Яа-яA-Za-z]/.test(potential)) {
      return potential
    }
  }
  
  return null
}

/**
 * Извлекает количество деталей из имени файла
 */
const extractQuantityFromFilename = (filename) => {
  if (!filename) return 1
  
  const nameWithoutExt = filename.replace(/\.dxf$/i, '')
  
  // Паттерн для нового формата: "001 - Корпус короба прямой 1600 1шт (А-151025-1235)"
  // Ищем "1шт", "2шт", "3шт" и т.д. или "1 шт", "2 шт"
  const patternNew = /(\d+)\s*шт/i
  const matchNew = nameWithoutExt.match(patternNew)
  if (matchNew) {
    const quantity = parseInt(matchNew[1], 10)
    if (quantity > 0 && quantity < 1000) return quantity
  }
  
  // Старый формат: "001_-_2200_1_-151025-1235"
  const pattern1 = /_-_(\d+)_-/i
  const match1 = nameWithoutExt.match(pattern1)
  if (match1) {
    const quantity = parseInt(match1[1], 10)
    if (quantity > 0) return quantity
  }
  
  const pattern2 = /_-_(\d+)$/i
  const match2 = nameWithoutExt.match(pattern2)
  if (match2) {
    const quantity = parseInt(match2[1], 10)
    if (quantity > 0) return quantity
  }
  
  // Паттерн для формата с подчеркиваниями в конце
  const pattern3 = /[_-](\d+)$/
  const match3 = nameWithoutExt.match(pattern3)
  if (match3) {
    const quantity = parseInt(match3[1], 10)
    if (quantity > 0 && quantity < 1000) return quantity
  }
  
  return 1
}

// Расчет стоимости для площади
const cost = computed(() => {
  if (!result.value || !selectedMaterial.value) return 0
  return result.value.total_area_with_gaps_m2 * selectedMaterial.value.price_per_m2
})

// Расчет стоимости для раскроя
const nestingCost = computed(() => {
  if (!nestingResult.value || !selectedMaterial.value) return 0
  return nestingResult.value.total_sheet_area_m2 * selectedMaterial.value.price_per_m2
})

// Расчет стоимости обрезков
const wasteCost = computed(() => {
  if (!nestingResult.value || !selectedMaterial.value) return 0
  return nestingResult.value.total_waste_area_m2 * selectedMaterial.value.price_per_m2
})

// Стоимость использованного материала (без обрезков)
const usedMaterialCost = computed(() => {
  if (!nestingResult.value || !selectedMaterial.value) return 0
  return nestingResult.value.total_parts_area_m2 * selectedMaterial.value.price_per_m2
})

// Итоговая стоимость всех деталей
const totalPartsCost = computed(() => {
  if (!selectedMaterial.value || !parts.value.length) return 0
  return parts.value.reduce((sum, part) => {
    return sum + (part.area_m2 * part.quantity * selectedMaterial.value.price_per_m2)
  }, 0)
})

// Сохраняем список уже загруженных файлов
const loadedFiles = ref(new Set())

const uploadFiles = async () => {
  if (!files.value || files.value.length === 0) {
    // Если все файлы удалены, очищаем все
    if (files.value.length === 0) {
      parts.value = []
      loadedFiles.value.clear()
    }
    return
  }
  
  // Определяем новые файлы (которые еще не загружены)
  const newFiles = files.value.filter(file => !loadedFiles.value.has(file.name))
  
  if (newFiles.length === 0) {
    // Все файлы уже загружены
    return
  }
  
  console.log('📤 Загрузка новых файлов:', newFiles.length, 'из', files.value.length, 'всего')
  uploading.value = true
  
  try {
    const formData = new FormData()
    
    // Загружаем только новые файлы
    for (const file of newFiles) {
      console.log('  📄 Новый файл:', file.name, 'размер:', file.size, 'байт')
      formData.append('files', file)
      loadedFiles.value.add(file.name)
    }
    
    console.log('🌐 Отправляю запрос на /api/upload')
    const response = await axios.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000, // 2 минуты таймаут для больших файлов
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          console.log(`📤 Прогресс загрузки: ${percentCompleted}%`)
        }
      }
    })
    
    console.log('📥 Получен ответ:', response.data)
    
    // Извлекаем количество из имени файла для каждой детали
    const newParts = response.data.parts.map(part => {
      const quantity = extractQuantityFromFilename(part.name)
      console.log(`  Деталь: ${part.name}, извлечено количество: ${quantity}`)
      return {
        ...part,
        quantity: quantity
      }
    })
    
    // Объединяем с существующими деталями (если есть)
    const existingPartsMap = new Map(parts.value.map(p => [p.name, p]))
    for (const newPart of newParts) {
      if (existingPartsMap.has(newPart.name)) {
        // Если деталь уже есть, СУММИРУЕМ количество
        const existing = existingPartsMap.get(newPart.name)
        existing.quantity = existing.quantity + newPart.quantity
        console.log(`  Обновлено количество для ${newPart.name}: ${existing.quantity}`)
      } else {
        // Добавляем новую деталь
        parts.value.push(newPart)
      }
    }
    
    // Извлекаем номер заказа из названий файлов, если не указан вручную
    if (!orderNumber.value) {
      const orderNumbers = new Set()
      for (const part of parts.value) {
        const extracted = extractOrderNumberFromFilename(part.name)
        if (extracted) {
          orderNumbers.add(extracted)
        }
      }
      if (orderNumbers.size === 1) {
        orderNumber.value = Array.from(orderNumbers)[0]
      } else if (orderNumbers.size > 1) {
        // Если несколько номеров, объединяем через запятую
        orderNumber.value = Array.from(orderNumbers).join(', ')
      }
    }
    
    console.log('✅ Всего деталей:', parts.value.length)
    result.value = null
    nestingResult.value = null
    
  } catch (error) {
    console.error('❌ Ошибка загрузки:', error)
    if (error.response) {
      console.error('Ответ сервера:', error.response.data)
    }
    alert('Ошибка загрузки файлов: ' + (error.response?.data?.error || error.message))
  } finally {
    uploading.value = false
  }
}

const calculate = async () => {
  console.log('🔄 Расчет площади для', parts.value.length, 'деталей')
  calculating.value = true
  
  try {
    const requestData = {
      parts: parts.value,
      cut_gap: 5,
      edge_margin: 10
    }
    
    console.log('📤 Отправляю запрос:', requestData)
    const response = await axios.post('/api/calculate', requestData)
    
    console.log('📥 Получен ответ:', response.data)
    result.value = response.data
    
  } catch (error) {
    console.error('❌ Ошибка расчета:', error)
    if (error.response) {
      console.error('Ответ сервера:', error.response.data)
    }
    alert('Ошибка расчета площадей: ' + (error.response?.data?.error || error.message))
  } finally {
    calculating.value = false
  }
}

const calculateNesting = async () => {
  console.log('='.repeat(50))
  console.log('🔄 Начинаю расчет раскроя...')
  console.log('📦 Детали:', parts.value)
  
  calculatingNesting.value = true
  
  try {
    const requestData = {
      parts: parts.value,
      sheet_width: 2500,
      sheet_height: 1250,
      allow_rotation: true
    }
    
    console.log('📤 Отправляю запрос:', requestData)
    console.log('🌐 URL: /api/nesting/calculate')
    
    const response = await axios.post('/api/nesting/calculate', requestData)
    
    console.log('📥 Получен ответ:', response.data)
    console.log('✅ Статус:', response.status)
    
    nestingResult.value = response.data
    
    // Валидация раскроя
    console.log('🔍 Запускаю валидацию раскроя...')
    try {
      const validateResponse = await axios.post('/api/nesting/validate', {
        sheets: response.data.sheets,
        sheet_width: response.data.sheet_width,
        sheet_height: response.data.sheet_height
      })
      
      validationResult.value = validateResponse.data
      console.log('✅ Валидация завершена:', validateResponse.data)
      
      if (!validateResponse.data.valid) {
        console.warn('⚠️ Раскрой содержит ошибки:', validateResponse.data.errors)
      }
    } catch (validateError) {
      console.error('❌ Ошибка валидации:', validateError)
      // Не блокируем отображение результата, если валидация не удалась
    }
    
    console.log('✅ Раскрой успешно рассчитан')
    console.log('='.repeat(50))
    
  } catch (error) {
    console.error('='.repeat(50))
    console.error('❌ ОШИБКА расчета раскроя')
    console.error('Тип ошибки:', error.name)
    console.error('Сообщение:', error.message)
    console.error('Полный объект ошибки:', error)
    
    if (error.response) {
      console.error('📥 Ответ сервера:', error.response.data)
      console.error('📊 Статус:', error.response.status)
      console.error('📋 Заголовки:', error.response.headers)
    } else if (error.request) {
      console.error('❌ Запрос отправлен, но ответа нет')
      console.error('Запрос:', error.request)
    } else {
      console.error('❌ Ошибка настройки запроса:', error.message)
    }
    
    console.error('='.repeat(50))
    
    const errorMsg = error.response?.data?.error || error.message || 'Неизвестная ошибка'
    alert('Ошибка расчета раскроя: ' + errorMsg)
  } finally {
    calculatingNesting.value = false
  }
}

const importExcel = async () => {
  if (!excelFile.value || excelFile.value.length === 0) {
    return
  }
  
  importingExcel.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', excelFile.value[0])
    
    const response = await axios.post('/api/import/excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    if (response.data.success && response.data.parts) {
      // Объединяем с существующими деталями
      const existingPartsMap = new Map(parts.value.map(p => [p.name, p]))
      for (const newPart of response.data.parts) {
        if (existingPartsMap.has(newPart.name)) {
          // Если деталь уже есть, СУММИРУЕМ количество
          const existing = existingPartsMap.get(newPart.name)
          existing.quantity = existing.quantity + newPart.quantity
        } else {
          // Добавляем новую деталь
          parts.value.push(newPart)
        }
      }
      
      result.value = null
      nestingResult.value = null
      
      alert(`Импортировано ${response.data.parts.length} деталей из Excel`)
    }
  } catch (error) {
    console.error('❌ Ошибка импорта Excel:', error)
    const errorMsg = error.response?.data?.error || error.message || 'Неизвестная ошибка'
    alert('Ошибка импорта Excel: ' + errorMsg)
  } finally {
    importingExcel.value = false
    excelFile.value = null
  }
}

const importPDF = async () => {
  if (!pdfFile.value || pdfFile.value.length === 0) {
    return
  }
  
  importingPDF.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', pdfFile.value[0])
    
    const response = await axios.post('/api/import/pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    if (response.data.success && response.data.parts) {
      // Объединяем с существующими деталями
      const existingPartsMap = new Map(parts.value.map(p => [p.name, p]))
      for (const newPart of response.data.parts) {
        if (existingPartsMap.has(newPart.name)) {
          // Если деталь уже есть, СУММИРУЕМ количество
          const existing = existingPartsMap.get(newPart.name)
          existing.quantity = existing.quantity + newPart.quantity
        } else {
          // Добавляем новую деталь
          parts.value.push(newPart)
        }
      }
      
      result.value = null
      nestingResult.value = null
      
      alert(`Импортировано ${response.data.parts.length} деталей из PDF`)
    }
  } catch (error) {
    console.error('❌ Ошибка импорта PDF:', error)
    const errorMsg = error.response?.data?.error || error.message || 'Неизвестная ошибка'
    alert('Ошибка импорта PDF: ' + errorMsg)
  } finally {
    importingPDF.value = false
    pdfFile.value = null
  }
}

const exportToExcel = async () => {
  if (!nestingResult.value) {
    alert('Нет данных для экспорта')
    return
  }
  
  exportingExcel.value = true
  
  try {
    const response = await axios.post('/api/export/excel', {
      nesting_result: nestingResult.value,
      validation_result: validationResult.value,
      order_number: orderNumber.value || '',
      material_price: selectedMaterial.value ? selectedMaterial.value.price_per_m2 : 0,
      material_name: selectedMaterial.value ? selectedMaterial.value.name : ''
    }, {
      responseType: 'blob'
    })
    
    // Получаем имя файла из заголовка ответа или формируем из order_number
    let filename = `nesting_export_${new Date().toISOString().slice(0, 10)}.xlsx`
    const contentDisposition = response.headers['content-disposition']
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename\*=UTF-8''(.+)/i) || contentDisposition.match(/filename="(.+)"/i)
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch[1])
      }
    } else if (orderNumber.value) {
      // Формируем имя файла из номера заказа
      const safeOrderNumber = orderNumber.value.replace(/[\/\\:*?"<>|]/g, '_')
      filename = `Расчет площади и раскроя ${safeOrderNumber}.xlsx`
    }
    
    // Создаем ссылку для скачивания
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    alert('Excel файл успешно экспортирован')
  } catch (error) {
    console.error('❌ Ошибка экспорта Excel:', error)
    const errorMsg = error.response?.data?.error || error.message || 'Неизвестная ошибка'
    alert('Ошибка экспорта Excel: ' + errorMsg)
  } finally {
    exportingExcel.value = false
  }
}

const exportToPDF = async () => {
  if (!nestingResult.value) {
    alert('Нет данных для экспорта')
    return
  }
  
  exportingPDF.value = true
  
  try {
    const response = await axios.post('/api/export/pdf', {
      nesting_result: nestingResult.value,
      validation_result: validationResult.value,
      material_price: selectedMaterial.value ? selectedMaterial.value.price_per_m2 : 0,
      material_name: selectedMaterial.value ? selectedMaterial.value.name : '',
      order_number: orderNumber.value || ''
    }, {
      responseType: 'blob'
    })
    
    // Получаем имя файла из заголовка ответа или формируем из order_number
    let filename = `nesting_export_${new Date().toISOString().slice(0, 10)}.pdf`
    const contentDisposition = response.headers['content-disposition']
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename\*=UTF-8''(.+)/i) || contentDisposition.match(/filename="(.+)"/i)
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch[1])
      }
    } else if (orderNumber.value) {
      // Формируем имя файла из номера заказа
      const safeOrderNumber = orderNumber.value.replace(/[\/\\:*?"<>|]/g, '_')
      filename = `Расчет площади и раскроя ${safeOrderNumber}.pdf`
    }
    
    // Создаем ссылку для скачивания
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    alert('PDF файл успешно экспортирован')
  } catch (error) {
    console.error('❌ Ошибка экспорта PDF:', error)
    const errorMsg = error.response?.data?.error || error.message || 'Неизвестная ошибка'
    alert('Ошибка экспорта PDF: ' + errorMsg)
  } finally {
    exportingPDF.value = false
  }
}

const printPage = () => {
  window.print()
}
</script>

<style scoped>
.parts-table {
  table-layout: auto;
}

.parts-table th:first-child,
.parts-table td:first-child {
  min-width: 450px !important;
  max-width: 600px !important;
  width: auto !important;
}

.part-name-cell {
  word-wrap: break-word !important;
  word-break: break-all !important;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: clip !important;
  line-height: 1.4 !important;
  padding: 8px 4px !important;
}

/* Компактная таблица результатов */
.results-summary-table {
  margin-bottom: 16px;
}

.results-summary-table th,
.results-summary-table td {
  padding: 8px 12px !important;
  font-size: 14px;
}

/* Стили для печати в PDF */
@media print {
  @page {
    size: A4 landscape;
    margin: 5mm;
    margin-header: 0;
    margin-footer: 0;
  }
  
  body {
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
    margin: 0 !important;
    padding: 0 !important;
  }
  
  /* Контейнер приложения */
  .v-application {
    margin: 0 !important;
    padding: 0 !important;
  }
  
  /* Главный контейнер */
  .v-main {
    margin: 0 !important;
    padding: 0 !important;
  }
  
  /* Контейнер контента */
  .v-container {
    margin: 0 !important;
    padding: 3mm !important;
    max-width: 100% !important;
  }
  
  /* Скрываем ненужные элементы */
  .v-app-bar,
  .v-footer,
  .v-btn,
  .v-file-input,
  .v-select,
  .v-alert,
  .v-card-actions,
  .v-divider {
    display: none !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  
  /* Карточки */
  .v-card {
    page-break-inside: avoid;
    break-inside: avoid;
    margin: 2mm 0 !important;
    margin-bottom: 3mm !important;
    box-shadow: none !important;
    border: none !important;
    padding: 0 !important;
  }
  
  .v-card-title {
    page-break-after: avoid;
    break-after: avoid;
    font-size: 14px !important;
    padding: 2mm 0 !important;
    margin: 0 !important;
    margin-bottom: 2mm !important;
    border-bottom: 1px solid #000 !important;
  }
  
  .v-card-text {
    padding: 2mm 0 !important;
    margin: 0 !important;
  }
  
  /* Компактные таблицы с увеличенным шрифтом */
  .v-table {
    page-break-inside: auto;
    font-size: 11px !important;
    border-collapse: collapse !important;
    width: 100% !important;
    margin: 1mm 0 !important;
  }
  
  .v-table th,
  .v-table td {
    padding: 1.5mm 2mm !important;
    border: 1px solid #000 !important;
    font-size: 10px !important;
    line-height: 1.2 !important;
  }
  
  .v-table th {
    background-color: #f0f0f0 !important;
    font-weight: bold !important;
  }
  
  /* Разрешаем перенос строк в таблицах */
  .v-table tr {
    page-break-inside: auto;
    break-inside: auto;
  }
  
  /* Заголовки таблиц повторяются на каждой странице */
  .v-table thead {
    display: table-header-group;
  }
  
  .v-table tbody {
    display: table-row-group;
  }
  
  /* Компактная таблица результатов */
  .results-summary-table {
    font-size: 11px !important;
    margin: 1mm 0 !important;
  }
  
  .results-summary-table th,
  .results-summary-table td {
    padding: 1mm 1.5mm !important;
    font-size: 10px !important;
    line-height: 1.2 !important;
  }
  
  /* Визуализация раскроя - компактная */
  .nesting-visualization {
    page-break-inside: avoid;
    break-inside: avoid;
    margin: 1mm 0 !important;
  }
  
  .canvas-container {
    max-width: 100% !important;
    overflow: visible;
    padding: 1mm !important;
    margin: 0 !important;
    page-break-inside: avoid;
    break-inside: avoid;
    border: none !important;
  }
  
  .nesting-canvas {
    max-width: 100% !important;
    height: auto !important;
    max-height: 120px !important;
    page-break-inside: avoid;
    break-inside: avoid;
  }
  
  /* Таблицы координат - компактные */
  .v-table {
    width: 100% !important;
    table-layout: fixed !important;
  }
  
  .v-table th,
  .v-table td {
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow: visible !important;
  }
  
  .part-name-cell {
    max-width: 150px !important;
    white-space: normal !important;
    word-break: break-word !important;
    font-size: 9px !important;
  }
  
  /* Убираем лишние отступы */
  .v-row {
    margin: 0 !important;
    margin-bottom: 1mm !important;
  }
  
  .v-col {
    padding: 1mm !important;
  }
  
  /* Компактные заголовки */
  .text-h4, .text-h5, .text-h6 {
    font-size: 12px !important;
    margin: 0.5mm 0 !important;
    line-height: 1.2 !important;
  }
  
  /* Убираем рамки вокруг карточек */
  .v-card {
    border: none !important;
    box-shadow: none !important;
  }
  
  /* Отступы между секциями */
  .v-card + .v-card {
    margin-top: 2mm !important;
  }
  
  /* Отступы для вложенных элементов */
  .v-card-text > * {
    margin-top: 1mm !important;
    margin-bottom: 1mm !important;
  }
  
  .v-card-text > *:first-child {
    margin-top: 0 !important;
  }
  
  .v-card-text > *:last-child {
    margin-bottom: 0 !important;
  }
}
</style>

