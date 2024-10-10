import { useEffect, useState } from "react";
import { Card, CardBody, CardHeader } from "reactstrap";
import { getServerURL } from "./common";
import { useSelector } from "react-redux";
import Speech from "speak-tts";

const speech = new Speech()
if (speech.hasBrowserSupport()) {
    speech.init().then(data => {
        console.log("Speech is ready", data)
    }
    ).catch(e => {
        console.error("Failed to initialize speech", e)
    })
} else {
    console.error("Speech is not supported")
}

export default function Imagery() {
    const [data, setData] = useState({
        valveState: null,
        arucoID: null,
        arucoPoseX: null,
        arucoPoseY: null,
        arucoPoseZ: null,
        pressureGuage: null
    })

    const [rate, setRate] = useState(1000)
    const mute = useSelector(state => state.mute)

    function speak(text) {
        if (mute) {
            return
        }
        speech.speak({
            text: text,
            queue: true
        }).catch(e => {
            console.error("Failed to speak: ", e)
        })
    }

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
            json.data = [null, null, null, null, null, null, null]

        if (json.data[1] !== null) {
            speak(`Valve detected in ${json.data[1] ? "open" : "closed"} state`)
        }
        if (json.data[2] !== null) {
            speak(`Aruco marker with I D ${json.data[2]} detected at position ${Math.round(json.data[3])}, ${Math.round(json.data[4])}`)
        }
        if (json.data[5] !== null) {
            speak(`Pressure guage detected at ${Math.round(json.data[5])} pascals`)
        }

        setData({
            valveState: json.data[1],
            arucoID: json.data[2],
            arucoPoseX: json.data[3],
            arucoPoseY: json.data[4],
            arucoPoseZ: json.data[5],
            pressureGuage: json.data[6]
        })
    }

    useEffect(() => {
        const interval = setInterval(() => {
            getData()
        }, rate)
        return () => clearInterval(interval)
    }, [mute])

    useEffect(() => {
        if (mute) {
            speech.cancel()
        } else {
            speak("Audio enabled")
        }
    }, [mute])

    return (
        <Card>
            <CardHeader>Imagery Stats</CardHeader>
            <CardBody>
                <p><b>Valve State</b>: {data.valveState === null ? "" : data.valveState ? "Open" : "Closed"}</p>
                <p><b>ArUCO ID</b>: {data.arucoID}</p>
                <p><b>ArUCO Position</b>: {data.arucoID === null ? "" : `(${data.arucoPoseX}, ${data.arucoPoseY}, ${data.arucoPoseZ})`}</p>
                <p><b>Pressure Guage</b>: {data.pressureGuage}</p>
            </CardBody>
        </Card>
    )
}