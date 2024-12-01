import {XCircle} from 'lucide-react';

interface ConfirmDialogProps {
    isOpen: boolean;
    title: string;
    message: string;
    confirmLabel?: string;
    cancelLabel?: string;
    onConfirm: () => void;
    onCancel: () => void;
}

export function ConfirmDialog({
                                  isOpen,
                                  title,
                                  message,
                                  confirmLabel = 'Confirm',
                                  cancelLabel = 'Cancel',
                                  onConfirm,
                                  onCancel
                              }: ConfirmDialogProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
                <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-medium text-gray-900">{title}</h3>
                        <button
                            onClick={onCancel}
                            className="text-gray-400 hover:text-gray-500"
                        >
                            <XCircle className="h-6 w-6"/>
                        </button>
                    </div>
                    <p className="text-sm text-gray-500 mb-6">{message}</p>
                    <div className="flex justify-end space-x-3">
                        <button
                            onClick={onCancel}
                            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        >
                            {cancelLabel}
                        </button>
                        <button
                            onClick={onConfirm}
                            className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                        >
                            {confirmLabel}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}