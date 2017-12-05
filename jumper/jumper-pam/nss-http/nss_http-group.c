#include "nss_http.h"

static pthread_mutex_t NSS_HTTP_MUTEX = PTHREAD_MUTEX_INITIALIZER;
#define NSS_HTTP_LOCK()    do { pthread_mutex_lock(&NSS_HTTP_MUTEX); } while (0)
#define NSS_HTTP_UNLOCK()  do { pthread_mutex_unlock(&NSS_HTTP_MUTEX); } while (0)

static json_t *ent_json_root = NULL;
static int ent_json_idx = 0;


/*
-1 Failed to parse
-2 Buffer too small
*/
static int pack_group_struct(json_t *root, struct group *result, char *buffer, size_t buflen)
{
    char *next_buf = buffer;
    size_t bufleft = buflen;

    if (!json_is_object(root)) return -1;

    json_t *j_member;
    json_t *j_gr_name = json_object_get(root, "gr_name");
    json_t *j_gr_gid = json_object_get(root, "gr_gid");
    json_t *j_gr_mem = json_object_get(root, "gr_mem");

    if (!json_is_string(j_gr_name)) return -1;
    if (!json_is_integer(j_gr_gid)) return -1;
    if (!json_is_array(j_gr_mem)) return -1;

    memset(buffer, 0, buflen);

    /* gr_name */
    if (bufleft <= j_strlen(j_gr_name)) return -2;
    result->gr_name = strncpy(next_buf, json_string_value(j_gr_name), bufleft);
    next_buf += strlen(result->gr_name) + 1;
    bufleft  -= strlen(result->gr_name) + 1;

    /* gr_passwd */
    result->gr_passwd = "x";
    /* gid */
    result->gr_gid = json_integer_value(j_gr_gid);

    /* if bufleft not able to hold all gr_mem data, return -2 force system give double buffer
        , don't forget that Solaris system won't give bigger buffer
     */
    size_t mem_size = json_array_size(j_gr_mem);
    if (bufleft <= (mem_size + 1) * sizeof(char *)) return -2;
    result->gr_mem = (char **)next_buf;
    next_buf += (mem_size + 1) * sizeof(char *);
    bufleft  -= (mem_size + 1) * sizeof(char *);

    /* pack group members */
    for(int i = 0; i < mem_size; i++)
    {
        j_member = json_array_get(j_gr_mem, i);
        if (!json_is_string(j_member)) return -1;

        if (bufleft <= j_strlen(j_member)) return -2;
        strncpy(next_buf, json_string_value(j_member), bufleft);
        result->gr_mem[i] = next_buf;

        next_buf += strlen(result->gr_mem[i]) + 1;
        bufleft  -= strlen(result->gr_mem[i]) + 1;
    }

    return 0;
}


enum nss_status _nss_http_setgrent_locked(int stayopen)
{
    json_t *json_root = NULL;

    /* fetch data from own data source */
    json_root = nss_request("group", "", "");

    /* NULL */
    if (!json_root) {
        return NSS_STATUS_UNAVAIL;
    }

    /* return list to global static var */
    ent_json_root = json_root;
    ent_json_idx = 0;

    return NSS_STATUS_SUCCESS;
}


/* Called to open the group file */
enum nss_status _nss_http_setgrent(int stayopen)
{
    enum nss_status ret;
    NSS_HTTP_LOCK();
    ret = _nss_http_setgrent_locked(stayopen);
    NSS_HTTP_UNLOCK();
    return ret;
}


enum nss_status _nss_http_endgrent_locked(void)
{
    if (ent_json_root) {
        while (ent_json_root->refcount > 0) json_decref(ent_json_root);
    }

    ent_json_root = NULL;
    ent_json_idx = 0;

    return NSS_STATUS_SUCCESS;
}


/* Called to close the group file */
enum nss_status _nss_http_endgrent(void)
{
    enum nss_status ret;
    NSS_HTTP_LOCK();
    ret = _nss_http_endgrent_locked();
    NSS_HTTP_UNLOCK();
    return ret;
}


