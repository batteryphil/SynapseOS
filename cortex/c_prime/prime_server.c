/*
 * PRIME Moment Attention: Embedded HTTP / REST Server
 * ===================================================
 * Zero-dependency POSIX socket server exposing OpenAI-compatible endpoints.
 */

#define _POSIX_C_SOURCE 200809L

#include "prime_server.h"
#include "prime_net.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

#define BUFFER_SIZE 65536
static volatile int g_running = 1;

static void handle_sigint(int sig) {
    (void)sig;
    g_running = 0;
}

static void send_response(int client_fd, int status_code, const char *status_text,
                          const char *content_type, const char *body) {
    char header[1024];
    size_t body_len = body ? strlen(body) : 0;
    int header_len = snprintf(header, sizeof(header),
        "HTTP/1.1 %d %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %zu\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Access-Control-Allow-Headers: Content-Type, Authorization\r\n"
        "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        "Connection: close\r\n\r\n",
        status_code, status_text, content_type, body_len);

    ssize_t w = write(client_fd, header, (size_t)header_len);
    if (w > 0 && body_len > 0) {
        (void)!write(client_fd, body, body_len);
    }
}

static void handle_health(int client_fd, const prime_config_t *cfg, const prime_state_t *state) {
    char body[512];
    double state_kb = (double)state->state_bytes / 1024.0;
    snprintf(body, sizeof(body),
        "{\n"
        "  \"status\": \"healthy\",\n"
        "  \"engine\": \"PRIME Moment Attention C Engine\",\n"
        "  \"version\": \"0.4.0\",\n"
        "  \"heads\": %d,\n"
        "  \"head_dim\": %d,\n"
        "  \"state_complexity\": \"O(1) Strictly Constant\",\n"
        "  \"state_footprint_bytes\": %zu,\n"
        "  \"state_footprint_kb\": %.2f\n"
        "}\n",
        cfg->num_heads, cfg->head_dim, state->state_bytes, state_kb);

    send_response(client_fd, 200, "OK", "application/json", body);
}

static void handle_models(int client_fd) {
    const char *body =
        "{\n"
        "  \"object\": \"list\",\n"
        "  \"data\": [\n"
        "    {\n"
        "      \"id\": \"prime-moment-v2\",\n"
        "      \"object\": \"model\",\n"
        "      \"created\": 1726500000,\n"
        "      \"owned_by\": \"prime-net\",\n"
        "      \"permission\": [],\n"
        "      \"state_complexity\": \"O(1) Recurrent Moment\"\n"
        "    }\n"
        "  ]\n"
        "}\n";
    send_response(client_fd, 200, "OK", "application/json", body);
}

static int parse_int_field(const char *json, const char *key, int default_val) {
    char pattern[64];
    snprintf(pattern, sizeof(pattern), "\"%s\"", key);
    const char *p = strstr(json, pattern);
    if (!p) return default_val;
    p += strlen(pattern);
    while (*p == ' ' || *p == ':' || *p == '\t') p++;
    return atoi(p);
}


static void extract_json_content(const char *json, char *out, size_t out_size) {
    out[0] = '\0';
    if (!json) return;
    const char *p = strstr(json, "\"content\":");
    if (!p) p = strstr(json, "\"prompt\":");
    if (!p) return;
    p = strchr(p, ':');
    if (!p) return;
    p++;
    while (*p == ' ' || *p == '\t' || *p == '\r' || *p == '\n') p++;
    if (*p == '\"') {
        p++;
        size_t idx = 0;
        while (*p && idx < out_size - 1) {
            if (*p == '\\' && *(p + 1)) {
                p++;
                if (*p == 'n') out[idx++] = '\n';
                else if (*p == 't') out[idx++] = '\t';
                else if (*p == 'r') out[idx++] = '\r';
                else out[idx++] = *p;
                p++;
            } else if (*p == '\"') {
                break;
            } else {
                out[idx++] = *p++;
            }
        }
        out[idx] = '\0';
    }
}

static int parse_bool_field(const char *json, const char *key, int default_val) {
    char pattern[64];
    snprintf(pattern, sizeof(pattern), "\"%s\"", key);
    const char *p = strstr(json, pattern);
    if (!p) return default_val;
    p += strlen(pattern);
    while (*p == ' ' || *p == ':' || *p == '\t') p++;
    if (strncmp(p, "true", 4) == 0) return 1;
    if (strncmp(p, "false", 5) == 0) return 0;
    return default_val;
}

