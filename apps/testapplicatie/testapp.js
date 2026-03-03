require('dotenv').config();
const express = require('express');
const session = require('express-session');
const { Issuer, generators, TokenSet } = require('openid-client');
const path = require('path');

const app = express();

app.set('trust proxy', 1); 
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public')));

app.use(session({
    secret: process.env.SESSION_SECRET || 'camazotz_geheim',
    resave: false,              
    saveUninitialized: true,        
    cookie: { 
        secure: true,          
        httpOnly: true, 
        sameSite: 'lax',                   
    }
}));

let client;

async function setupClient() {
    try {
        const curityIssuer = await Issuer.discover(process.env.ISSUER_URL);
        
        client = new curityIssuer.Client({
            client_id: process.env.CLIENT_ID,
            client_secret: process.env.CLIENT_SECRET,
            redirect_uris: [process.env.REDIRECT_URI],
            response_types: ['code']
        });
        
        console.log('Verbinding met Curity hersteld via Discovery');
    } catch (err) {
        console.error('Discovery mislukt:', err);
        process.exit(1);
    }
}
app.get('/', (req, res) => {
    res.render('index', { user: req.session.user });
});

app.get('/login', (req, res) => {
    const state = generators.state();
    const nonce = generators.nonce();


    req.session.state = state;
    req.session.nonce = nonce;

    const authUrl = client.authorizationUrl({
        scope: 'openid',
        state: state,
        nonce: nonce
    });

    req.session.save((err) => {
        console.log('State opgeslagen:', state);
        res.redirect(authUrl);
    });
});
app.get('/callback', async (req, res) => {
    try {

        const params = client.callbackParams(req);
        
        const tokenSet = await client.callback(process.env.REDIRECT_URI, params, {
            state: req.session.state, 
            nonce: req.session.nonce
        });

        req.session.user = tokenSet.claims();
        res.redirect('/profile');
    } catch (err) {
        console.error('Callback error details:', err);
        res.status(500).send('Fout tijdens inloggen: ' + err.message);
    }
    
});

app.get('/profile', (req, res) => {
    if (!req.session.user) return res.redirect('/login');
    
    res.render('profile', { user: req.session.user });

});

app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/');
});

setupClient().then(() => {
    const port = process.env.PORT || 3000;
    app.listen(port, () => console.log(`App draait op poort ${port}`));
});