enum nss_status _nss_http_getgrent_r_locked(struct group *result, char *buffer, size_t buflen, int *errnop)
{
    enum nss_status ret = NSS_STATUS_SUCCESS;

    if (ent_json_root == NULL) {
        ret = _nss_http_setgrent_locked(0);
    }

    if (ret != NSS_STATUS_SUCCESS) return ret;

    int pack_result = pack_group_struct(
        json_array_get(ent_json_root, ent_json_idx), result, buffer, buflen
    );

    if (pack_result == -1) {
        *errnop = ENOENT;
        return NSS_STATUS_UNAVAIL;
    }

    if (pack_result == -2) {
        *errnop = ERANGE;
        return NSS_STATUS_TRYAGAIN;
    }

    /* Return not found when there's nothing else to read. */
    if (ent_json_idx >= json_array_size(ent_json_root)) {
        *errnop = ENOENT;
        return NSS_STATUS_NOTFOUND;
    }

    /* cursor to next entry */
    ent_json_idx++;

    return NSS_STATUS_SUCCESS;
}


/* Called to look up next entry in group file */
enum nss_status _nss_http_getgrent_r(struct group *result, char *buffer, size_t buflen, int *errnop)
{
    enum nss_status ret;
    NSS_HTTP_LOCK();
    ret = _nss_http_getgrent_r_locked(result, buffer, buflen, errnop);
    NSS_HTTP_UNLOCK();
    return ret;
}


/* Find a group by gid */
enum nss_status _nss_http_getgrgid_r_locked(gid_t gid, struct group *result, char *buffer, size_t buflen, int *errnop)
{
    json_t * json_root = NULL;
    char str_gid[24];
    sprintf(str_gid, "%d", gid);

    json_root = nss_request("group", "gid", str_gid);

    if (!json_root) {
        *errnop = ENOENT;
        return NSS_STATUS_UNAVAIL;
    }

    int pack_result = pack_group_struct(json_root, result, buffer, buflen);

    if (pack_result == -1) {
        json_decref(json_root);
        *errnop = ENOENT;
        return NSS_STATUS_UNAVAIL;
    }

    if (pack_result == -2) {
        json_decref(json_root);
        *errnop = ERANGE;
        return NSS_STATUS_TRYAGAIN;
    }

    json_decref(json_root);

    return NSS_STATUS_SUCCESS;
}


enum nss_status _nss_http_getgrgid_r(gid_t gid, struct group *result, char *buffer, size_t buflen, int *errnop)
{
    enum nss_status ret;
    NSS_HTTP_LOCK();
    ret = _nss_http_getgrgid_r_locked(gid, result, buffer, buflen, errnop);
    NSS_HTTP_UNLOCK();
    return ret;
}


enum nss_status _nss_http_getgrnam_r_locked(const char *name, struct group *result, char *buffer, size_t buflen, int *errnop)
{
    json_t *json_root;
    json_root = nss_request("group", "name", name);

    if (!json_root) {
        *errnop = ENOENT;
        return NSS_STATUS_UNAVAIL;
    }

    int pack_result = pack_group_struct(json_root, result, buffer, buflen);

    if (pack_result == -1) {
        json_decref(json_root);
        *errnop = ENOENT;
        return NSS_STATUS_UNAVAIL;
    }

    if (pack_result == -2) {
        json_decref(json_root);
        *errnop = ERANGE;
        return NSS_STATUS_TRYAGAIN;
    }

    json_decref(json_root);

    return NSS_STATUS_SUCCESS;
}


/* Find a group by name */
enum nss_status _nss_http_getgrnam_r(const char *name, struct group *result, char *buffer, size_t buflen, int *errnop)
{
    enum nss_status ret;
    NSS_HTTP_LOCK();
    ret = _nss_http_getgrnam_r_locked(name, result, buffer, buflen, errnop);
    NSS_HTTP_UNLOCK();
    return ret;
}
