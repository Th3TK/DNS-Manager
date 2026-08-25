type ErrorDetails = {
    title: string;
    message: string;
};

export const HTTP_ERROR_NOTIFICATIONS: Partial<Record<number, ErrorDetails>> = {
    400: {
        title: "Bad Request",
        message: "The request was invalid.",
    },
    401: {
        title: "Unauthorized",
        message: "You are not authorized to perform this action.",
    },
    403: {
        title: "Forbidden",
        message: "You do not have permission to perform this action.",
    },
    404: {
        title: "Not Found",
        message: "The requested resource could not be found.",
    },
    405: {
        title: "Method Not Allowed",
        message: "This operation is not allowed.",
    },
    408: {
        title: "Request Timeout",
        message: "The request took too long to complete.",
    },
    409: {
        title: "Conflict",
        message: "The request conflicts with the current state of the resource.",
    },
    413: {
        title: "Content Too Large",
        message: "The request data is too large.",
    },
    415: {
        title: "Unsupported Media Type",
        message: "The requested data format is not supported.",
    },
    422: {
        title: "Unprocessable Content",
        message: "The request could not be processed.",
    },
    429: {
        title: "Too Many Requests",
        message: "Too many requests were sent. Please try again later.",
    },
    500: {
        title: "Internal Server Error",
        message: "The server encountered an unexpected error.",
    },
    501: {
        title: "Not Implemented",
        message: "The server does not support this operation.",
    },
    502: {
        title: "Bad Gateway",
        message: "The server received an invalid response from an upstream server.",
    },
    503: {
        title: "Service Unavailable",
        message: "The service is temporarily unavailable.",
    },
    504: {
        title: "Gateway Timeout",
        message: "The server did not receive a timely response.",
    },
};

export const AXIOS_ERROR_NOTIFICATIONS: Record<string, ErrorDetails> = {
    ERR_BAD_OPTION_VALUE: {
        title: "Invalid Configuration",
        message: "An invalid value was provided in the Axios configuration.",
    },

    ERR_BAD_OPTION: {
        title: "Invalid Configuration",
        message: "An invalid option was provided in the Axios configuration.",
    },

    ECONNABORTED: {
        title: "Request Aborted",
        message: "The request was aborted or timed out.",
    },

    ETIMEDOUT: {
        title: "Request Timeout",
        message: "The request timed out before a response was received.",
    },

    ERR_NETWORK: {
        title: "Network Error",
        message: "A network error prevented the request from completing.",
    },

    ERR_FR_TOO_MANY_REDIRECTS: {
        title: "Too Many Redirects",
        message: "The request was redirected too many times.",
    },

    ERR_DEPRECATED: {
        title: "Deprecated Feature",
        message: "The request uses a deprecated Axios feature or method.",
    },

    ERR_BAD_RESPONSE: {
        title: "Invalid Response",
        message: "The server returned a response that could not be processed.",
    },

    ERR_BAD_REQUEST: {
        title: "Bad Request",
        message: "The request was invalid or contained missing or incorrect parameters.",
    },

    ERR_CANCELED: {
        title: "Request Canceled",
        message: "The request was canceled.",
    },

    ERR_NOT_SUPPORT: {
        title: "Not Supported",
        message: "This feature or operation is not supported in the current environment.",
    },

    ERR_INVALID_URL: {
        title: "Invalid URL",
        message: "The request URL is invalid.",
    },

    ERR_FORM_DATA_DEPTH_EXCEEDED: {
        title: "Request Data Too Deep",
        message: "The request data exceeds the maximum allowed serialization depth.",
    },
};

export const DEFAULT_ERROR_NOTIFICATION: ErrorDetails = {
    title: "Error Occured",
    message: "Unknown error occured.",
};
