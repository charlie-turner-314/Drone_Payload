export function getServerURL() {
    // let url = new URL(window.location.href)
    let url = new URL('http://127.0.0.1')
    url.port = 5000
    return url
}