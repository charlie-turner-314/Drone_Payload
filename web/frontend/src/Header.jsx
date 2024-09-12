import { Nav, Navbar, NavItem, NavLink } from 'reactstrap';

export default function Header() {
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
                    <NavLink href='#'>Settings</NavLink>
                </NavItem>
            </Nav>
        </Navbar>
    )
}