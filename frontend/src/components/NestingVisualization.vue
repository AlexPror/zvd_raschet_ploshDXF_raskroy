<template>
  <div class="nesting-visualization">
    <v-card>
      <v-card-title class="text-h6">
        Лист №{{ sheet.sheet_number }} ({{ sheet.utilization_percent }}% использовано)
      </v-card-title>
      <v-card-text>
        <div class="canvas-container">
          <canvas
            ref="canvasRef"
            :width="canvasWidth"
            :height="canvasHeight"
            class="nesting-canvas"
            style="border: 1px solid #ccc;"
          ></canvas>
        </div>
        
        <v-row class="mt-2">
          <v-col cols="6">
            <div class="text-caption">
              <strong>Использовано:</strong> {{ sheet.used_area_m2.toFixed(4) }} м²
            </div>
          </v-col>
          <v-col cols="6">
            <div class="text-caption">
              <strong>Остаток:</strong> {{ sheet.waste_area_m2.toFixed(4) }} м²
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  sheet: {
    type: Object,
    required: true
  },
  sheetWidth: {
    type: Number,
    default: 2500
  },
  sheetHeight: {
    type: Number,
    default: 1250
  },
  intersections: {
    type: Array,
    default: () => []
  }
})

const canvasRef = ref(null)
// Размер canvas для отображения листа в масштабе
// Используем динамические пропорции листа для правильного отображения
const maxCanvasWidth = 1000
const canvasAspectRatio = computed(() => {
  // sheetWidth - это ширина листа (большая сторона, например 2500)
  // sheetHeight - это длина/высота листа (меньшая сторона, например 1250)
  // Соотношение: ширина/длина для правильной ориентации (горизонтальный лист)
  if (!props.sheetWidth || !props.sheetHeight) return 2
  return props.sheetWidth / props.sheetHeight
})
const canvasWidth = ref(maxCanvasWidth)
const canvasHeight = computed(() => {
  if (!canvasAspectRatio.value) return 500
  return Math.round(maxCanvasWidth / canvasAspectRatio.value)
})

