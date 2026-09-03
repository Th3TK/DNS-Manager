export const formatRemainingTime = (deletionDate: string | Date): string => {
    const trashIntervalSeconds = Number(import.meta.env.VITE_ITEM_TRASH_INTERVAL_SECONDS);

    const permanentDeletionDate = new Date(deletionDate).getTime() + trashIntervalSeconds * 1000;

    const remainingSeconds = Math.max(0, Math.floor((permanentDeletionDate - Date.now()) / 1000));

    if (remainingSeconds < 60) {
        return "Less than 1 minute";
    }

    if (remainingSeconds < 3600) {
        const roundedMinutes = Math.floor(remainingSeconds / 60);
        return `${roundedMinutes} minute${roundedMinutes !== 1 ? "s" : ""}`;
    }

    if (remainingSeconds < 86400) {
        const roundedHours = Math.floor(remainingSeconds / 3600);
        return `${roundedHours} hour${roundedHours !== 1 ? "s" : ""}`;
    }

    const roundedDays = Math.floor(remainingSeconds / 86400);
    return `${roundedDays} day${roundedDays !== 1 ? "s" : ""}`;
};

export const formatTime = (seconds: number) => {
    if (seconds < 60) {
        return `${seconds} second${seconds !== 1 ? "s" : ""}`;
    }

    if (seconds < 3600) {
        const roundedMinutes = Math.floor(seconds / 60);
        return `${roundedMinutes} minute${roundedMinutes !== 1 ? "s" : ""}`;
    }

    if (seconds < 86400) {
        const roundedHours = Math.floor(seconds / 3600);
        return `${roundedHours} hour${roundedHours !== 1 ? "s" : ""}`;
    }

    const roundedDays = Math.floor(seconds / 86400);
    return `${roundedDays} day${roundedDays !== 1 ? "s" : ""}`;
};
