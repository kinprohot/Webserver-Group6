/*
 * sws.c - Main Entry & Server Lifecycle Module
 * Author: Nguyen Hoang Luc (23IT151) - Team Leader
 *
 * Responsibilities:
 * - Option parsing (-c, -d, -h, -i, -l, -p, dir)
 * - Daemonization (fork, setsid, chdir, redirect stdio)
 * - Socket creation, IPv4/IPv6 dual-stack binding, and accept loop
 * - Concurrency management using fork() and SIGCHLD signal handling
 */

#include "sws.h"

ServerConfig config;

static void usage(const char *progname) {
    fprintf(stderr, "Usage: %s [-dh] [-c dir] [-i address] [-l file] [-p port] dir\n", progname);
    fprintf(stderr, "Options:\n");
    fprintf(stderr, "  -c dir      Allow execution of CGIs from the given directory\n");
    fprintf(stderr, "  -d          Enter debugging mode (no daemonize, single connection, stdout logging)\n");
    fprintf(stderr, "  -h          Print this short usage summary and exit\n");
    fprintf(stderr, "  -i address  Bind to the given IPv4 or IPv6 address (default: any)\n");
    fprintf(stderr, "  -l file     Log all requests to the given file\n");
    fprintf(stderr, "  -p port     Listen on the given port (default: 8080)\n");
    fprintf(stderr, "  dir         Document root directory to serve content from\n");
    exit(EXIT_FAILURE);
}

static void sigchld_handler(int sig) {
    (void)sig;
    int saved_errno = errno;
    while (waitpid(-1, NULL, WNOHANG) > 0);
    errno = saved_errno;
}

void daemonize_server(void) {
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        exit(EXIT_FAILURE);
    }
    if (pid > 0) {
        /* Parent exits */
        exit(EXIT_SUCCESS);
    }

    if (setsid() < 0) {
        perror("setsid");
        exit(EXIT_FAILURE);
    }

    /* Catch or ignore signals */
    signal(SIGCHLD, sigchld_handler);
    signal(SIGPIPE, SIG_IGN);

    /* Fork again to ensure daemon cannot acquire a controlling terminal */
    pid = fork();
    if (pid < 0) {
        perror("fork second");
        exit(EXIT_FAILURE);
    }
    if (pid > 0) {
        exit(EXIT_SUCCESS);
    }

    /* Change working directory to root or docroot */
    umask(027);

    /* Close standard file descriptors unless in debug mode */
    if (!config.debug) {
        int devnull = open("/dev/null", O_RDWR);
        if (devnull >= 0) {
            dup2(devnull, STDIN_FILENO);
            dup2(devnull, STDOUT_FILENO);
            dup2(devnull, STDERR_FILENO);
            if (devnull > 2) close(devnull);
        }
    }
}

int init_server_socket(void) {
    int server_fd = -1;
    struct addrinfo hints, *res, *rp;
    char port_str[16];

    snprintf(port_str, sizeof(port_str), "%d", config.port);

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;     /* IPv4 or IPv6 */
    hints.ai_socktype = SOCK_STREAM; /* TCP stream */
    hints.ai_flags = AI_PASSIVE;     /* Wildcard IP if bind_address is NULL */

    int s = getaddrinfo(config.bind_address, port_str, &hints, &res);
    if (s != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(s));
        exit(EXIT_FAILURE);
    }

    for (rp = res; rp != NULL; rp = rp->ai_next) {
        server_fd = socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);
        if (server_fd == -1) continue;

        int opt = 1;
        setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        /* If IPv6, disable IPV6_V6ONLY to accept dual-stack IPv4 connections */
        if (rp->ai_family == AF_INET6) {
            int no = 0;
            setsockopt(server_fd, IPPROTO_IPV6, IPV6_V6ONLY, &no, sizeof(no));
        }

        if (bind(server_fd, rp->ai_addr, rp->ai_addrlen) == 0) {
            break; /* Successfully bound */
        }

        close(server_fd);
        server_fd = -1;
    }

    freeaddrinfo(res);

    if (server_fd == -1) {
        perror("Could not bind server socket");
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 64) < 0) {
        perror("listen");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    return server_fd;
}