const drawNesting = () => {
  if (!canvasRef.value) return
  
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  
  // Проверяем наличие данных
  if (!props.sheet || !props.sheet.parts || props.sheet.parts.length === 0) {
    console.warn('Нет данных для визуализации:', props.sheet)
    return
  }
  
  if (!props.sheetWidth || !props.sheetHeight) {
    console.warn('Не указаны размеры листа:', props.sheetWidth, props.sheetHeight)
    return
  }
  
  // Устанавливаем размеры canvas
  canvas.width = canvasWidth.value
  canvas.height = canvasHeight.value
  
  // Очищаем canvas
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // Масштаб для отображения (sheetWidth - ширина, sheetHeight - длина)
  const scaleX = canvasWidth.value / props.sheetWidth
  const scaleY = canvasHeight.value / props.sheetHeight
  const scale = Math.min(scaleX, scaleY)
  
  const offsetX = (canvasWidth.value - props.sheetWidth * scale) / 2
  const offsetY = (canvasHeight.value - props.sheetHeight * scale) / 2
  
  // Рисуем лист (фон) - sheetWidth по горизонтали, sheetHeight по вертикали
  ctx.fillStyle = '#e0e0e0'
  ctx.fillRect(offsetX, offsetY, props.sheetWidth * scale, props.sheetHeight * scale)
  
  // Рисуем границу листа
  ctx.strokeStyle = '#424242'
  ctx.lineWidth = 2
  ctx.strokeRect(offsetX, offsetY, props.sheetWidth * scale, props.sheetHeight * scale)
  
  // Определяем пересекающиеся детали для этого листа
  const intersectingParts = new Set()
  if (props.intersections && props.intersections.length > 0) {
    props.intersections.forEach(intersection => {
      if (intersection.sheet === props.sheet.sheet_number) {
        intersectingParts.add(intersection.part1)
        intersectingParts.add(intersection.part2)
      }
    })
  }
  
  // Рисуем детали
  const colors = [
    '#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336',
    '#00BCD4', '#FFC107', '#E91E63', '#3F51B5', '#8BC34A'
  ]
  
  props.sheet.parts.forEach((part, index) => {
    // Если деталь пересекается, используем красный цвет
    const isIntersecting = intersectingParts.has(part.name)
    const color = isIntersecting ? '#F44336' : colors[index % colors.length]
    
    // Рисуем деталь
    ctx.fillStyle = color
    ctx.fillRect(
      offsetX + part.x * scale,
      offsetY + part.y * scale,
      part.width * scale,
      part.height * scale
    )
    
    // Рисуем границу детали (толще для пересекающихся)
    ctx.strokeStyle = isIntersecting ? '#FF0000' : '#000'
    ctx.lineWidth = isIntersecting ? 3 : 1
    ctx.strokeRect(
      offsetX + part.x * scale,
      offsetY + part.y * scale,
      part.width * scale,
      part.height * scale
    )
    
    // Если деталь пересекается, рисуем предупреждающий индикатор
    if (isIntersecting) {
      ctx.fillStyle = '#FF0000'
      ctx.font = 'bold 12px Arial'
      ctx.textAlign = 'left'
      ctx.textBaseline = 'top'
      ctx.fillText('⚠ ПЕРЕСЕЧЕНИЕ', offsetX + part.x * scale + 5, offsetY + part.y * scale + 5)
    }
    
    // Подпись детали (если достаточно места)
    if (part.width * scale > 50 && part.height * scale > 30) {
      ctx.fillStyle = '#000'
      ctx.font = '9px Arial'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      
      const textX = offsetX + part.x * scale + part.width * scale / 2
      const textY = offsetY + part.y * scale + part.height * scale / 2
      
      // Полное название файла
      const fullName = part.name
      
      // Разбиваем текст на строки, если он длинный
      const maxWidth = part.width * scale - 10 // Оставляем отступы
      const lineHeight = 12
      const lines = []
      let currentLine = ''
      
      // Разбиваем по словам (если есть пробелы) или по символам
      const words = fullName.split(/[\s_-]/).filter(w => w.length > 0)
      
      if (words.length > 0) {
        // Разбиваем по словам
        for (const word of words) {
          const testLine = currentLine ? `${currentLine} ${word}` : word
          const metrics = ctx.measureText(testLine)
          
          if (metrics.width <= maxWidth || !currentLine) {
            currentLine = testLine
          } else {
            lines.push(currentLine)
            currentLine = word
          }
        }
        if (currentLine) {
          lines.push(currentLine)
        }
      } else {
        // Если нет пробелов, разбиваем по символам
        for (let i = 0; i < fullName.length; i++) {
          const testLine = currentLine + fullName[i]
          const metrics = ctx.measureText(testLine)
          
          if (metrics.width <= maxWidth) {
            currentLine = testLine
          } else {
            if (currentLine) lines.push(currentLine)
            currentLine = fullName[i]
          }
        }
        if (currentLine) {
          lines.push(currentLine)
        }
      }
      
      // Ограничиваем количество строк в зависимости от высоты детали
      const maxLines = Math.floor((part.height * scale - 10) / lineHeight)
      const displayLines = lines.slice(0, maxLines)
      
      // Если текст обрезан, добавляем многоточие
      if (lines.length > maxLines) {
        const lastLine = displayLines[displayLines.length - 1]
        const ellipsis = '...'
        let truncated = lastLine
        while (ctx.measureText(truncated + ellipsis).width > maxWidth && truncated.length > 0) {
          truncated = truncated.slice(0, -1)
        }
        displayLines[displayLines.length - 1] = truncated + ellipsis
      }
      
      // Вычисляем общую высоту текста
      const totalTextHeight = displayLines.length * lineHeight
      const startY = textY - totalTextHeight / 2 + lineHeight / 2
      
      // Рисуем фон для текста
      const maxLineWidth = Math.max(...displayLines.map(line => ctx.measureText(line).width))
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
      ctx.fillRect(
        textX - maxLineWidth / 2 - 3,
        startY - lineHeight / 2 - 2,
        maxLineWidth + 6,
        totalTextHeight + 4
      )
      
      // Рисуем текст построчно
      ctx.fillStyle = '#000'
      displayLines.forEach((line, idx) => {
        ctx.fillText(line, textX, startY + idx * lineHeight)
      })
    }
    
    // Рисуем номер позиции в углу детали
    if (part.position_number) {
      const posNum = part.position_number.toString()
      ctx.fillStyle = '#000'
      ctx.font = 'bold 14px Arial'
      ctx.textAlign = 'left'
      ctx.textBaseline = 'top'
      
      // Фон для номера позиции
      const posMetrics = ctx.measureText(posNum)
      ctx.fillStyle = 'rgba(255, 255, 0, 0.9)'
      ctx.fillRect(
        offsetX + part.x * scale + 3,
        offsetY + part.y * scale + 3,
        posMetrics.width + 6,
        18
      )
      
      // Номер позиции
      ctx.fillStyle = '#000'
      ctx.fillText(posNum, offsetX + part.x * scale + 6, offsetY + part.y * scale + 5)
    }
    
    // Индикатор поворота
    if (part.rotated) {
      ctx.fillStyle = '#FF0000'
      ctx.font = '8px Arial'
      ctx.fillText('↻', offsetX + part.x * scale + 5, offsetY + part.y * scale + 25)
    }
  })
  
  // Подпись размеров листа
  ctx.fillStyle = '#666'
  ctx.font = '12px Arial'
  ctx.textAlign = 'left'
  ctx.fillText(
    `${props.sheetWidth}×${props.sheetHeight} мм`,
    offsetX + 5,
    offsetY + props.sheetHeight * scale - 5
  )
}

onMounted(() => {
  drawNesting()
})

watch(() => props.sheet, () => {
  drawNesting()
}, { deep: true })

watch(() => [props.sheetWidth, props.sheetHeight], () => {
  drawNesting()
})
</script>

<style scoped>
.nesting-visualization {
  margin-bottom: 16px;
}

.canvas-container {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: visible;
  background: #f5f5f5;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
}

.nesting-canvas {
  display: block;
  margin: 0 auto;
}
</style>

