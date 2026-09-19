const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const KEYS_FILE = path.join(__dirname, 'keys.json');
const CONFIG_FILE = path.join(__dirname, 'localconfig.json');

function readJSON(file, defaultData) {
    if (!fs.existsSync(file)) {
        fs.writeFileSync(file, JSON.stringify(defaultData, null, 2));
        return defaultData;
    }
    try {
        return JSON.parse(fs.readFileSync(file, 'utf8'));
    } catch (e) {
        return defaultData;
    }
}

function writeJSON(file, data) {
    fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

function checkAdminAuth(req, res, next) {
    const password = req.headers['x-admin-password'];
    if (password === '20110829bavindu') {
        next();
    } else {
        res.status(401).json({ success: false, message: 'Access Denied: Invalid Admin Password' });
    }
}

// Config Endpoint for Game Client
app.get('/api/config', (req, res) => {
    const config = readJSON(CONFIG_FILE, { maintenance: false });
    res.json(config);
});

// Admin Routes
app.get('/api/admin/keys', checkAdminAuth, (req, res) => {
    const keys = readJSON(KEYS_FILE, []);
    const config = readJSON(CONFIG_FILE, { maintenance: false });
    res.json({ success: true, keys, config });
});

app.post('/api/admin/toggle-maintenance', checkAdminAuth, (req, res) => {
    const config = readJSON(CONFIG_FILE, { maintenance: false });
    config.maintenance = !config.maintenance;
    writeJSON(CONFIG_FILE, config);
    res.json({ success: true, maintenance: config.maintenance });
});

app.post('/api/admin/generate-key', checkAdminAuth, (req, res) => {
    const { durationDays } = req.body;
    const keys = readJSON(KEYS_FILE, []);
    
    const randomStr = Math.random().toString(36).substring(2, 8).toUpperCase();
    const newKey = `SIBOK-${durationDays}D-${randomStr}`;
    
    const keyData = {
        key: newKey,
        durationDays: parseInt(durationDays),
        createdAt: new Date().toISOString(),
        expiresAt: null,
        hwid: null,
        active: true
    };

    keys.push(keyData);
    writeJSON(KEYS_FILE, keys);
    res.json({ success: true, key: newKey });
});

// Client Key Authentication Route
app.post('/api/validate-key', (req, res) => {
    const { key, hwid } = req.body;
    const config = readJSON(CONFIG_FILE, { maintenance: false });

    if (config.maintenance) {
        return res.json({ valid: false, message: 'SYSTEM MAINTENANCE IN PROGRESS.' });
    }

    const keys = readJSON(KEYS_FILE, []);
    const keyIndex = keys.findIndex(k => k.key === key && k.active);

    if (keyIndex === -1) {
        return res.json({ valid: false, message: 'Invalid or Terminated Key Code.' });
    }

    let keyObj = keys[keyIndex];

    if (!keyObj.hwid) {
        keyObj.hwid = hwid;
        const now = new Date();
        now.setDate(now.getDate() + keyObj.durationDays);
        keyObj.expiresAt = now.toISOString();
    } else if (keyObj.hwid !== hwid) {
        return res.json({ valid: false, message: 'HWID LOCK ERROR: Key bound to another device!' });
    }

    if (new Date(keyObj.expiresAt) < new Date()) {
        keyObj.active = false;
        writeJSON(KEYS_FILE, keys);
        return res.json({ valid: false, message: 'Subscription Expired!' });
    }

    writeJSON(KEYS_FILE, keys);
    res.json({ valid: true, expiresAt: keyObj.expiresAt, config });
});

app.listen(PORT, () => {
    console.log(`SIBOK SENSI VIP Engine listening on port ${PORT}`);
});
