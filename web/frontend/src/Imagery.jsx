import { useEffect, useState } from "react";
import { Card, CardBody, CardHeader } from "reactstrap";
import { getServerURL } from "./common";
import Speech from "speak-tts";

const speech = new Speech()
if (speech.hasBrowserSupport()) {
    console.log("TTS supported")
    speech.init().then((data) => {
        console.log("TTS ready: ", data)
        speech.speak({
            text: 'Hello',
            queue: false
        }).catch(e => {
            console.error("Error: ", e)
        })
    }).catch(e => {
        console.error("Failed to init TTS: ", e)
    })
}

export default function Imagery() {
    const [data, setData] = useState({
        valveState: null,
        arucoID: null,
        arucoPoseX: null,
        arucoPoseY: null,
        pressureGuage: null
    })
    const [rate, setRate] = useState(1000)

    async function getData() {
        const url = getServerURL()
        url.pathname = '/data/imagery'

        const response = await fetch(url)
        const json = await response.json()
        if (json.error) {
            console.error(json.data)
            return
        }

        // FIXME: Sometimes data is null, IDK why
        if (!json.data)
            json.data = [null, null, null, null, null, null]

        if (json.data[1] !== null) {
            speech.speak({
                text: `Valve state is ${json.data[1] ? "open" : "closed"}`,
                queue: true
            }).catch(e => {
                console.error("Error: ", e)
            })
        }

        setData({
            valveState: json.data[1],
            arucoID: json.data[2],
            arucoPoseX: json.data[3],
            arucoPoseY: json.data[4],
            pressureGuage: json.data[5]
        })
    }

    useEffect(() => {
        const interval = setInterval(() => {
            getData()
        }, rate)
        return () => clearInterval(interval)
    }, [])

    return (
        <Card>
            <CardHeader>Imagery Stats</CardHeader>
            <CardBody>
                <p><b>Valve State</b>: {data.valveState === null ? "" : data.valveState ? "Open" : "Closed"}</p>
                <p><b>ArUCO ID</b>: {data.arucoID}</p>
                <p><b>ArUCO Position</b>: {data.arucoID === null ? "" : `(${data.arucoPoseX}, ${data.arucoPoseY})`}</p>
                <p><b>Pressure Guage</b>: {data.pressureGuage}</p>
            </CardBody>
        </Card>
    )
}