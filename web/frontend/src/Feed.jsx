import { useEffect, useState } from "react";
import { Card, CardBody, CardHeader, CardImg } from "reactstrap";
import { getHost } from "./util";

export default function Feed() {
    const [src, setSrc] = useState(undefined)

    useEffect(() => {
        let url = getHost()
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