<script setup lang="ts">
import RecordsTable from "../components/tables/records/RecordsTable.vue";
import MainLayout from "../layouts/MainLayout.vue";
</script>

<template>
    <MainLayout fill-height>
        <RecordsTable
            global
            zoneName=""
        />
    </MainLayout>
</template>
