var tracker_url = 'http://localhost:5000/noscript.gif'
function tracker(event) {
    var t = 'tracker'
    var extra = '?referrer=' + document.referrer
    if (event) {
        extra += '&event=' + event 
    }
    if (window.localStorage.getItem(t)) {
        extra += '&last=' + window.localStorage.getItem(t)
        window.localStorage.setItem(t, Date.now())
    } else {
        window.localStorage.setItem(t, Date.now())
        extra += '&unique=true'
    }
    var src = tracker_url + extra,
        img = document.createElement('img')
    img.src = src;
    document.body.appendChild(img).remove()
}
window.onload = function() {
    tracker()
}
