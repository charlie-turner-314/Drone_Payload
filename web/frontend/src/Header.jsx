import { DropdownItem, DropdownMenu, DropdownToggle, Nav, Navbar, NavItem, NavLink, UncontrolledDropdown } from "reactstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faVolumeHigh, faVolumeXmark } from "@fortawesome/free-solid-svg-icons";
import { useDispatch, useSelector } from "react-redux";
import { setRate, toggleMute } from "./Store";

export default function Header() {
    const dispatch = useDispatch()
    const mute = useSelector(state => state.mute)
    const rate = useSelector(state => state.rate)

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
                <UncontrolledDropdown nav inNavbar>
                    <DropdownToggle nav caret>
                        Update Rate ({rate})
                    </DropdownToggle>
                    <DropdownMenu>
                        <DropdownItem onClick={() => dispatch(setRate(250))}>250ms</DropdownItem>
                        <DropdownItem onClick={() => dispatch(setRate(500))}>500ms</DropdownItem>
                        <DropdownItem onClick={() => dispatch(setRate(1000))}>1s</DropdownItem>
                        <DropdownItem onClick={() => dispatch(setRate(2000))}>2s</DropdownItem>
                        <DropdownItem onClick={() => dispatch(setRate(5000))}>5s</DropdownItem>
                    </DropdownMenu>
                </UncontrolledDropdown>
            </Nav>
        </Navbar>
    )
}