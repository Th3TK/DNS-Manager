import _ from "lodash";

export const combinePaths = (...paths: string[]) => `${paths.map((p) => _.trim(p, "/")).join("/")}`;
