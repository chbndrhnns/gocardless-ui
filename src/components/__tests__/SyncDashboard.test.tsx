import {describe, expect, it} from 'vitest';
import {render, screen, waitFor} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {SyncDashboard} from '../SyncDashboard';
import {http, HttpResponse} from 'msw';
import {setupServer} from 'msw/node';
import {act} from "react";

describe('SyncDashboard', () => {
    it('displays sync status information', async () => {
        render(<SyncDashboard/>);

        await waitFor(() => {
            expect(screen.getByText('Test Bank')).toBeInTheDocument();
            expect(screen.getByText('5 transactions synced')).toBeInTheDocument();
        });
    });

    it('handles sync trigger correctly', async () => {
        const user = userEvent.setup();
        const server = setupServer(
            http.post('http://localhost:4000/api/sync', () => {
                return HttpResponse.json({status: 'success'});
            })
        );
        server.listen();

        render(<SyncDashboard/>);

        const syncButton = await screen.findByText('Sync Now');
        act(() => {
            await user.click(syncButton);
        })

        await waitFor(() => {
            expect(syncButton).toBeDisabled();
            expect(screen.getByText('Syncing...')).toBeInTheDocument();
        });

        server.close();
    });

    it('displays error state appropriately', async () => {
        const server = setupServer(
            http.get('http://localhost:4000/api/sync/status', () => {
                return HttpResponse.error();
            })
        );
        server.listen();

        render(<SyncDashboard/>);

        await waitFor(() => {
            expect(screen.getByText(/failed to fetch sync status/i)).toBeInTheDocument();
        });

        server.close();
    });
});