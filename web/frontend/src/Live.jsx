import { CardGroup } from "reactstrap";

import Feed from "./Feed";
import Imagery from "./Imagery";
import Graph from "./Graph";
import Controls from "./Controls";

export default function Live() {
    return (
        <div>
            <CardGroup className="mx-3">
                <Feed />
                <Imagery />
                {/* <Controls /> */}
            </CardGroup>
            <Graph />
        </div>
    )
}