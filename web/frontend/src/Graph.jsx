import { useEffect, useState } from "react";
import { Card, CardBody, CardHeader, DropdownItem, DropdownMenu, DropdownToggle, InputGroup, UncontrolledDropdown } from "reactstrap";
import { Multiselect } from "multiselect-react-dropdown";
import { Line } from "react-chartjs-2";
import { getServerURL } from "./common";
import "chart.js/auto";
import "./Graph.css";

export default function Graph() {
    const [data, setData] = useState(undefined)
    const [rate, setRate] = useState(1000)
    const [entries, setEntries] = useState(30)
    const [selected, setSelected] = useState([
        { name: 'Temperature', id: 1 },
        { name: 'Pressure', id: 2 },
        { name: 'Humidity', id: 3 }
    ])

    const options = {
        maintainAspectRatio: false,
        scales: {
            A: {
                type: 'linear',
                position: 'right',
                beginAtZero: true
            },
            B: {
                type: 'linear',
                position: 'left',
                beginAtZero: true
            }
        },
        plugins: {
            legend: {
                display: false
            }
        }
    }

    const state = {
        options: [
            { name: 'Temperature', id: 1 },
            { name: 'Pressure', id: 2 },
            { name: 'Humidity', id: 3 },
            { name: 'Light', id: 4 },
            { name: 'Oxidised', id: 5 },
            { name: 'Reduced', id: 6 },
            { name: 'Ammonia', id: 7 }
        ]
    }

    const colors = [
        'rgba(255, 99, 132, 1.0)',
        'rgba(54, 162, 235, 1.0)',
        'rgba(255, 206, 86, 1.0)',
        'rgba(75, 192, 192, 1.0)',
        'rgba(153, 102, 255, 1.0)',
        'rgba(255, 159, 64, 1.0)',
        'rgba(255, 99, 132, 1.0)'
    ]

    let start = 0
    let results = []

    async function getData() {
        const url = getServerURL()
        url.pathname = '/data/enviro'
        url.searchParams.append('start', start)

        const response = await fetch(url)
        const json = await response.json()
        if (json.error) {
            console.log(json.data)
            return
        }

        results = results.concat(json.data)
        results = results.slice(-entries)

        const id = results.map(d => d[0])
        start = id[id.length - 1]

        const sets = [];
        selected.forEach(s => {
            sets.push({
                label: s.name,
                data: results.map(d => d[s.id]),
                borderColor: colors[s.id - 1],
                backgroundColor: colors[s.id - 1],
                yAxisID: s.id === 2 ? 'A' : 'B' // Pressure on right, everything else on left
            })
        })

        setData({
            labels: id,
            datasets: sets
        })
    }

    useEffect(() => {
        const interval = setInterval(() => {
            getData()
        }, rate)
        return () => clearInterval(interval)
    }, [rate, entries, selected])

    return (
        <Card className="m-3">
            <CardHeader>Enviro Data</CardHeader>
            <CardBody>
                <div className="d-flex justify-content-between flex-wrap">
                    <Multiselect
                        options={state.options}
                        displayValue="name"
                        placeholder=""
                        closeIcon="cancel"
                        selectedValues={selected}
                        onSelect={(list, _) => setSelected(list)}
                        onRemove={(list, _) => setSelected(list)}
                        selectedValueDecorator={(text, opt) => {
                            return <span className={"chip-id-" + opt.id}>{text}</span>
                        }}
                    />
                    <div>
                        <InputGroup>
                            <UncontrolledDropdown>
                                <DropdownToggle caret color="primary">Update Rate ({rate})</DropdownToggle>
                                <DropdownMenu>
                                    <DropdownItem onClick={() => setRate(250)}>250ms</DropdownItem>
                                    <DropdownItem onClick={() => setRate(500)}>500ms</DropdownItem>
                                    <DropdownItem onClick={() => setRate(1000)}>1s</DropdownItem>
                                    <DropdownItem onClick={() => setRate(2000)}>2s</DropdownItem>
                                    <DropdownItem onClick={() => setRate(5000)}>5s</DropdownItem>
                                </DropdownMenu>
                            </UncontrolledDropdown>
                            <UncontrolledDropdown className="ml-auto">
                                <DropdownToggle caret color="primary">Entries ({entries})</DropdownToggle>
                                <DropdownMenu>
                                    <DropdownItem onClick={() => setEntries(10)}>10</DropdownItem>
                                    <DropdownItem onClick={() => setEntries(20)}>20</DropdownItem>
                                    <DropdownItem onClick={() => setEntries(30)}>30</DropdownItem>
                                    <DropdownItem onClick={() => setEntries(40)}>40</DropdownItem>
                                    <DropdownItem onClick={() => setEntries(50)}>50</DropdownItem>
                                </DropdownMenu>
                            </UncontrolledDropdown>
                        </InputGroup>
                    </div>
                </div>
                <div className="mt-3">
                    {data ? <Line data={data} options={options} style={{ height: "500px" }} /> : null}
                </div>
            </CardBody>
        </Card>
    )
}