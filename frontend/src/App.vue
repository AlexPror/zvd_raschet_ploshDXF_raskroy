<template>
  <v-app>
    <v-app-bar color="primary" dark>
      <v-app-bar-title>
        📐 ZVD Калькулятор Площадей
      </v-app-bar-title>
    </v-app-bar>

    <v-main>
      <v-container>
        <AreaCalculator />
      </v-container>
    </v-main>

    <v-footer color="primary" dark app>
      <v-spacer></v-spacer>
      <span>&copy; 2025 ZVD GROUP</span>
      <v-spacer></v-spacer>
    </v-footer>
  </v-app>
</template>

<script setup>
import AreaCalculator from './components/AreaCalculator.vue'
</script>

<style>
/* Глобальные стили для печати */
@media print {
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
  }
  
  /* Скрываем хедер и футер */
  .v-app-bar,
  .v-footer {
    display: none !important;
    margin: 0 !important;
    padding: 0 !important;
    height: 0 !important;
  }
  
  /* Убираем отступы между хедером/футером и контентом */
  .v-main {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
  }
  
  /* Контейнер без отступов сверху и снизу */
  .v-container {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
  }
}
</style>