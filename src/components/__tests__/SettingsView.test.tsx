import {describe, expect, it} from 'vitest';
import {render, screen, waitFor} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {SettingsView} from '../SettingsView';
import {http, HttpResponse} from 'msw';
import {setupServer} from 'msw/node';

describe('SettingsView', () => {
    it('displays bank connections correctly', async () => {
        render(<SettingsView/>);

        await waitFor(() => {
            expect(screen.getByText('Active Connections')).toBeInTheDocument();
            expect(screen.getByText('bank123')).toBeInTheDocument();
        });
    });

    it('opens add bank dialog and handles country selection', async () => {
        const user = userEvent.setup();
        const server = setupServer(
            http.get('http://localhost:4000/api/institutions', ({request}) => {
                const url = new URL(request.url);
                const country = url.searchParams.get('country');
                return HttpResponse.json([
                    {
                        id: 'bank123',
                        name: `Test Bank ${country}`,
                        bic: 'TESTBIC',
                        logo: 'https://example.com/logo.png'
                    }
                ]);
            })
        );
        server.listen();

        render(<SettingsView/>);

        const addButton = screen.getByText('New Connection');
        await user.click(addButton);

        const countrySelect = screen.getByRole('combobox');
        await user.selectOptions(countrySelect, 'de');

        await waitFor(() => {
            expect(screen.getByText('Test Bank de')).toBeInTheDocument();
        });

        server.close();
    });

    it('handles bank connection deletion', async () => {
        const user = userEvent.setup();
        const server = setupServer(
            http.delete('http://localhost:4000/api/requisitions/req123', () => {
                return new HttpResponse(null, {status: 204});
            })
        );
        server.listen();

        render(<SettingsView/>);

        const deleteButton = await screen.findByLabelText('Delete connection');
        await user.click(deleteButton);

        const confirmButton = screen.getByText('Are you sure?');
        await user.click(confirmButton);

        await waitFor(() => {
            expect(screen.queryByText('bank123')).not.toBeInTheDocument();
        });

        server.close();
    });
});