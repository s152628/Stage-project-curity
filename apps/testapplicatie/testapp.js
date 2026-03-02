require('dotenv').config();
const express = require('express');
const session = require('express-session');
const { Issuer, generators, TokenSet } = require('openid-client');

const app = express();

app.set('trust proxy', 1); // Vertrouw de proxy (belangrijk voor jouw setup!)

app.use(session({
    secret: process.env.SESSION_SECRET || 'camazotz_geheim',
    resave: true,               // Forceer herschrijven van de sessie
    saveUninitialized: true,    // Maak direct een sessie aan
    name: 'curity_session',     // Een custom naam helpt soms bij debugging
    cookie: { 
        secure: false,          // MOET false zijn voor HTTP
        httpOnly: true, 
        sameSite: 'lax',        // 'Lax' staat toe dat de cookie wordt meegestuurd bij een redirect
        path: '/'               // Zorg dat de cookie overal in de app geldig is
    }
}));

let client;

async function setupClient() {
    try {
        // Gebruik de URL uit .env voor discovery
        const curityIssuer = await Issuer.discover(process.env.ISSUER_URL);
        
        client = new curityIssuer.Client({
            client_id: process.env.CLIENT_ID,
            client_secret: process.env.CLIENT_SECRET,
            redirect_uris: [process.env.REDIRECT_URI],
            response_types: ['code']
        });
        
        console.log('✅ Verbinding met Curity hersteld via Discovery');
    } catch (err) {
        console.error('❌ Discovery mislukt:', err);
        process.exit(1);
    }
}

app.get('/login', (req, res) => {
    const state = generators.state();
    const nonce = generators.nonce();

    // 1. Sla ze op in de sessie
    req.session.state = state;
    req.session.nonce = nonce;

    // 2. BOUW de URL
    const authUrl = client.authorizationUrl({
        scope: 'openid profile',
        state: state,
        nonce: nonce
    });

    // 3. FORCEER de save van de sessie
    req.session.state = state;
    req.session.save((err) => {
        console.log('--- LOGIN START ---');
        console.log('Sessie ID:', req.sessionID);
        console.log('State opgeslagen:', state);
        res.redirect(authUrl);
    });
});
app.get('/callback', async (req, res) => {
    // DEBUG: Kijk of de sessie nog leeft
    console.log('--- CALLBACK AANGEROEPEN ---');
    console.log('Sessie ID:', req.sessionID);
    console.log('State in sessie:', req.session.state);
    console.log('State in URL:', req.query.state);

    try {

        const params = client.callbackParams(req);
        
        // De cruciale check:
        const tokenSet = await client.callback(process.env.REDIRECT_URI, params, {
            state: req.session.state, // Als dit undefined is, krijg je jouw error
            nonce: req.session.nonce
        });

        req.session.tokens = tokenSet;
        res.redirect('/profile');
    } catch (err) {
        console.error('Callback error details:', err);
        res.status(500).send('Fout tijdens inloggen: ' + err.message);
    }
    
});

app.get('/profile', (req, res) => {
    if (!req.session.tokens) return res.redirect('/login');
    
    const tokens = new TokenSet(req.session.tokens);
    const claims = tokens.claims();
    
    console.log("Dit zijn je basis claims:", claims);

    res.json({
        status: "Ingelogd!",
        subject: claims.sub,
        issuer: claims.iss,
        full_payload: claims
    });
});

setupClient().then(() => {
    const port = process.env.PORT || 3000;
    app.listen(port, () => console.log(`🚀 App draait op http://127.0.0.1:${port}/login`));
});