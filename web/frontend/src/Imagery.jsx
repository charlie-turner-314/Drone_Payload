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

const PRESSURE_THRESHOLD = 10
const RESET_TIMEOUT = 5000

export default function Imagery() {
    const [data, setData] = useState({
        valveState: null,
        arucoID: null,
        arucoPoseX: null,
        arucoPoseY: null,
        pressureGuage: null
    })
    const [lastValveState, setLastValveState] = useState(null)
    const [lastArucoID, setLastArucoID] = useState(null)
    const [lastPressureValue, setLastPressureValue] = useState(null)

    const rate = useSelector(state => state.rate)
    const mute = useSelector(state => state.mute)

    function speak(text) {
        if (mute) {
            return
        }
        speech.speak({
            text: text,
            queue: false
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
            json.data = [null, null, null, null, null, null]

        if (json.data[1] !== null) {
            if (lastValveState !== json.data[1]) {
                setLastValveState(json.data[1])
                setTimeout(() => setLastValveState(null), RESET_TIMEOUT)
                speak(`Valve detected in ${json.data[1] ? "open" : "closed"} state`)
            }
        }
        if (json.data[2] !== null) {
            if (lastArucoID !== json.data[2]) {
                setLastArucoID(json.data[2])
                setTimeout(() => setLastArucoID(null), RESET_TIMEOUT)
                speak(`Aruco marker with I D ${json.data[2]} detected at position ${Math.round(json.data[3])}, ${Math.round(json.data[4])}`)
            }
        }
        if (json.data[5] !== null) {
            let nearest = Math.round(json.data[5] / PRESSURE_THRESHOLD) * PRESSURE_THRESHOLD
            if (lastPressureValue !== nearest) {
                setLastPressureValue(nearest)
                setTimeout(() => setLastPressureValue(null), RESET_TIMEOUT)
                speak(`Pressure guage detected at ${Math.round(json.data[5])} pascals`)
            }
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
    }, [mute, rate])

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
                <p><b>ArUCO Position</b>: {data.arucoID === null ? "" : `(${data.arucoPoseX}, ${data.arucoPoseY})`}</p>
                <p><b>Pressure Guage</b>: {data.pressureGuage}</p>
            </CardBody>
        </Card>
    )
}