import * as _modelcontextprotocol_sdk_server from '@modelcontextprotocol/sdk/server';
import { z } from 'zod';

declare const serverConfigSchema: z.ZodObject<{
    apiKey: z.ZodString;
}, "strip", z.ZodTypeAny, {
    apiKey: string;
}, {
    apiKey: string;
}>;
declare const configSchema: z.ZodObject<{
    apiKey: z.ZodString;
}, "strip", z.ZodTypeAny, {
    apiKey: string;
}, {
    apiKey: string;
}>;
type ServerConfig = z.infer<typeof serverConfigSchema>;
declare function createServer({ config }: {
    config: ServerConfig;
}): _modelcontextprotocol_sdk_server.Server<{
    method: string;
    params?: {
        [x: string]: unknown;
        _meta?: {
            [x: string]: unknown;
            progressToken?: string | number | undefined;
        } | undefined;
    } | undefined;
}, {
    method: string;
    params?: {
        [x: string]: unknown;
        _meta?: {
            [x: string]: unknown;
        } | undefined;
    } | undefined;
}, {
    [x: string]: unknown;
    _meta?: {
        [x: string]: unknown;
    } | undefined;
}>;

export { configSchema, createServer as default };
