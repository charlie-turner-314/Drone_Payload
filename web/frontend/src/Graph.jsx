import { useEffect, useState } from "react";
import { Card, CardBody, CardHeader } from "reactstrap";
import { Line } from "react-chartjs-2";

import "chart.js/auto";

export default function Graph() {
    const [data, setData] = useState(undefined)

    const INTERVAL = 1000
    const MAX_ENTRIES = 30

    const options = {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }

    let start = 0
    let results = []

    async function getData() {
        const url = new URL('http://localhost:5000/data')
        url.searchParams.append('start', start)

        const response = await fetch(url)
        const json = await response.json()
        if (json.error) {
            console.log(json.data)
            return
        }

        results = results.concat(json.data)
        results = results.slice(-MAX_ENTRIES)

        const id = results.map(d => d[0])
        const temperature = results.map(d => d[1])
        const pressure = results.map(d => d[2])
        const humidity = results.map(d => d[3])
        const light = results.map(d => d[4])
        const oxidised = results.map(d => d[5])
        const reduced = results.map(d => d[6])
        const ammonia = results.map(d => d[7])

        start = id[id.length - 1]

        setData({
            labels: id,
            datasets: [
                {
                    label: "Temperature",
                    data: temperature,
                    borderColor: "rgba(255, 99, 132, 1)",
                    backgroundColor: "rgba(255, 99, 132, 0.2)"
                },
                {
                    label: "Pressure",
                    data: pressure,
                    borderColor: "rgba(54, 162, 235, 1)",
                    backgroundColor: "rgba(54, 162, 235, 0.2)"
                },
                {
                    label: "Humidity",
                    data: humidity,
                    borderColor: "rgba(255, 206, 86, 1)",
                    backgroundColor: "rgba(255, 206, 86, 0.2)"
                },
                {
                    label: "Light",
                    data: light,
                    borderColor: "rgba(75, 192, 192, 1)",
                    backgroundColor: "rgba(75, 192, 192, 0.2)"
                },
                {
                    label: "Oxidised",
                    data: oxidised,
                    borderColor: "rgba(153, 102, 255, 1)",
                    backgroundColor: "rgba(153, 102, 255, 0.2)"
                },
                {
                    label: "Reduced",
                    data: reduced,
                    borderColor: "rgba(255, 159, 64, 1)",
                    backgroundColor: "rgba(255, 159, 64, 0.2)"
                },
                {
                    label: "Ammonia",
                    data: ammonia,
                    borderColor: "rgba(255, 99, 132, 1)",
                    backgroundColor: "rgba(255, 99, 132, 0.2)"
                }
            ]
        })
    }

    useEffect(() => {
        const interval = setInterval(() => {
            getData()
        }, INTERVAL)
        return () => clearInterval(interval)
    }, [])

    return (
        <Card className="m-3">
            <CardHeader>Enviro Data</CardHeader>
            <CardBody>
                {data ? <Line data={data} options={options} /> : null}
            </CardBody>
        </Card>
    )
}