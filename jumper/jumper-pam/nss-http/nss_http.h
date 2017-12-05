#ifndef NSS_HTTP_H
#define NSS_HTTP_H

#define _GNU_SOURCE
#define _BSD_SOURCE

/* http, struct , jansson */
#include <grp.h>
#include <nss.h>
#include <pwd.h>
#include <errno.h>
#include <shadow.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <jansson.h>
#include <pthread.h>

/* syslog */
#include <syslog.h>

/* networks */
#include <sys/un.h>
#include <arpa/inet.h>
#include <sys/socket.h>

/* local cache file */
#define NSS_GROUP_CACHE "/var/lib/nss-cache/group"
#define NSS_PASSWD_CACHE "/var/lib/nss-cache/passwd"
#define NSS_GROUP_ALL_CACHE "/var/lib/nss-cache/group_all"

/* socket settings */
#define PORT 28888
#define HOST_IP "127.0.0.1"
#define SOCKET_FILE "/var/run/nss-cache.sock"
#define REQUEST "{\"type\": \"%s\", \"name\": \"%s\", \"value\": \"%s\", \"pid\": \"%d\", \"process_name\":\"%s\"}"

/* global funcitons */
extern char *__progname;
extern size_t j_strlen(json_t *);
extern json_t *nss_request(const char *type, const char *name, const char *value);

#endif /* NSS_HTTP_H */
