/// <reference types="vite/client" />

declare module "*.vue" {
    import type { DefineComponent } from "vue";

    const component: DefineComponent;
    export default component;
}

interface ImportMetaEnv {
    readonly VITE_HTTPS_ENABLED: string;
    readonly VITE_API_PORT: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}
