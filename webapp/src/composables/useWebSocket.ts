import { ref } from "vue";
import { logout, refreshTokens } from "../services/api";
import { combinePaths } from "../utils/url";
import { useRouter } from "vue-router";
import { useAuthenticationStore } from "../stores/useAuthenticationStore";
import APP_CONFIG from "../config/app.config";

export function useWebSocket<T>(path: string) {
    const authentication = useAuthenticationStore();
    const router = useRouter();

    const socket = ref<WebSocket | null>(null);
    const connected = ref(false);
    const lastMessage = ref<T | null>(null);

    const onUnauthorized = () => {
        router.push("/login");
        authentication.refresh();

        logout();
    };

    const connect = () => {
        if (connected.value) return;

        socket.value = new WebSocket(combinePaths(APP_CONFIG.API_URL_WEBSOCKET, path));

        socket.value.onopen = () => {
            connected.value = true;
        };

        socket.value.onmessage = (event) => {
            lastMessage.value = JSON.parse(event.data);
        };

        socket.value.onclose = (event: CloseEvent) => {
            connected.value = false;

            if (event.code !== 1008) return;

            refreshTokens()
                .then(connect)
                .catch(() => onUnauthorized);
        };
    };

    const send = (data: unknown) => {
        socket.value?.send(JSON.stringify(data));
    };

    const disconnect = () => {
        socket.value?.close();
    };

    return {
        socket,
        connected,
        connect,
        send,
        lastMessage,
        disconnect,
    };
}
