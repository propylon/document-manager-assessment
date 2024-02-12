import React from 'react';
import { Navbar, Container, Button } from 'react-bootstrap';
import axios from 'axios';

const CustomNavbar = ({ isLoggedIn, handleLogout }) => {

  const logout = async (e) => {
    e.preventDefault();
    
    // Clear token from local storage
    localStorage.removeItem('token');
    
    handleLogout();

    try {
      await axios.post('http://localhost:8001/logout/', null, { withCredentials: true });
    } catch (error) {
      console.error('Logout request failed:', error);
    }
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="justify-content-between">
      <Container>
        <Navbar.Brand>Document Management</Navbar.Brand>
        <Navbar.Toggle aria-controls="navbar-collapse" />
        <Navbar.Collapse id="navbar-collapse" className="justify-content-end">
          <Navbar.Text>
            {isLoggedIn && (
              <>
                <span className="text-light mr-3">Welcome to Document Management</span>
                <Button onClick={logout} variant="secondary">Logout</Button>
              </>
            )}
          </Navbar.Text>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default CustomNavbar;
