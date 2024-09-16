import { useEffect, useState } from "react";
import { Card, CardBody, CardHeader, CardImg } from "reactstrap";
import { getServerURL } from "./common";

export default function Feed() {
    const [src, setSrc] = useState(undefined)

    useEffect(() => {
        let url = getServerURL()
        url.pathname = '/video'
        setSrc(url.toString())
    }, [])

    return (
        <Card>
            <CardHeader>Live Feed</CardHeader>
            <CardBody>
                {src ? <CardImg src={src} alt="Live Feed" /> : null}
            </CardBody>
        </Card>
    )
}