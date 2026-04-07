import { useSelector, useDispatch } from 'react-redux';
import { toggleVisibility } from '../store/avatarSlice';

const Avatar = () => {
  const { currentState, isVisible } = useSelector((state) => state.avatar);
  const dispatch = useDispatch();

  const handleToggleVisibility = () => {
    dispatch(toggleVisibility());
  };

  if (!isVisible) {
    return (
      <button
        onClick={handleToggleVisibility}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-indigo-600 hover:bg-indigo-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center group"
        aria-label="Show avatar"
      >
        <svg className="w-6 h-6 transition-transform group-hover:scale-110" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <div className="relative">
        <div 
          className="w-20 h-20 rounded-full overflow-hidden transition-all duration-500 hover:scale-110 hover:-translate-y-2 group transform-gpu"
          style={{
            boxShadow: '0 4px 12px rgba(0,0,0,0.15), 0 2px 6px rgba(0,0,0,0.1)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.boxShadow = '0 12px 25px rgba(0,0,0,0.2), 0 6px 15px rgba(0,0,0,0.15)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15), 0 2px 6px rgba(0,0,0,0.1)';
          }}
        >
          <img
            src={`/avatar/listening.png`}
            alt={`Avatar listening`}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110 opacity-0 group-hover:opacity-100 absolute inset-0 z-10"
          />
          <img
            src={`/avatar/${currentState}.png`}
            alt={`Avatar ${currentState}`}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110 group-hover:opacity-0"
          />
          
          <div className="absolute inset-0 bg-gradient-to-br from-transparent to-black/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </div>
        
        <div className="absolute -top-2 -right-2">
          <div className={`w-4 h-4 rounded-full border-2 border-white shadow-lg transition-colors duration-300 ${
            currentState === 'idle' ? 'bg-green-400' :
            currentState === 'listening' ? 'bg-blue-400 animate-pulse' :
            currentState === 'thinking' ? 'bg-yellow-400 animate-pulse' :
            currentState === 'analyzing' ? 'bg-purple-400 animate-pulse' :
            currentState === 'presenting' ? 'bg-indigo-400' :
            currentState === 'encouraging' ? 'bg-green-500' :
            currentState === 'celebrating' ? 'bg-pink-400 animate-bounce' :
            currentState === 'error' ? 'bg-red-400 animate-pulse' :
            'bg-gray-400'
          } group-hover:bg-blue-400 group-hover:animate-pulse`} />
        </div>

        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
          <div className="bg-black/75 text-white text-xs px-2 py-1 rounded-md backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300 whitespace-nowrap">
            <span className="group-hover:hidden">{currentState.charAt(0).toUpperCase() + currentState.slice(1)}</span>
            <span className="hidden group-hover:block">Listening</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Avatar;