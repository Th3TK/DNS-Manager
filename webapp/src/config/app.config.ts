const API_PORT = Number(import.meta.env.VITE_API_PORT ?? 9000);
const HTTPS_ENABLED = import.meta.env.VITE_HTTPS_ENABLED?.toUpperCase() === "TRUE";

const protocol = HTTPS_ENABLED ? "https" : "http";
const wsProtocol = HTTPS_ENABLED ? "wss" : "ws";

const API_HOST = `${window.location.hostname}:${API_PORT}`;

const APP_CONFIG = {
    API_URL_HTTP: `${protocol}://${API_HOST}/api/`,
    API_URL_WEBSOCKET: `${wsProtocol}://${API_HOST}/api/`,
};

export default APP_CONFIG;
