import { env } from '../config/env.js';
import { readLinks, writeLinks } from './storage.js';

const LUNCHMONEY_API_URL = 'https://dev.lunchmoney.app/v1';

async function getLunchmoneyHeaders() {
  return {
    'Authorization': `Bearer ${env.lunchmoney_token}`,
    'Content-Type': 'application/json',
  };
}

export async function getAssets() {
  try {
    const response = await fetch(`${LUNCHMONEY_API_URL}/assets`, {
      method: 'GET',
      headers: await getLunchmoneyHeaders(),
    });
    const jsonResponse = await response.json();

    // Get linked accounts to add linking information
    const { links } = await readLinks();

    // Add linked status to each asset
    const assetsWithLinks = jsonResponse.assets.map(asset => ({
      ...asset,
      linked_account: links.find(link => link.lunchmoneyId === asset.id)?.gocardlessId || null
    }));

    return assetsWithLinks;
  } catch (error) {
    console.error('Error fetching Lunchmoney assets:', error);
    throw new Error('Failed to fetch Lunchmoney assets');
  }
}

export async function linkAccounts(lunchmoneyId, gocardlessId) {
  try {
    const data = await readLinks();

    // Remove any existing links for either account
    data.links = data.links.filter(link =>
        link.lunchmoneyId !== lunchmoneyId &&
        link.gocardlessId !== gocardlessId
    );

    // Add new link
    data.links.push({
      lunchmoneyId,
      gocardlessId,
      createdAt: new Date().toISOString()
    });

    await writeLinks(data);
    return true;
  } catch (error) {
    console.error('Error linking accounts:', error);
    throw new Error('Failed to link accounts');
  }
}

export async function unlinkAccounts(lunchmoneyId) {
  try {
    const data = await readLinks();
    data.links = data.links.filter(link => link.lunchmoneyId !== lunchmoneyId);
    await writeLinks(data);
    return true;
  } catch (error) {
    console.error('Error unlinking accounts:', error);
    throw new Error('Failed to unlink accounts');
  }
}