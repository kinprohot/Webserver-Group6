/*
 * response.c - HTTP Response Engine & Directory Indexing Module
 * Author: Nguyen Dang Luan
 *
 * Responsibilities:
 * - Generate standard RFC1945 HTTP headers (Date, Server, Last-Modified, Content-Type, Content-Length)
 * - Handle conditional request header If-Modified-Since (return 304 Not Modified)
 * - Output HTTP Error responses (400, 403, 404, 500, 501)
 * - Serve static files (HTML, CSS, JS, Images, Plain text)
 * - Dynamic directory indexing (auto-generate HTML index when index.html is absent)
 */

#include "sws.h"

void send_response_header(int client_fd, int status_code, const char *status_msg,
                          const char *content_type, off_t content_length, time_t last_modified) {
    char header_buf[BUFFER_SIZE];
    char date_str[128];
    char lm_str[128];
    time_t now = time(NULL);

    struct tm tm_now, tm_lm;
    gmtime_r(&now, &tm_now);
    strftime(date_str, sizeof(date_str), "%a, %d %b %Y %H:%M:%S GMT", &tm_now);

    int offset = snprintf(header_buf, sizeof(header_buf),
                          "HTTP/1.0 %d %s\r\n"
                          "Date: %s\r\n"
                          "Server: %s\r\n",
                          status_code, status_msg, date_str, SERVER_NAME);

    if (last_modified > 0) {
        gmtime_r(&last_modified, &tm_lm);
        strftime(lm_str, sizeof(lm_str), "%a, %d %b %Y %H:%M:%S GMT", &tm_lm);
        offset += snprintf(header_buf + offset, sizeof(header_buf) - offset,
                           "Last-Modified: %s\r\n", lm_str);
    }

    if (content_type) {
        offset += snprintf(header_buf + offset, sizeof(header_buf) - offset,
                           "Content-Type: %s\r\n", content_type);
    }

    if (content_length >= 0) {
        offset += snprintf(header_buf + offset, sizeof(header_buf) - offset,
                           "Content-Length: %ld\r\n", (long)content_length);
    }

    offset += snprintf(header_buf + offset, sizeof(header_buf) - offset,
                       "Connection: close\r\n\r\n");

    write(client_fd, header_buf, offset);
}

void send_error_response(int client_fd, int status_code, const char *status_msg, const HttpRequest *req) {
    char body[1024];
    int body_len = snprintf(body, sizeof(body),
                           "<!DOCTYPE html>\n<html><head><title>%d %s</title></head>\n"
                           "<body style='font-family:sans-serif;text-align:center;padding:50px;'>\n"
                           "<h1>%d %s</h1>\n<p>sws/1.0 HTTP Server - Advanced Programming in UNIX Environment</p>\n"
                           "<hr><p>Team: Nguyen Hoang Luc (23IT151), Nguyen Xuan Lam, Nguyen Dang Luan, Vo Thi Quynh Linh</p>\n"
                           "</body></html>\n",
                           status_code, status_msg, status_code, status_msg);

    send_response_header(client_fd, status_code, status_msg, "text/html", body_len, 0);

    if (strcmp(req->method, "HEAD") != 0) {
        write(client_fd, body, body_len);
    }

    char first_line[256];
    snprintf(first_line, sizeof(first_line), "%s %s %s", req->method, req->uri, req->version);
    log_access(req->remote_ip, first_line, status_code, body_len);
}

