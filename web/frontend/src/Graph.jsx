import { useEffect, useState } from "react";
import { Card, CardBody, CardHeader } from "reactstrap";
import { Line } from "react-chartjs-2";

import "chart.js/auto";

export default function Graph() {
    const [data, setData] = useState(undefined)

    const options = {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }

    async function getData() {
        const response = await fetch('http://localhost:5000/data')
        const json = await response.json()
        if (json.error) {
            console.log(json.data)
            return
        }

        const id = json.data.map(d => d[0])
        const temperature = json.data.map(d => d[1])
        const pressure = json.data.map(d => d[2])
        const humidity = json.data.map(d => d[3])
        const light = json.data.map(d => d[4])
        const oxidised = json.data.map(d => d[5])
        const reduced = json.data.map(d => d[6])
        const ammonia = json.data.map(d => d[7])

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
        getData()
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