void handle_client(int client_fd, struct sockaddr_storage *client_addr) {
    HttpRequest req;
    memset(&req, 0, sizeof(req));

    /* Extract remote client IP */
    if (client_addr->ss_family == AF_INET) {
        struct sockaddr_in *s = (struct sockaddr_in *)client_addr;
        inet_ntop(AF_INET, &s->sin_addr, req.remote_ip, sizeof(req.remote_ip));
    } else {
        struct sockaddr_in6 *s = (struct sockaddr_in6 *)client_addr;
        inet_ntop(AF_INET6, &s->sin6_addr, req.remote_ip, sizeof(req.remote_ip));
    }

    if (parse_http_request(client_fd, &req) < 0) {
        close(client_fd);
        return;
    }

    /* Check if CGI */
    if (req.is_cgi) {
        if (!config.cgi_dir) {
            send_error_response(client_fd, 403, "Forbidden", &req);
        } else {
            char cgi_full_path[PATH_MAX_LEN];
            snprintf(cgi_full_path, sizeof(cgi_full_path), "%s/%s", config.cgi_dir, req.uri + 9);
            execute_cgi(client_fd, cgi_full_path, &req);
        }
        close(client_fd);
        return;
    }

    /* Resolve relative path */
    char resolved_path[PATH_MAX_LEN];
    if (resolve_path(req.uri, resolved_path, sizeof(resolved_path), &req) < 0) {
        send_error_response(client_fd, 404, "Not Found", &req);
        close(client_fd);
        return;
    }

    struct stat st;
    if (stat(resolved_path, &st) < 0) {
        if (errno == EACCES)
            send_error_response(client_fd, 403, "Forbidden", &req);
        else
            send_error_response(client_fd, 404, "Not Found", &req);
        close(client_fd);
        return;
    }

    if (S_ISDIR(st.st_mode)) {
        /* Check if index.html exists */
        char index_path[PATH_MAX_LEN];
        snprintf(index_path, sizeof(index_path), "%s/index.html", resolved_path);
        struct stat st_idx;
        if (stat(index_path, &st_idx) == 0 && S_ISREG(st_idx.st_mode)) {
            serve_static_file(client_fd, index_path, &req);
        } else {
            serve_directory_index(client_fd, resolved_path, req.uri, &req);
        }
    } else if (S_ISREG(st.st_mode)) {
        serve_static_file(client_fd, resolved_path, &req);
    } else {
        send_error_response(client_fd, 403, "Forbidden", &req);
    }

    close(client_fd);
}

int main(int argc, char **argv) {
    int opt;
    memset(&config, 0, sizeof(config));
    config.port = DEFAULT_PORT;
    config.log_fd = -1;

    while ((opt = getopt(argc, argv, "c:dhi:l:p:")) != -1) {
        switch (opt) {
            case 'c':
                config.cgi_dir = optarg;
                break;
            case 'd':
                config.debug = 1;
                break;
            case 'h':
                usage(argv[0]);
                break;
            case 'i':
                config.bind_address = optarg;
                break;
            case 'l':
                config.log_file = optarg;
                break;
            case 'p':
                config.port = atoi(optarg);
                if (config.port <= 0 || config.port > 65535) {
                    fprintf(stderr, "Invalid port number: %s\n", optarg);
                    exit(EXIT_FAILURE);
                }
                break;
            default:
                usage(argv[0]);
        }
    }

    if (optind >= argc) {
        fprintf(stderr, "Missing document root directory\n");
        usage(argv[0]);
    }

    config.doc_root = argv[optind];

    /* Verify document root exists and is directory */
    struct stat st;
    if (stat(config.doc_root, &st) < 0 || !S_ISDIR(st.st_mode)) {
        fprintf(stderr, "Document root '%s' is not a valid directory\n", config.doc_root);
        exit(EXIT_FAILURE);
    }

    /* Open log file if specified */
    if (config.log_file) {
        config.log_fd = open(config.log_file, O_WRONLY | O_CREAT | O_APPEND, 0644);
        if (config.log_fd < 0) {
            perror("Error opening log file");
            exit(EXIT_FAILURE);
        }
    }

    int server_fd = init_server_socket();

    if (config.debug) {
        printf("[DEBUG MODE - sws running]\n");
        printf("Document Root: %s\n", config.doc_root);
        printf("Listening on port: %d (bind: %s)\n", config.port, config.bind_address ? config.bind_address : "all");
        if (config.cgi_dir) printf("CGI Directory: %s\n", config.cgi_dir);
    } else {
        daemonize_server();
    }

    signal(SIGCHLD, sigchld_handler);

    /* Main Accept Loop */
    for (;;) {
        struct sockaddr_storage client_addr;
        socklen_t addr_len = sizeof(client_addr);

        int client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &addr_len);
        if (client_fd < 0) {
            if (errno == EINTR) continue;
            perror("accept");
            continue;
        }

        if (config.debug) {
            /* Debug mode handles sequentially */
            handle_client(client_fd, &client_addr);
        } else {
            /* Daemon mode handles concurrently using fork() */
            pid_t pid = fork();
            if (pid < 0) {
                perror("fork client");
                close(client_fd);
            } else if (pid == 0) {
                /* Child process */
                close(server_fd);
                handle_client(client_fd, &client_addr);
                exit(EXIT_SUCCESS);
            } else {
                /* Parent process */
                close(client_fd);
            }
        }
    }

    close(server_fd);
    if (config.log_fd >= 0) close(config.log_fd);
    return EXIT_SUCCESS;
}
