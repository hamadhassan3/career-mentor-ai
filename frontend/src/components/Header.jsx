import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Logo from './Logo';
import UserAvatar from './UserAvatar';

export default function Header() {
  const renderNavigation = () => {
    return (
      <div className="flex items-center">
        <UserAvatar />
      </div>
    );
  };

  const logoElement = (
    <Link to="/" className="flex items-center gap-3">
      <Logo size="header" />
      <span className="text-xl font-bold text-gray-900 tracking-tight">{process.env.REACT_APP_NAME}</span>
    </Link>
  );

  return (
    <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-lg border-b border-gray-100 w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        {logoElement}
        {renderNavigation()}
      </div>
    </header>
  );
}