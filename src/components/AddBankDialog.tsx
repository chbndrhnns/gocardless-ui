import {useState} from 'react';
import {ChevronRight, Loader2, Search, X} from 'lucide-react';
import type {Institution} from '../types/gocardless';

interface AddBankDialogProps {
    isOpen: boolean;
    onClose: () => void;
    institutions: Institution[];
    isLoading: boolean;
    error: string | null;
    onInstitutionSelect: (institution: Institution) => void;
    selectedCountry: string;
    onCountryChange: (country: string) => void;
    isCreatingRequisition: boolean;
}

const COUNTRIES = [
    {code: 'de', name: 'Germany'},
    {code: 'fr', name: 'France'},
    {code: 'gb', name: 'United Kingdom'},
    {code: 'es', name: 'Spain'},
    {code: 'it', name: 'Italy'},
];

export function AddBankDialog({
                                  isOpen,
                                  onClose,
                                  institutions,
                                  isLoading,
                                  error,
                                  onInstitutionSelect,
                                  selectedCountry,
                                  onCountryChange,
                                  isCreatingRequisition,
                              }: AddBankDialogProps) {
    const [searchQuery, setSearchQuery] = useState('');

    if (!isOpen) return null;

    const filteredInstitutions = institutions.filter((institution) =>
        institution.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
                <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                    <h2 className="text-2xl font-semibold text-gray-900">Connect Your Bank</h2>
                    <button
                        onClick={onClose}
                        disabled={isCreatingRequisition}
                        className="text-gray-400 hover:text-gray-500 transition-colors disabled:opacity-50"
                    >
                        <X className="w-6 h-6"/>
                    </button>
                </div>

                <div className="p-6 space-y-4">
                    <div className="flex space-x-4 mb-6">
                        <select
                            value={selectedCountry}
                            onChange={(e) => onCountryChange(e.target.value)}
                            disabled={isCreatingRequisition}
                            className="block w-48 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50"
                        >
                            {COUNTRIES.map((country) => (
                                <option key={country.code} value={country.code}>
                                    {country.name}
                                </option>
                            ))}
                        </select>

                        <div className="relative flex-1">
                            <Search
                                className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5"/>
                            <input
                                type="text"
                                placeholder="Search banks..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                disabled={isCreatingRequisition}
                                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
                            />
                        </div>
                    </div>

                    {error && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                            {error}
                        </div>
                    )}

                    <div className="overflow-y-auto max-h-[400px]">
                        {isLoading ? (
                            <div className="space-y-4">
                                {[...Array(3)].map((_, i) => (
                                    <div key={i} className="animate-pulse flex items-center p-4 rounded-lg">
                                        <div className="w-12 h-12 bg-gray-200 rounded-lg mr-4"></div>
                                        <div className="flex-1">
                                            <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                                            <div className="h-3 bg-gray-200 rounded w-1/3"></div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : isCreatingRequisition ? (
                            <div className="flex flex-col items-center justify-center py-12 space-y-4">
                                <Loader2 className="w-8 h-8 text-blue-600 animate-spin"/>
                                <p className="text-gray-600">Creating bank connection...</p>
                            </div>
                        ) : filteredInstitutions.length === 0 ? (
                            <div className="text-center py-12">
                                <p className="text-gray-500">No banks found matching your search.</p>
                            </div>
                        ) : (
                            <div className="space-y-2">
                                {filteredInstitutions.map((institution) => (
                                    <button
                                        key={institution.id}
                                        onClick={() => onInstitutionSelect(institution)}
                                        disabled={isCreatingRequisition}
                                        className="w-full flex items-center p-4 rounded-lg hover:bg-gray-50 transition-colors group disabled:opacity-50"
                                    >
                                        <img
                                            src={institution.logo}
                                            alt={`${institution.name} logo`}
                                            className="w-12 h-12 object-contain rounded-lg"
                                        />
                                        <div className="ml-4 flex-1 text-left">
                                            <h3 className="font-medium text-gray-900">{institution.name}</h3>
                                            <p className="text-sm text-gray-500">{institution.bic}</p>
                                        </div>
                                        <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600"/>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}