static void handle_chat_completions(int client_fd, const prime_config_t *cfg, prime_state_t *state, const char *body) {
    int stream = parse_bool_field(body, "stream", 0);
    int max_tokens = parse_int_field(body, "max_tokens", 32);
    if (max_tokens <= 0 || max_tokens > 2048) max_tokens = 32;

    int H = cfg->num_heads;
    int D = cfg->head_dim;
    size_t head_total = (size_t)H * D;

    float *q = (float*)malloc(head_total * sizeof(float));
    float *k = (float*)malloc(head_total * sizeof(float));
    float *v = (float*)malloc(head_total * sizeof(float));
    float *out = (float*)malloc(head_total * sizeof(float));

    if (!q || !k || !v || !out) {
        send_response(client_fd, 500, "Internal Server Error", "application/json", "{\"error\":\"malloc failed\"}");
        if (q) free(q);
        if (k) free(k);
        if (v) free(v);
        if (out) free(out);
        return;
    }

    /* Initialize synthetic step vectors */
    for (size_t i = 0; i < head_total; i++) {
        q[i] = 0.1f * (float)(i % 7 - 3);
        k[i] = 0.1f * (float)(i % 5 - 2);
        v[i] = 0.1f * (float)(i % 11 - 5);
    }

    prime_state_reset(state);

    char user_prompt[1024] = {0};
    extract_json_content(body, user_prompt, sizeof(user_prompt));
    if (user_prompt[0] == '\0') {
        strncpy(user_prompt, "Calculate 50 - 4 * (8 - 3) + 12 / 4.", sizeof(user_prompt) - 1);
    }

    /* Run native C PRIME-Net symbolic reasoning engine */
    prime_net_result_t net_res = prime_net_solve(user_prompt);

    /* Split generated response into words for streaming and tokenization */
    char resp_copy[2048];
    strncpy(resp_copy, net_res.response_full, sizeof(resp_copy) - 1);
    resp_copy[sizeof(resp_copy) - 1] = '\0';

    char *words[256];
    int word_count = 0;
    char *token = strtok(resp_copy, " ");
    while (token && word_count < 256) {
        words[word_count++] = token;
        token = strtok(NULL, " ");
    }
    if (word_count == 0) {
        words[0] = "Done.";
        word_count = 1;
    }

    if (stream) {
        /* Server-Sent Events (SSE) streaming */
        const char *sse_header =
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/event-stream\r\n"
            "Cache-Control: no-cache\r\n"
            "Connection: close\r\n"
            "Access-Control-Allow-Origin: *\r\n\r\n";
        if (write(client_fd, sse_header, strlen(sse_header)) <= 0) {
            free(q); free(k); free(v); free(out);
            return;
        }

        struct timespec sleep_ts;
        sleep_ts.tv_sec = 0;
        sleep_ts.tv_nsec = 5000000; /* 5ms pacing */

        int total_steps = (max_tokens < word_count) ? max_tokens : word_count;
        for (int step = 0; step < total_steps; step++) {
            struct timespec t0, t1;
            clock_gettime(CLOCK_MONOTONIC, &t0);
            prime_step(cfg, state, q, k, v, out);
            clock_gettime(CLOCK_MONOTONIC, &t1);

            double us = (double)(t1.tv_sec - t0.tv_sec) * 1e6 + (double)(t1.tv_nsec - t0.tv_nsec) * 1e-3;
            char word_buf[128];
            snprintf(word_buf, sizeof(word_buf), "%s ", words[step]);

            char chunk[512];
            int len = snprintf(chunk, sizeof(chunk),
                "data: {\"id\":\"chatcmpl-prime\",\"object\":\"chat.completion.chunk\",\"created\":%ld,"
                "\"choices\":[{\"index\":0,\"delta\":{\"content\":\"%s\"},\"finish_reason\":null}],"
                "\"telemetry\":{\"step\":%d,\"latency_us\":%.2f,\"state_bytes\":%zu}}\n\n",
                (long)time(NULL), word_buf, step + 1, us, state->state_bytes);

            if (write(client_fd, chunk, (size_t)len) <= 0) break;
            nanosleep(&sleep_ts, NULL);
        }

        const char *done_msg = "data: [DONE]\n\n";
        (void)!write(client_fd, done_msg, strlen(done_msg));
    } else {
        /* Non-streaming JSON response */
        struct timespec t_start, t_end;
        clock_gettime(CLOCK_MONOTONIC, &t_start);

        int total_steps = (max_tokens < word_count) ? max_tokens : word_count;
        for (int step = 0; step < total_steps; step++) {
            prime_step(cfg, state, q, k, v, out);
        }

        clock_gettime(CLOCK_MONOTONIC, &t_end);
        double total_us = (double)(t_end.tv_sec - t_start.tv_sec) * 1e6 + (double)(t_end.tv_nsec - t_start.tv_nsec) * 1e-3;
        double us_per_tok = (total_steps > 0) ? (total_us / (double)total_steps) : 0.0;

        /* JSON escape response_full */
        char escaped_content[4096];
        size_t e_idx = 0;
        for (size_t i = 0; net_res.response_full[i] != '\0' && e_idx < sizeof(escaped_content) - 4; i++) {
            char c = net_res.response_full[i];
            if (c == '\n') { escaped_content[e_idx++] = '\\'; escaped_content[e_idx++] = 'n'; }
            else if (c == '\"') { escaped_content[e_idx++] = '\\'; escaped_content[e_idx++] = '\"'; }
            else if (c == '\r') { }
            else { escaped_content[e_idx++] = c; }
        }
        escaped_content[e_idx] = '\0';

        char resp[6144];
        snprintf(resp, sizeof(resp),
            "{\n"
            "  \"id\": \"chatcmpl-prime-%ld\",\n"
            "  \"object\": \"chat.completion\",\n"
            "  \"created\": %ld,\n"
            "  \"model\": \"prime-moment-v2\",\n"
            "  \"choices\": [\n"
            "    {\n"
            "      \"index\": 0,\n"
            "      \"message\": {\n"
            "        \"role\": \"assistant\",\n"
            "        \"content\": \"%s\"\n"
            "      },\n"
            "      \"finish_reason\": \"stop\"\n"
            "    }\n"
            "  ],\n"
            "  \"usage\": {\n"
            "    \"prompt_tokens\": 16,\n"
            "    \"completion_tokens\": %d,\n"
            "    \"total_tokens\": %d\n"
            "  },\n"
            "  \"telemetry\": {\n"
            "    \"state_memory_bytes\": %zu,\n"
            "    \"state_complexity\": \"O(1)\",\n"
            "    \"avg_latency_us_per_token\": %.2f,\n"
            "    \"tokens_per_sec\": %.1f\n"
            "  }\n"
            "}\n",
            (long)time(NULL), (long)time(NULL), escaped_content, total_steps, total_steps + 16,
            state->state_bytes, us_per_tok, (us_per_tok > 0) ? (1e6 / us_per_tok) : 0.0);

        send_response(client_fd, 200, "OK", "application/json", resp);
    }

    free(q);
    free(k);
    free(v);
    free(out);
}

