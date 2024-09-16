export function getHost() {
    let url = new URL(window.location.href)
    url.port = 5000
    return url
}