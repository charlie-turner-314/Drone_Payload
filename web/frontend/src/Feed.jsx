import { Card, CardBody, CardHeader, CardImg } from "reactstrap";

export default function Feed() {
    return (
        <Card>
            <CardHeader>Live Feed</CardHeader>
            <CardBody>
                <CardImg src="https://picsum.photos/300/200"></CardImg>
            </CardBody>
        </Card>
    )
}