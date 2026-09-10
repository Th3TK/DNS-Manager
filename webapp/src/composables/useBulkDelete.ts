// composables/useBulkDelete.ts

import { h } from "vue";
import _ from "lodash";
import type { AxiosError } from "axios";
import { NButton, NIcon, useNotification } from "naive-ui";
import DeletionResult from "../components/display/DeletionResult.vue";
import { Trash } from "@vicons/tabler";

export default function useBulkDelete() {
    const notification = useNotification();

    const onBulkDelete = async <T extends Record<string, any>>(
        objects: T[],
        deletionFunc: (object: T) => Promise<unknown>,
        objectName: string,
        keyField: keyof T,
    ) => {
        const batchSize = 10;
        const failed: { object: T; error: AxiosError }[] = [];
        const controller = new AbortController();

        let succeeded = 0;
        let cancelled = false;

        const notificationInstance = notification.info({
            title: `${_.capitalize(objectName)} bulk deletion`,
            content: `Deleted 0 / ${objects.length}`,
            duration: 0,
            closable: true,
            onClose: () => controller.abort(),
        });

        for (const batch of _.chunk(objects, batchSize)) {
            if (controller.signal.aborted) {
                cancelled = true;
                break;
            }

            const results = await Promise.allSettled(batch.map((object) => deletionFunc(object)));

            results.forEach((result, index) => {
                if (result.status === "fulfilled") {
                    succeeded++;
                } else {
                    failed.push({
                        object: batch[index],
                        error: result.reason as AxiosError,
                    });
                }
            });

            notificationInstance.content = `Status: ${succeeded + failed.length} / ${objects.length}`;
        }

        if (cancelled) {
            notification.warning({
                title: `${_.capitalize(objectName)} deletion cancelled`,
                content: `Deleted ${succeeded} / ${objects.length}`,
                duration: 5000,
            });
        }

        if (failed.length) {
            notificationInstance.type = "warning";
            notificationInstance.title = `${_.capitalize(objectName)} deletion completed with errors`;
            notificationInstance.content = () =>
                h(DeletionResult, {
                    keyField: keyField as string,
                    succeeded,
                    failed,
                });
        } else if (!cancelled) {
            notificationInstance.type = "success";
            notificationInstance.title = `${_.capitalize(objectName)} deletion completed`;
            notificationInstance.content = `${succeeded} ${objectName}${succeeded === 1 ? "" : "s"} deleted`;

            setTimeout(() => notificationInstance.destroy(), 5000);
        }

        return {
            succeeded,
            failed,
            cancelled,
        };
    };

    return { onBulkDelete };
}
