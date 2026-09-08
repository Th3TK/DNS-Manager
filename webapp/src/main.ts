import { createApp } from "vue";
import { createPinia } from "pinia";
import router from "./router.ts";
import App from "./App.vue";

import "./styles/main.css";

import "vfonts/Lato.css";
import "vfonts/FiraCode.css";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.mount("#app");
