import { useEffect, useState } from "react";
import { Card, CardBody, CardHeader } from "reactstrap";
import { getHost } from "./util";

export default function Imagery() {
    const [data, setData] = useState(undefined)
    const [rate, setRate] = useState(1000)

    async function getData() {
        const url = getHost()
        url.pathname = '/data/imagery'

        console.log(url)
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
                <p>TODO</p>
            </CardBody>
        </Card>
    )
}