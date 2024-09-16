import { useEffect, useState } from 'react'
import { Card, CardBody, CardHeader, Table } from 'reactstrap';
import { getServerURL } from './common';

export default function Logs() {
    const [data, setData] = useState(undefined)

    async function getData() {
        const url = getServerURL()
        url.pathname = '/data/enviro'

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
                                </tr>
                            )) : null}
                        </tbody>
                    </Table>
                </CardBody>
            </Card>
        </div>
    )
}