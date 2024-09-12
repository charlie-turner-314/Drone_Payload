import { useEffect, useState } from "react";
import { Card, CardBody, CardHeader } from "reactstrap";
import { Line } from "react-chartjs-2";

import "chart.js/auto";

export default function Graph() {
    const [data, setData] = useState(undefined)

    const options = {
    }

    async function getData() {
        //
    }

    useEffect(() => {
        getData()
    }, [])

    return (
        <Card className="m-3">
            <CardHeader>Enviro Data</CardHeader>
            <CardBody>
                <p>TODO</p>
            </CardBody>
        </Card>
    )
}