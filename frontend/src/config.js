export async function loadConfig() {
    const res = await fetch("/config.json");
    const json = await res.json();
    return json.websocket;
}
