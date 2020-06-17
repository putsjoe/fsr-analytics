var tracker_url = 'http://localhost:5000/noscript.gif'
function tracker(event) {
    var t = 'tracker-jhsb8e'
    var extra = '?referrer=' + document.referrer
    if (event) {
        extra += '&event=' + event 
    }
    if (window.localStorage.getItem(t)) {
        extra += '&id=' + window.localStorage.getItem(t)
    } else {
        window.localStorage.setItem(t,
            Date.now().toString().substring(5,-1) +
            Math.random().toString(30).substring(2,15))
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
