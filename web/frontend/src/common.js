export function getServerURL() {
    let url = new URL(window.location.href)
    url.port = 5000
    return url
}