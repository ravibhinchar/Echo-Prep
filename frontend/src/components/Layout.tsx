import { Outlet } from 'react-router-dom';
import Navbar from './Navbar.js';

const Layout = () => {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-grow">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;