import {Link, Outlet, useLocation} from 'react-router-dom';
import {Settings} from 'lucide-react';

export function Layout() {
    const location = useLocation();

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">GoCardless Sync</h1>
                        <p className="mt-1 text-sm text-gray-500">
                            Sync your bank transactions with Lunch Money
                        </p>
                    </div>
                </div>

                <div className="mb-8">
                    <nav className="flex space-x-4" aria-label="Tabs">
                        <Link
                            to="/"
                            className={`px-3 py-2 font-medium text-sm rounded-md ${
                                location.pathname === '/'
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'text-gray-500 hover:text-gray-700'
                            }`}
                        >
                            Sync Status
                        </Link>
                        <Link
                            to="/settings"
                            className={`inline-flex items-center px-3 py-2 font-medium text-sm rounded-md ${
                                location.pathname === '/settings'
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'text-gray-500 hover:text-gray-700'
                            }`}
                        >
                            <Settings className="h-4 w-4 mr-2"/>
                            Settings
                        </Link>
                    </nav>
                </div>

                <Outlet />
            </div>
        </div>
    );
}