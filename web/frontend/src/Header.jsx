import { Nav, Navbar, NavItem, NavLink } from "reactstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faVolumeHigh, faVolumeXmark } from "@fortawesome/free-solid-svg-icons";
import { useDispatch, useSelector } from "react-redux";
import { toggleMute } from "./Store";

export default function Header() {
    const dispatch = useDispatch()
    const mute = useSelector(state => state.mute)

    return (
        <Navbar>
            <Nav className="w-100">
                <NavItem>
                    <NavLink href="/">Live</NavLink>
                </NavItem>
                <NavItem>
                    <NavLink href="/logs">Logs</NavLink>
                </NavItem>
                <NavItem className="ms-auto">
                    <NavLink href='#'>
                        <FontAwesomeIcon icon={mute ? faVolumeXmark : faVolumeHigh} onClick={() => dispatch(toggleMute())} />
                    </NavLink>
                </NavItem>
            </Nav>
        </Navbar>
    )
}