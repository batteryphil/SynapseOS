/*
 * PRIME Moment Attention: Embedded HTTP / REST Server Header
 * ==========================================================
 * Provides an OpenAI-compatible HTTP/1.1 API with SSE streaming.
 */

#ifndef PRIME_SERVER_H
#define PRIME_SERVER_H

#include "prime_moment.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Starts the embedded HTTP REST server on the specified port.
 * Runs an event loop processing requests until SIGINT/SIGTERM.
 *
 * Supported endpoints:
 *   GET  /health
 *   GET  /v1/models
 *   POST /v1/chat/completions (supports stream: true / false)
 *   POST /v1/completions
 */
int prime_server_start(const prime_config_t *cfg, int port);

#ifdef __cplusplus
}
#endif

#endif /* PRIME_SERVER_H */
