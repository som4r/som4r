function setCookie(name, value) {
    var curCookie = name + "=" + escape(value);
    document.cookie = curCookie;
}

/*
      name - name of the desired cookie
      return string containing value of specified cookie or null
      if cookie does not exist
    */
function getCookie(name) {
    var dc = document.cookie;
    var prefix = name + "=";
    var begin = dc.indexOf("; " + prefix);
    if (begin == -1) {
        begin = dc.indexOf(prefix);
        if (begin != 0) return null;
    } else
        begin += 2;
    var end = document.cookie.indexOf(";", begin);
    if (end == -1)
        end = dc.length;
    return unescape(dc.substring(begin + prefix.length, end));
}

