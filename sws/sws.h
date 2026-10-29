#ifndef SWS_H
#define SWS_H

#ifndef _XOPEN_SOURCE
#define _XOPEN_SOURCE 700
#endif

#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#endif

#ifndef _DEFAULT_SOURCE
#define _DEFAULT_SOURCE
#endif

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <time.h>
#include <dirent.h>
#include <signal.h>
#include <pwd.h>

#define SERVER_NAME "sws/1.0 (Advanced Programming in the UNIX Environment - Team NguyenHoangLuc)"
#define DEFAULT_PORT 8080
#define BUFFER_SIZE 8192
#define PATH_MAX_LEN 2048

/* Forward declaration of strptime */
char *strptime(const char *s, const char *format, struct tm *tm);

/* Global server configuration options */
typedef struct {
    int debug;              /* -d debug mode (no daemonize, single connection, log stdout) */
    char *cgi_dir;          /* -c directory for CGI execution */
    char *bind_address;     /* -i IP address to bind */
    char *log_file;         /* -l log file path */
    int port;               /* -p port number */
    char *doc_root;         /* root document directory */
    int log_fd;             /* file descriptor for log file */
} ServerConfig;

extern ServerConfig config;

/* HTTP Request Structure */
typedef struct {
    char method[16];        /* GET, HEAD */
    char uri[1024];         /* requested URI */
    char version[16];       /* HTTP/1.0, HTTP/1.1 */
    char if_modified_since[128];
    char remote_ip[INET6_ADDRSTRLEN];
    int is_cgi;
    char cgi_query[1024];
} HttpRequest;

/* Module 1: Networking & Server Lifecycle (Nguyen Hoang Luc) */
int init_server_socket(void);
void daemonize_server(void);
void handle_client(int client_fd, struct sockaddr_storage *client_addr);

/* Module 2: HTTP Parsing & Routing (Nguyen Xuan Lam) */
int parse_http_request(int client_fd, HttpRequest *req);
int resolve_path(const char *uri, char *resolved_path, size_t max_len, HttpRequest *req);

/* Module 3: Response Engine & Directory Indexing (Nguyen Dang Luan) */
void send_response_header(int client_fd, int status_code, const char *status_msg,
                          const char *content_type, off_t content_length, time_t last_modified);
void send_error_response(int client_fd, int status_code, const char *status_msg, const HttpRequest *req);
void serve_static_file(int client_fd, const char *path, const HttpRequest *req);
void serve_directory_index(int client_fd, const char *dir_path, const char *req_uri, const HttpRequest *req);

/* Module 4: CGI Engine & Logging (Vo Thi Quynh Linh) */
void execute_cgi(int client_fd, const char *cgi_path, const HttpRequest *req);
void log_access(const char *remote_ip, const char *first_line, int status_code, off_t bytes_sent);
const char *get_mime_type(const char *path);

#endif /* SWS_H */
