/*
 * cgi.c - CGI Execution & Logging Subsystem
 * Author: Vo Thi Quynh Linh
 *
 * Responsibilities:
 * - RFC3875 Common Gateway Interface execution
 * - Setup CGI environment variables (REQUEST_METHOD, QUERY_STRING, SCRIPT_NAME, SERVER_PROTOCOL, etc.)
 * - Pipe stdout from CGI script to client socket descriptor
 * - MIME type detection based on file extensions
 * - Apache Common Log Format generator (%a %t "%r" %>s %b)
 */

#include "sws.h"

const char *get_mime_type(const char *path) {
    const char *dot = strrchr(path, '.');
    if (!dot) return "application/octet-stream";

    if (strcasecmp(dot, ".html") == 0 || strcasecmp(dot, ".htm") == 0) return "text/html";
    if (strcasecmp(dot, ".css") == 0) return "text/css";
    if (strcasecmp(dot, ".js") == 0) return "application/javascript";
    if (strcasecmp(dot, ".txt") == 0 || strcasecmp(dot, ".c") == 0 || strcasecmp(dot, ".h") == 0) return "text/plain";
    if (strcasecmp(dot, ".jpg") == 0 || strcasecmp(dot, ".jpeg") == 0) return "image/jpeg";
    if (strcasecmp(dot, ".png") == 0) return "image/png";
    if (strcasecmp(dot, ".gif") == 0) return "image/gif";
    if (strcasecmp(dot, ".pdf") == 0) return "application/pdf";
    if (strcasecmp(dot, ".json") == 0) return "application/json";

    return "text/plain";
}

void log_access(const char *remote_ip, const char *first_line, int status_code, off_t bytes_sent) {
    /* Format: %a %t "%r" %>s %b */
    char time_buf[64];
    time_t now = time(NULL);
    struct tm tm_gmt;
    gmtime_r(&now, &tm_gmt);
    strftime(time_buf, sizeof(time_buf), "%Y-%m-%dT%H:%M:%SZ", &tm_gmt);

    char log_entry[BUFFER_SIZE];
    int len = snprintf(log_entry, sizeof(log_entry), "%s %s \"%s\" %d %ld\n",
                       remote_ip, time_buf, first_line, status_code, (long)bytes_sent);

    if (config.debug) {
        printf("%s", log_entry);
        fflush(stdout);
    }

    if (config.log_fd >= 0) {
        write(config.log_fd, log_entry, len);
    }
}

void execute_cgi(int client_fd, const char *cgi_path, const HttpRequest *req) {
    struct stat st;
    if (stat(cgi_path, &st) < 0) {
        send_error_response(client_fd, 404, "Not Found", req);
        return;
    }

    /* Check executable permission */
    if (!(st.st_mode & S_IXUSR)) {
        send_error_response(client_fd, 403, "Forbidden", req);
        return;
    }

    int pipe_fd[2];
    if (pipe(pipe_fd) < 0) {
        send_error_response(client_fd, 500, "Internal Server Error", req);
        return;
    }

    pid_t pid = fork();
    if (pid < 0) {
        close(pipe_fd[0]);
        close(pipe_fd[1]);
        send_error_response(client_fd, 500, "Internal Server Error", req);
        return;
    }

    if (pid == 0) {
        /* Child: Setup CGI Environment & Execute */
        close(pipe_fd[0]);
        dup2(pipe_fd[1], STDOUT_FILENO);
        close(pipe_fd[1]);

        /* RFC3875 Environment Variables */
        setenv("REQUEST_METHOD", req->method, 1);
        setenv("QUERY_STRING", req->cgi_query, 1);
        setenv("SERVER_PROTOCOL", "HTTP/1.0", 1);
        setenv("SERVER_SOFTWARE", SERVER_NAME, 1);
        setenv("REMOTE_ADDR", req->remote_ip, 1);
        setenv("SCRIPT_NAME", req->uri, 1);
        setenv("GATEWAY_INTERFACE", "CGI/1.1", 1);

        char port_str[16];
        snprintf(port_str, sizeof(port_str), "%d", config.port);
        setenv("SERVER_PORT", port_str, 1);

        execl(cgi_path, cgi_path, (char *)NULL);
        perror("execl cgi");
        exit(EXIT_FAILURE);
    }

    /* Parent Process */
    close(pipe_fd[1]);

    /* Send initial HTTP/1.0 200 OK header */
    send_response_header(client_fd, 200, "OK", NULL, -1, 0);

    char buf[BUFFER_SIZE];
    ssize_t n;
    off_t total_bytes = 0;
    while ((n = read(pipe_fd[0], buf, sizeof(buf))) > 0) {
        total_bytes += n;
        write(client_fd, buf, n);
    }
    close(pipe_fd[0]);
    waitpid(pid, NULL, 0);

    char first_line[256];
    snprintf(first_line, sizeof(first_line), "%s %s %s", req->method, req->uri, req->version);
    log_access(req->remote_ip, first_line, 200, total_bytes);
}
