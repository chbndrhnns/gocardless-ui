import '@testing-library/jest-dom';
import {afterAll, afterEach, beforeAll} from 'vitest';
import {setupServer} from 'msw/node';
import {http, HttpResponse} from 'msw';

// Make vi available globally
// globalThis.vi = vi;

// Mock API handlers
export const handlers = [
    http.get('http://localhost:4000/api/lunchmoney/assets', () => {
        return HttpResponse.json({
            "assets": [
                {id: '-1', name: 'Some account', 'currency': 'EUR', 'balance_as_of': "2024-11-30T14:07:59.494Z"}
            ]
        });
    }),
    http.post('http://localhost:4000/api/sync', () => {
        return HttpResponse.json({
            "assets": [
                {id: '-1', name: 'Some account', 'currency': 'EUR', 'balance_as_of': "2024-11-30T14:07:59.494Z"}
            ]
        });
    }),
    http.get('http://localhost:4000/api/sync/status', () => {
        return HttpResponse.json({
            accounts: [
                {
                    gocardlessId: '123',
                    gocardlessName: 'Test Bank',
                    lunchmoneyName: 'Test Account',
                    lastSync: '2024-03-14T10:00:00Z',
                    nextSync: '2024-03-14T13:00:00Z',
                    lastSyncStatus: 'success',
                    lastSyncTransactions: 5,
                    isSyncing: false,
                    rateLimit: {
                        limit: 100,
                        remaining: 95,
                        reset: '2024-03-15T10:00:00Z'
                    }
                }
            ]
        });
    }),

    http.get('http://localhost:4000/api/requisitions/', () => {
        return HttpResponse.json({
            results: [
                {
                    id: 'req123',
                    created: '2024-03-14T10:00:00Z',
                    status: 'CR',
                    institution_id: 'bank123',
                    reference: 'test-ref',
                    accounts: ['acc123'],
                    link: 'https://example.com/link'
                }
            ]
        });
    }),
    http.get('http://localhost:4000/api/requisitions/req123', () => {
        return HttpResponse.json({
            results: {
                id: 'req123',
                created: '2024-03-14T10:00:00Z',
                status: 'CR',
                institution_id: 'bank123',
                reference: 'test-ref',
                accounts: ['acc123'],
                link: 'https://example.com/link'
            }
        });
    }),
];

const server = setupServer(...handlers);

// Start server before all tests
beforeAll(() => server.listen({onUnhandledRequest: 'error'}));

// Reset handlers after each test
afterEach(() => server.resetHandlers());

// Clean up after all tests
afterAll(() => server.close());