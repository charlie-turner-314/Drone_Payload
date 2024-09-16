import { useEffect, useState } from 'react'
import { Card, CardBody, CardHeader, Table } from 'reactstrap';
import { getServerURL } from './common';

export default function Logs() {
    const [data, setData] = useState(undefined)

    async function getData() {
        const url = getServerURL()
        url.pathname = '/data/all'

        const response = await fetch(url)
        const json = await response.json()
        if (json.error) {
            console.log(json.data)
            return
        }

        setData(json.data)
    }

    useEffect(() => {
        getData()
    }, [])

    return (
        <div>
            <Card className="m-3">
                <CardHeader>Raw Logs</CardHeader>
                <CardBody>
                    <Table responsive>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Temperature</th>
                                <th>Pressure</th>
                                <th>Humidity</th>
                                <th>Light</th>
                                <th>Oxidised</th>
                                <th>Reduced</th>
                                <th>Ammonia</th>
                                <th>Valve State</th>
                                <th>ArUCO ID</th>
                                <th>ArUCO Position</th>
                                <th>Pressure Guage</th>
                                <th>Timestamp</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data ? data.map((d, i) => (
                                <tr key={i}>
                                    <td>{d[0]}</td>
                                    <td>{d[1]}</td>
                                    <td>{d[2]}</td>
                                    <td>{d[3]}</td>
                                    <td>{d[4]}</td>
                                    <td>{d[5]}</td>
                                    <td>{d[6]}</td>
                                    <td>{d[7]}</td>
                                    <td>{d[8] === null ? "" : d[8] ? "Open" : "Closed"}</td>
                                    <td>{d[9]}</td>
                                    <td>{d[9] === null ? "" : `(${d[10]}, ${d[11]})`}</td>
                                    <td>{d[12]}</td>
                                    <td>{d[13]}</td>
                                </tr>
                            )) : null}
                        </tbody>
                    </Table>
                </CardBody>
            </Card>
        </div>
    )
}