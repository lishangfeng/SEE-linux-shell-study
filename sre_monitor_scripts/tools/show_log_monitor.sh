source ../lib

function contains() {
    local n=$#
    local value=${!n}
    for ((i=1;i < $#;i++)) {
        if [ "${!i}" == "${value}" ]; then
            echo "y"
            return 0
        fi
    }
    echo "n"
    return 1
}


projects=`find ../ -type d -d 1| grep -E -v '(git)|(tool)|(deploy)|(cron)' | awk -F '/' '{print $3}'`

printf "|%-15s|%-15s|%-15s|%-31s|\n" project log.error url.check time
for project in $projects; do
    # log
    log_err_mon=`ls "../$project" | grep log.error.sh`
    log_error_ignore=("dns" "guard" )
    if [ -z $log_err_mon ]; then
        if [ `contains "${log_error_ignore[@]}" "$project"` == "y" ]; then
            log_err_mon="won't do"
        else
            log_err_mon=TODO
        fi
    else
        log_err_mon="DONE"
    fi

    # log other
    time=`ls "../$project" | grep time`

    # url.check
    url_check=`ls "../$project" | grep url.check`
    if [ -z $url_check ]; then
        url_check="TODO"
    else
        url_check="DONE"
    fi
    printf "|%-15s|%-15s|%-15s|%-31s|\n" "$project" "$log_err_mon" "$url_check" "$time"
done
