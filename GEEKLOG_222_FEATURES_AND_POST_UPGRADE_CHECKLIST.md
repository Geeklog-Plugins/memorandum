# Geeklog 2.1.1 → 2.2.2 : nouveautés et vérification post-migration

Document de référence pour les sites migrés. **Une migration SQL réussie ne vaut pas validation fonctionnelle.** Ne pas activer une fonctionnalité uniquement parce qu'elle est disponible.

## Évolutions à examiner

| Domaine | Contrôle |
| --- | --- |
| Routage / redirections | Anciennes URLs, statuts 200/301/404, boucles, URLs réécrites, plugins |
| SEO / données structurées | Articles, pages statiques, fils d'Ariane ; éviter les doublons avec thèmes et plugins |
| XMLSitemap / IndexNow | URLs publiées, dates, contenus privés, absence de notifications concurrentes |
| Blocs / thèmes | Emplacements personnalisés, conditions d'affichage selon appareil, templates par catégorie |
| Likes / Dislikes | Paramètres, rôles, anonymes, classements ; activation facultative |
| Emails | PHPMailer, modèles HTML et texte, adresse d'expéditeur, inscription, notifications, réinitialisation |
| Sessions | Connexion et déconnexion, expiration, cookies, séparation des domaines |
| Confidentialité et sécurité | Anonymisation IP, anti-spam, limitations, reCAPTCHA si activé |
| Recherche | Inclusion des pages statiques et résultats des plugins |
| Médias et comptes | Gestionnaire de fichiers, uploads, permissions, avatars automatiques |
| Localisation | Accents, langue, métadonnées traduites, UTF8MB4 |
| Administration | Sauvegardes, permissions, maintenance de commentaires, tâches planifiées |

Certaines options dépendent du thème, des plugins et de la configuration effective. Vérifier les fonctionnalités précises contre le code déployé et les [notes de version du cœur](https://github.com/Geeklog-Core/geeklog/releases).

## Contrôles par site (ordre recommandé)

### P0 — intégrité et sécurité
- [ ] Version du code et version de base 2.2.2 confirmées ; migration SQL achevée.
- [ ] Aucune requête ne présume l'existence de tables appartenant à des plugins désinstallés (ex. `gl_polltopics`).
- [ ] Préfixes SQL, chemins de données persistantes, paramètres et domaines corrects.
- [ ] Sessions et connexions administrateur isolées entre sites.
- [ ] Groupes, ACL, contenus privés et formulaires testés.
- [ ] Sauvegarde complète base + fichiers et restauration hors production validées.

### P1 — fonctionnement et SEO
- [ ] URL anciennes et nouvelles, redirections, canonical, hreflang.
- [ ] Données structurées cohérentes, sans balisage contradictoire entre cœur et plugins.
- [ ] XMLSitemap et IndexNow corrects, sans doublons.
- [ ] Blocs, menus et formulaires du thème Eclipse testés sur mobile et ordinateur.
- [ ] Emails réellement reçus (inscription, notifications, récupération de compte).
- [ ] Recherche, médias, téléchargements, accents et traductions vérifiés.
- [ ] Cookie Consent sans responsabilité redondante entre thème, cœur et plugin.

### P2 — adoption facultative
- [ ] Étudier Likes / Dislikes et leurs permissions avant activation.
- [ ] Examiner les nouveaux emplacements de blocs et templates par catégorie.
- [ ] Évaluer avatars automatiques, anonymisation IP et autres options de configuration.

## Multisite et automatisation

Répéter les contrôles **sur chaque domaine et base**, même avec un cœur Geeklog partagé. Contrôler particulièrement `HTTP_HOST`, `db-config.php`, `siteconfig.php`, chemins publics/privés, caches, cookies, tâches cron et conservation des données après vidage de cache.

**Monitor** peut relever versions, configuration, schéma SQL, fichiers, chemins, alertes et tests non destructifs. **Migrator** peut prévoir sauvegarde, préflight et migration SQL sûre avec historique. L'affichage, les emails reçus et les parcours utilisateur restent à valider manuellement.

Consigner pour chaque contrôle : site, priorité, statut (à faire / OK / échec / non applicable), preuve, date, responsable.

Le suivi opérationnel et l'ordre des travaux appartiennent au dépôt [todo](https://github.com/hostellerie/todo), sans recopier cette référence.
