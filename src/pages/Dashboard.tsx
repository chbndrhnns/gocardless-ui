import {useState} from 'react';
import {RefreshCw} from 'lucide-react';
import {SyncDashboard} from '../components/SyncDashboard';

export function Dashboard() {
    const [isRefreshing, setIsRefreshing] = useState(false);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        // Add refresh logic here
        setTimeout(() => setIsRefreshing(false), 1000);
    };

    return (
        <div>
            <div className="flex justify-end mb-4">
                <button
                    onClick={handleRefresh}
                    disabled={isRefreshing}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                    <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`}/>
                    Refresh
                </button>
            </div>
            <SyncDashboard/>
        </div>
    );
}