void serve_static_file(int client_fd, const char *path, const HttpRequest *req) {
    struct stat st;
    if (stat(path, &st) < 0) {
        send_error_response(client_fd, 404, "Not Found", req);
        return;
    }

    /* Check If-Modified-Since header */
    if (strlen(req->if_modified_since) > 0) {
        struct tm tm_ims;
        memset(&tm_ims, 0, sizeof(tm_ims));
        if (strptime(req->if_modified_since, "%a, %d %b %Y %H:%M:%S GMT", &tm_ims) != NULL) {
            time_t ims_time = timegm(&tm_ims);
            if (st.st_mtime <= ims_time) {
                send_response_header(client_fd, 304, "Not Modified", NULL, -1, st.st_mtime);
                char first_line[256];
                snprintf(first_line, sizeof(first_line), "%s %s %s", req->method, req->uri, req->version);
                log_access(req->remote_ip, first_line, 304, 0);
                return;
            }
        }
    }

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        send_error_response(client_fd, 403, "Forbidden", req);
        return;
    }

    const char *mime = get_mime_type(path);
    send_response_header(client_fd, 200, "OK", mime, st.st_size, st.st_mtime);

    if (strcmp(req->method, "HEAD") != 0) {
        char buf[BUFFER_SIZE];
        ssize_t n;
        while ((n = read(fd, buf, sizeof(buf))) > 0) {
            if (write(client_fd, buf, n) < 0) break;
        }
    }

    close(fd);

    char first_line[256];
    snprintf(first_line, sizeof(first_line), "%s %s %s", req->method, req->uri, req->version);
    log_access(req->remote_ip, first_line, 200, st.st_size);
}

void serve_directory_index(int client_fd, const char *dir_path, const char *req_uri, const HttpRequest *req) {
    DIR *dir = opendir(dir_path);
    if (!dir) {
        send_error_response(client_fd, 403, "Forbidden", req);
        return;
    }

    char body[16384];
    int offset = snprintf(body, sizeof(body),
                          "<!DOCTYPE html>\n<html><head><title>Index of %s</title>\n"
                          "<style>body{font-family:monospace;padding:20px;} table{width:100%%;border-collapse:collapse;}"
                          "th,td{padding:8px;text-align:left;border-bottom:1px solid #ddd;} tr:hover{background:#f5f5f5;}</style>"
                          "</head><body>\n<h1>Index of %s</h1>\n<hr>\n"
                          "<table><tr><th>Name</th><th>Size</th><th>Last Modified</th></tr>\n",
                          req_uri, req_uri);

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue; /* Ignore hidden files starting with . */

        char full_entry_path[1024];
        snprintf(full_entry_path, sizeof(full_entry_path), "%s/%s", dir_path, entry->d_name);
        struct stat st;
        if (stat(full_entry_path, &st) == 0) {
            char size_str[32];
            if (S_ISDIR(st.st_mode)) {
                strcpy(size_str, "-");
            } else {
                snprintf(size_str, sizeof(size_str), "%ld B", (long)st.st_size);
            }

            char mtime_str[64];
            struct tm tm_m;
            localtime_r(&st.st_mtime, &tm_m);
            strftime(mtime_str, sizeof(mtime_str), "%Y-%m-%d %H:%M:%S", &tm_m);

            const char *slash = (req_uri[strlen(req_uri) - 1] == '/') ? "" : "/";
            offset += snprintf(body + offset, sizeof(body) - offset,
                               "<tr><td><a href='%s%s%s%s'>%s%s</a></td><td>%s</td><td>%s</td></tr>\n",
                               req_uri, slash, entry->d_name, S_ISDIR(st.st_mode) ? "/" : "",
                               entry->d_name, S_ISDIR(st.st_mode) ? "/" : "",
                               size_str, mtime_str);
        }
    }
    closedir(dir);

    offset += snprintf(body + offset, sizeof(body) - offset,
                       "</table>\n<hr>\n<p><em>sws/1.0 Server at %s</em></p>\n</body></html>\n",
                       SERVER_NAME);

    send_response_header(client_fd, 200, "OK", "text/html", offset, time(NULL));

    if (strcmp(req->method, "HEAD") != 0) {
        write(client_fd, body, offset);
    }

    char first_line[256];
    snprintf(first_line, sizeof(first_line), "%s %s %s", req->method, req->uri, req->version);
    log_access(req->remote_ip, first_line, 200, offset);
}