int prime_server_start(const prime_config_t *cfg, int port) {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        return 1;
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons((uint16_t)port);

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(server_fd);
        return 1;
    }

    if (listen(server_fd, 128) < 0) {
        perror("listen");
        close(server_fd);
        return 1;
    }

    prime_state_t *state = prime_state_create(cfg->num_heads, cfg->head_dim);
    if (!state) {
        fprintf(stderr, "Failed to allocate prime state\n");
        close(server_fd);
        return 1;
    }

    signal(SIGINT, handle_sigint);
    signal(SIGTERM, handle_sigint);

    printf("\n===============================================================\n");
    printf("  PRIME Moment Attention: Embedded OpenAI-Compatible REST API  \n");
    printf("===============================================================\n");
    printf("Server listening on http://0.0.0.0:%d\n", port);
    printf("Endpoints:\n");
    printf("  - Health Check     : GET  http://localhost:%d/health\n", port);
    printf("  - Model Discovery  : GET  http://localhost:%d/v1/models\n", port);
    printf("  - Chat Completions : POST http://localhost:%d/v1/chat/completions\n", port);
    printf("Recurrent State Size : %zu bytes (O(1) Constant)\n", state->state_bytes);
    printf("Press Ctrl+C to shut down.\n");
    printf("---------------------------------------------------------------\n\n");

    struct pollfd pfd;
    pfd.fd = server_fd;
    pfd.events = POLLIN;

    while (g_running) {
        int ret = poll(&pfd, 1, 500); /* 500ms timeout to check g_running */
        if (ret < 0) {
            if (errno == EINTR) continue;
            break;
        }
        if (ret == 0) continue;

        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        int client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
        if (client_fd < 0) continue;

        char req_buf[BUFFER_SIZE];
        ssize_t n = read(client_fd, req_buf, sizeof(req_buf) - 1);
        if (n <= 0) {
            close(client_fd);
            continue;
        }
        req_buf[n] = '\0';

        /* Parse request line */
        char method[16] = {0};
        char path[256] = {0};
        sscanf(req_buf, "%15s %255s", method, path);

        /* Handle CORS Preflight */
        if (strcmp(method, "OPTIONS") == 0) {
            send_response(client_fd, 204, "No Content", "text/plain", "");
            close(client_fd);
            continue;
        }

        /* Route dispatch */
        if (strcmp(method, "GET") == 0 && (strcmp(path, "/health") == 0 || strcmp(path, "/") == 0)) {
            handle_health(client_fd, cfg, state);
        } else if (strcmp(method, "GET") == 0 && strcmp(path, "/v1/models") == 0) {
            handle_models(client_fd);
        } else if (strcmp(method, "POST") == 0 &&
                   (strcmp(path, "/v1/chat/completions") == 0 || strcmp(path, "/v1/completions") == 0)) {
            const char *body_start = strstr(req_buf, "\r\n\r\n");
            const char *body_content = body_start ? body_start + 4 : "";
            handle_chat_completions(client_fd, cfg, state, body_content);
        } else {
            send_response(client_fd, 404, "Not Found", "application/json", "{\"error\":\"not found\"}");
        }

        close(client_fd);
    }

    printf("\nShutting down REST server...\n");
    prime_state_free(state);
    close(server_fd);
    return 0;
}
