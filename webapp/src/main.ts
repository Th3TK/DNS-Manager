import { createApp } from "vue";
import { router } from "./router.ts";
import App from "./App.vue";

import "./styles/main.css";

import "vfonts/Lato.css";
import "vfonts/FiraCode.css";

createApp(App).use(router).mount("#app");
