import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LINKS_FILE = path.join(__dirname, '../data/account-links.json');

export async function readLinks() {
    try {
        const data = await fs.readFile(LINKS_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        if (error.code === 'ENOENT') {
            // File doesn't exist, create it with empty links array
            await fs.writeFile(LINKS_FILE, JSON.stringify({ links: [] }));
            return { links: [] };
        }
        throw error;
    }
}

export async function writeLinks(data) {
    await fs.writeFile(LINKS_FILE, JSON.stringify(data, null, 2));
}