import {API_CONFIG} from '../config/api';
import type {LunchmoneyApiResponse, LunchmoneyAsset} from '../types/lunchmoney';

export async function fetchLunchmoneyAssets(): Promise<LunchmoneyAsset[]> {
    try {
        const response = await fetch(`${API_CONFIG.baseUrl}/lunchmoney/assets`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(
                errorData?.message || `API error: ${response.status} ${response.statusText}`
            );
        }
        const data: LunchmoneyApiResponse = await response.json();
        return data.assets;
    } catch (error) {
        console.error('Error fetching Lunchmoney assets:', error);
        throw error;
    }
}

export async function linkLunchmoneyAccount(lunchmoneyId: number, gocardlessId: string): Promise<void> {
    try {
        const response = await fetch(`${API_CONFIG.baseUrl}/lunchmoney/link`, {
            method: 'POST',
            headers: API_CONFIG.headers,
            body: JSON.stringify({lunchmoneyId, gocardlessId}),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(
                errorData?.message || `API error: ${response.status} ${response.statusText}`
            );
        }
    } catch (error) {
        console.error('Error linking accounts:', error);
        throw error;
    }
}

export async function unlinkLunchmoneyAccount(lunchmoneyId: number, gocardlessId: string): Promise<void> {
    try {
        const response = await fetch(`${API_CONFIG.baseUrl}/lunchmoney/unlink`, {
            method: 'POST',
            headers: API_CONFIG.headers,
            body: JSON.stringify({lunchmoneyId, gocardlessId}),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(
                errorData?.message || `API error: ${response.status} ${response.statusText}`
            );
        }
    } catch (error) {
        console.error('Error unlinking account:', error);
        throw error;
    }
}