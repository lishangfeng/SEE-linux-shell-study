package lib

import (
    "time"
    "io"
    "io/ioutil"
    "compress/gzip"
    "net/http"
    "github.com/thevipwan/go-logger/logger"
)

func Http(method, url, ua string, timeout int) (body []byte, err error) {
    client := &http.Client{Timeout: time.Duration(timeout) * time.Second}

    logger.Debug(method, url)
    // make request body
    request, err := http.NewRequest(method, url, nil)
    if err != nil {
        logger.Error("Http make request body: ", err.Error())
        return
    }

    // set headers
    request.Header.Add("User-Agent", ua)
    request.Header.Add("Accept-Encoding", "gzip")
    request.Header.Add("Content-Type", "application/json")
    response, err := client.Do(request)

    if err != nil {
        logger.Error("Http request: ", err.Error())
        return
    } else {
        // close request
        defer response.Body.Close()
    }

    // response code
    if response.StatusCode != 200 {
        logger.Error("Http 请求服务端失败:", response.StatusCode, url)
        return
    }

    // gzip response
    var reader io.ReadCloser
    switch response.Header.Get("Content-Encoding") {
    case "gzip":
        reader, _ = gzip.NewReader(response.Body)
        defer reader.Close()
    default:
        reader = response.Body
    }
    body, err = ioutil.ReadAll(reader)
    return
}
