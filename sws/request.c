/*
 * request.c - HTTP Request Parsing & Path Resolution Module
 * Author: Nguyen Xuan Lam
 *
 * Responsibilities:
 * - Read incoming HTTP byte stream line by line
 * - Parse Request-Line: Method (GET, HEAD), Request-URI, HTTP-Version (HTTP/1.0, HTTP/1.1)
 * - Parse Request Headers: If-Modified-Since
 * - Path traversal security check (prevent ../ escape from docroot)
 * - Map ~user/ to /home/user/sws/
 * - Identify /cgi-bin requests
 */

#include "sws.h"

int parse_http_request(int client_fd, HttpRequest *req) {
    char line[BUFFER_SIZE];
    int line_num = 0;

    /* Read first line: Method URI Version */
    FILE *stream = fdopen(dup(client_fd), "r");
    if (!stream) {
        send_error_response(client_fd, 500, "Internal Server Error", req);
        return -1;
    }

    while (fgets(line, sizeof(line), stream)) {
        /* Strip CRLF */
        char *eol = strpbrk(line, "\r\n");
        if (eol) *eol = '\0';

        if (line_num == 0) {
            /* Empty request line */
            if (strlen(line) == 0) {
                fclose(stream);
                send_error_response(client_fd, 400, "Bad Request", req);
                return -1;
            }

            char raw_uri[1024];
            int n = sscanf(line, "%15s %1023s %15s", req->method, raw_uri, req->version);
            if (n < 2) {
                fclose(stream);
                send_error_response(client_fd, 400, "Bad Request", req);
                return -1;
            }
            if (n == 2) {
                /* Simple request (HTTP/0.9 format), default to HTTP/1.0 */
                strcpy(req->version, "HTTP/1.0");
            }

            /* Only GET and HEAD are supported */
            if (strcmp(req->method, "GET") != 0 && strcmp(req->method, "HEAD") != 0) {
                fclose(stream);
                send_error_response(client_fd, 501, "Not Implemented", req);
                return -1;
            }

            /* Separate query string if present */
            char *q = strchr(raw_uri, '?');
            if (q) {
                *q = '\0';
                strncpy(req->cgi_query, q + 1, sizeof(req->cgi_query) - 1);
            }
            strncpy(req->uri, raw_uri, sizeof(req->uri) - 1);

            /* Check if URI begins with /cgi-bin */
            if (strncmp(req->uri, "/cgi-bin/", 9) == 0 || strcmp(req->uri, "/cgi-bin") == 0) {
                req->is_cgi = 1;
            }

            line_num++;
        } else {
            /* Empty line indicates end of HTTP headers */
            if (strlen(line) == 0) break;

            /* Parse headers */
            if (strncasecmp(line, "If-Modified-Since:", 18) == 0) {
                char *val = line + 18;
                while (*val == ' ' || *val == '\t') val++;
                strncpy(req->if_modified_since, val, sizeof(req->if_modified_since) - 1);
            }
        }
    }

    fclose(stream);
    return 0;
}

int resolve_path(const char *uri, char *resolved_path, size_t max_len, HttpRequest *req) {
    (void)req;

    /* Prevent directory traversal attack using /../ */
    if (strstr(uri, "/../") != NULL || strcmp(uri, "..") == 0 || strncmp(uri, "../", 3) == 0 ||
        (strlen(uri) >= 3 && strcmp(uri + strlen(uri) - 3, "/..") == 0)) {
        return -1;
    }

    /* Check for User Directories: /~user/ or /~user */
    if (strncmp(uri, "/~", 2) == 0) {
        char username[128];
        const char *slash = strchr(uri + 2, '/');
        size_t user_len = slash ? (size_t)(slash - (uri + 2)) : strlen(uri + 2);
        if (user_len >= sizeof(username)) return -1;

        strncpy(username, uri + 2, user_len);
        username[user_len] = '\0';

        struct passwd *pw = getpwnam(username);
        if (!pw) return -1;

        const char *subpath = slash ? slash : "";
        snprintf(resolved_path, max_len, "%s/sws%s", pw->pw_dir, subpath);
        return 0;
    }

    /* Normal document root path resolution */
    if (strcmp(uri, "/") == 0) {
        snprintf(resolved_path, max_len, "%s", config.doc_root);
    } else {
        snprintf(resolved_path, max_len, "%s%s", config.doc_root, uri);
    }

    return 0;
}
