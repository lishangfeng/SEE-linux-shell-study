#include "nss_http.h"

/*
 Newer versions of Jansson have this but the version
 on Ubuntu 12.04 don't, so make a wrapper.
*/
extern size_t j_strlen(json_t *str)
{
    return strlen(json_string_value(str));
}

/* don't close socket */
static int nss_socket_fd = -1;

/* timeout for socket recv */
struct timeval tv = {1,10000};  // 设置10ms读超时

/* user_name flag */
//static char user_name[24] = "";

int nss_connect(void){
    // single process send onetime error message
    static int socket_failed_flag;
    nss_socket_fd = -1;
    struct sockaddr_un server;
    if ((nss_socket_fd = socket(AF_UNIX, SOCK_STREAM, 0)) < 0){
        syslog(LOG_INFO, "ERROR[%d]: ERROR opening socket", getpid());
        return -1;
    }
    // pack socket unix struct
    memset(&server, 0, sizeof(server));
    server.sun_family = AF_UNIX;
    strcpy(server.sun_path, SOCKET_FILE);

    // connect to server
    if (connect(nss_socket_fd, (struct sockaddr *) &server, sizeof(server)) < 0){
        nss_socket_fd = -1;
        if (socket_failed_flag == 0){
            syslog(LOG_INFO, "ERROR[%d]: connect to socket file failed", getpid());
        }
        socket_failed_flag = 1;
        return -1;
    }
    /* 分别设置读写超时 */
    setsockopt(nss_socket_fd, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof(struct timeval));
    setsockopt(nss_socket_fd, SOL_SOCKET, SO_SNDTIMEO, (const char*)&tv, sizeof(struct timeval));
    return 1;
}

/* fix crond fork process bug */
int check_mypid(void){
    static pid_t mypid;
    if(strcmp(__progname, "crond") == 0 || strcmp(__progname, "CROND") == 0){
        if (getpid() != mypid) {
                close(nss_socket_fd);
                nss_socket_fd = -1;
                nss_connect();
                mypid = getpid();
            }
            return 1;
    }
    return 0;
}

/*
阻塞与非阻塞recv返回值没有区分，都是
<0 出错
=0 连接关闭
>0 接收到数据大小，
*/
int receive(char *buf, int length)
{
    char *new_buf = buf;
    int left = length;
    int total = 0;
    int count = 0;
    while(1)
    {
        if (count >= 16){
            return -1;
        }
        if (recv(nss_socket_fd, new_buf, left, 0) <= 0){
            return -1;
        }else{
            count += 1;
            int data_length = strlen(new_buf);
            total += data_length;
            if (data_length == left){
                return length;  // 数据获取正确返回正确的数据长度
            }else{
                left =  length - total;
                new_buf += data_length;   // 移动指针，相当于拼接字符串
            }
        }
    }
}

/* load json string from file */
json_t * nss_read_file(const char * filename)
{
    long file_size;
    char *contents;
    FILE *file = fopen(filename, "r");
    if (file == NULL) return NULL;
    fseek(file, 0, SEEK_END);
    file_size = ftell(file);
    rewind(file);
    contents = malloc(file_size * (sizeof(char))+1);
    if (!contents){
        fclose(file);
        return NULL;
    }
    memset(contents, 0, file_size * (sizeof(char))+1);
    fread(contents, sizeof(char), file_size, file);
    fclose(file);

    json_t *root = NULL;
    json_error_t error;
    size_t flag = 0;

    /* load json string from encrypt file */
    root = json_loads(contents, flag, &error);
    free(contents);

    if (!root){
        json_decref(root);
        return NULL;
    }
    return root;
}

/* request from cache file */
json_t * nss_cache_request(const char *type, const char *name, const char *value)
{
    /* passwd cache handler*/
    if (strcmp(type, "password") == 0)
    {
//        strcpy(user_name, value);
        /* read cache file, parse it to json array */
        json_t * root = nss_read_file(NSS_PASSWD_CACHE);
        if (!root) {
            syslog(LOG_INFO, "ERROR[%d]: nss-cache daemon dead, read local passwd cache file failed.", getpid());
            return NULL;
        }
        json_t *json_return = json_deep_copy(json_object_get(root, value));
        json_decref(root);
        return json_return;
    }

    /* group cache handler */
    else if (strcmp(type, "group") == 0)
    {
        json_t * root = nss_read_file(NSS_GROUP_CACHE);
        if (!root) {
            syslog(LOG_INFO, "ERROR[%d]: nss-cache daemon dead, read local group cache file failed.", getpid());
            return NULL;
        }
        /* loads all groups */
        if (strcmp(name , "") == 0)
        {
            if (strcmp(__progname, "getent") == 0) return NULL;
            json_t * array = nss_read_file(NSS_GROUP_ALL_CACHE);
            if (!array) return NULL;
            return array;
        }
        else{
//            json_t *json_return = json_deep_copy(json_object_get(root, user_name));
            json_t *json_return = json_deep_copy(json_object_get(root, value));
            json_decref(root);
            return json_return;
        }
    }

    return NULL;
}

/* request local unix file */
json_t * nss_request(const char *type, const char *name, const char *value)
{
    check_mypid();

    // bind sock with unix file
    if (nss_socket_fd <= 0){
        if (nss_connect() < 0){
            json_t * json_return = nss_cache_request(type, name, value);
            if (!json_return) return NULL;
            return json_return;
        }
    }

    // concat request json
    char request_json[256] = "";
    snprintf(request_json, 256, REQUEST, type, name, value, getpid(), __progname);

    // send json object
    if (send(nss_socket_fd, request_json, strlen(request_json), MSG_NOSIGNAL) < 0){
        if (nss_connect() < 0){
            return NULL;
        }
        if (send(nss_socket_fd, request_json, strlen(request_json), MSG_NOSIGNAL) < 0) {
            syslog(LOG_INFO, "ERROR[%d]: send request_json failed again.", getpid());
            return NULL;
        }
    }

    // get header length
    char header[17] = "";
    if (receive(header, 16) < 0){
        syslog(LOG_INFO, "ERROR[%d]: scoket recv body header failed", getpid());
        return NULL;
    }

    // get body of json
    int length = atoi(header);
    char body[length + 2];
    memset(body, 0, length + 2);
    if (receive(body, length) < 0){
        syslog(LOG_INFO, "ERROR[%d]: scoket recv body failed", getpid());
        return NULL;
    }

    /* json pack */
    json_error_t json_error;
    json_t * json_root = NULL;

    json_root = json_loads(body, 0, &json_error);
    if (!json_root) {
        syslog(LOG_INFO, "ERROR[%d]: json_loads fialed, body: %s", getpid(), body);
        return NULL;
    }
    return json_root;
}
