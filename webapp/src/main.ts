import { createApp } from "vue";
import router from "./router.ts";
import App from "./App.vue";

import "./styles/main.css";

import "vfonts/Lato.css";
import "vfonts/FiraCode.css";
import { pinia } from "./pinia.ts";

const app = createApp(App);

app.use(pinia);
app.use(router);
app.mount("#app");
