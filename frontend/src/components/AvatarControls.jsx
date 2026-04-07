import { useDispatch, useSelector } from 'react-redux';
import {
  setIdle,
  setListening,
  setThinking,
  setAnalyzing,
  setPresenting,
  setEncouraging,
  setCelebrating,
  setError
} from '../store/avatarSlice';

const AvatarControls = () => {
  const dispatch = useDispatch();
  const { currentState } = useSelector((state) => state.avatar);

  const avatarActions = [
    { action: setIdle, label: 'Idle', color: 'bg-green-500' },
    { action: setListening, label: 'Listening', color: 'bg-blue-500' },
    { action: setThinking, label: 'Thinking', color: 'bg-yellow-500' },
    { action: setAnalyzing, label: 'Analyzing', color: 'bg-purple-500' },
    { action: setPresenting, label: 'Presenting', color: 'bg-indigo-500' },
    { action: setEncouraging, label: 'Encouraging', color: 'bg-green-600' },
    { action: setCelebrating, label: 'Celebrating', color: 'bg-pink-500' },
    { action: setError, label: 'Error', color: 'bg-red-500' },
  ];

  return (
    <div className="p-4 bg-gray-50 rounded-lg">
      <h3 className="text-lg font-semibold mb-3">Avatar Controls</h3>
      <p className="text-sm text-gray-600 mb-4">Current state: <span className="font-medium">{currentState}</span></p>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {avatarActions.map(({ action, label, color }) => (
          <button
            key={label}
            onClick={() => dispatch(action())}
            className={`${color} hover:opacity-80 text-white px-3 py-2 rounded text-sm font-medium transition-opacity`}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default AvatarControls;