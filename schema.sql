CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT NOT NULL UNIQUE,
    password   TEXT NOT NULL,
    email      TEXT NOT NULL,
    bio        TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS writeups (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    title      TEXT NOT NULL,
    content    TEXT NOT NULL,
    tags       TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS comments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    writeup_id INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    content    TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (writeup_id) REFERENCES writeups(id),
    FOREIGN KEY (user_id)    REFERENCES users(id)
);

-- Données de démo
INSERT OR IGNORE INTO users (username, password, email, bio) VALUES
    ('admin',   '21232f297a57a5a743894a0e4a801fc3', 'admin@hackboard.io',   'Fondateur de HackBoard. Root or nothing.'),
    ('h4x0r',   '5f4dcc3b5aa765d61d8327deb882cf99', 'h4x0r@hackboard.io',   'CTF player, bug bounty hunter.'),
    ('newbie',  'fe01ce2a7fbac8fafaed7c982a04e229', 'newbie@hackboard.io',  'Junior pentester en formation.');

INSERT OR IGNORE INTO writeups (user_id, title, content, tags) VALUES
    (1, 'RootMe - SQL Injection Auth Bypass',
     'Dans ce challenge, le formulaire de login est vulnérable à une injection SQL classique. En entrant `'' OR ''1''=''1` dans le champ username, on bypass complètement l''authentification...',
     'sqli,rootme,web'),
    (2, 'HackTheBox - XSS to Account Takeover',
     'Ce write-up explique comment exploiter un XSS stocké dans un forum pour voler les cookies de session d''un admin et prendre le contrôle de son compte...',
     'xss,htb,web,cookie'),
    (1, 'Introduction à Docker pour les pentesters',
     'Docker change la donne pour le pentest : environnements isolés, labs reproductibles, partage facile des outils. Voici comment je structure mes labs...',
     'docker,devsecops,tools');

INSERT OR IGNORE INTO comments (writeup_id, user_id, content) VALUES
    (1, 2, 'Super write-up ! J''ai eu le même challenge la semaine dernière.'),
    (1, 3, 'Merci, j''apprends beaucoup de ces explications.'),
    (2, 1, 'Beau travail sur le cookie hijacking. As-tu testé avec HttpOnly ?');
