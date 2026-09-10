import { createApp } from "vue";
import { pinia } from "./config/pinia.config.ts";
import router from "./config/router.config.ts";
import App from "./App.vue";

import "./styles/main.css";

import "vfonts/Lato.css";
import "vfonts/FiraCode.css";

const app = createApp(App);

app.use(pinia);
app.use(router);
app.mount("#app");
