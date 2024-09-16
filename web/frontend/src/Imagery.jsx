import { useEffect, useState } from "react";
import { Card, CardBody, CardHeader } from "reactstrap";
import { getHost } from "./util";

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
        const url = getHost()
        url.pathname = '/data/imagery'

        const response = await fetch(url)
        const json = await response.json()
        if (json.error) {
            console.log(json.data)
            return
        }

        // FIXME: Sometimes data is null, IDK why
        if (!json.data)
            json.data = [null, null, null, null, null, null]

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