# OVERBOLT | NO BS — Document de transfert (état au 20/10/2026)

Version de l'application en ligne : **v3.51** (fichier unique `index.html`, déployé tel quel par GitHub Pages).
Ce document remplace l'ancienne version (qui décrivait la v3.5). Il sert à reprendre le travail sans perdre le contexte.

---

## 1. Le projet en une page

- **Produit** : appli de suivi de musculation, PWA en un seul fichier HTML/CSS/JS autonome, sans backend (données dans `localStorage`, clé `muscleman_state_v1_6`).
- **Public / ton** : client (propriétaire) non technique, francophone ; veut des instructions pas à pas pour toute manipulation manuelle ; aime voir des **aperçus en image avant publication** ; ton marketing décalé/sarcastique : « Une appli de muscu. Pas une centrale nucléaire. ».
- **Vente** : Gumroad, **5 € en achat unique, sans abonnement**, clé de licence par vente. Page : `https://michaelwave210.gumroad.com/l/gktnl`. L'app se déverrouille avec la clé (écran de licence dans `index.html`).
- **Dépôts GitHub** :
  - `mic67420/OVERBOLT` : l'application (`index.html`, `sw.js`, `manifest.json`, docs). `main` est publié sur `https://mic67420.github.io/OVERBOLT/`.
  - `mic67420/mic67420.github.io` : **site de présentation** (page de vente, captures, vidéo) publié sur `https://mic67420.github.io/`. Contenu : `index.html`, `img/`, `video/`, `.nojekyll`.
  - Branche de travail `claude/claude-md-handoff-review-m08dij` du dépôt app : contient en plus le dossier `site/` (sources du site, visuels Gumroad, vidéos, scripts de montage). **`site/` ne doit JAMAIS être poussé sur `main`** (voir §6).

---

## 2. Architecture de l'application

- **Fichier unique** `index.html` : tout le CSS, le JS (un grand IIFE) et les traductions (16 langues, objet `TRANSLATIONS`, clés `settings_*`, `add_week_btn`, etc.). Un second bloc `<script>` final (enregistrement du service worker + détection de mise à jour) est **global** et doit rester **autonome** : il ne voit pas `state` ni `t` (ils sont dans l'IIFE).
- **`sw.js`** : service worker « réseau d'abord » (3 s de délai, `cache:"no-cache"`), `CACHE_NAME` à incrémenter à CHAQUE publication (actuellement `overbolt-cache-v41`).
- **Mise à jour automatique** : `checkForUpdate` compare le `<title>` en ligne à la version affichée ; rechargement auto si aucune séance en cours, sinon bandeau.
- **Licence** : écran `#licenseGate`. Vérification `POST https://api.gumroad.com/v2/licenses/verify` avec **`product_id` = `vdjG3nNeBBEqWwbecY8lrg==`** (identifiant du produit, exigé par Gumroad ; repli sur `product_permalink` = `gktnl` si vide) et `increment_uses_count=false`. Déblocage de test local caché : 5 taps sur `#lgTitle` en moins de 4 s (ne pas supprimer, ne pas le rendre visible).
- **Modèle de données** : `state.dayOrder` (noms de séances), `state.days[nom]` avec `.exercises[]`, `.archivedExercises[]`, `.weeks[]` (chaque semaine : `.rows[]`, `.locked`, `.startDate`, `.session{startAt,endAt}`) ; chaque ligne a `.series[]` (`charge`, `reps`, `rest`, `validated`, flags `chargeAuto/repsAuto/restAuto`). Un exercice a un `id` unique par séance.
- **Thèmes / couleurs** : `applyTheme` pose `html[data-theme]` ; 5 catégories de couleurs dans `state.settings` : `colorPrincipal`, `colorWarmup`, `colorSerie`, `colorAddRemove`, **`colorValid`** (5ᵉ couleur, validation des séries, défaut `#ff2d95`). Variables CSS `--neon`, `--warmup`, `--serie`, `--addrm`, `--valid` (+ `-soft`/`-glow`), `--ink-base` (#000 clair / #fff sombre), `--ink-active`, `--ink-done`, `--ink-on-serie`, `--ink-on-valid` (calculées par `applyInk`).
- **Tuile « couleurs au hasard »** (entre Séries et Bilan) : roue SVG à **5 secteurs**, bouton ↺ (historique en mémoire, `COLOR_CATEGORIES`), soleil/lune. **Règle de tirage** (`harmonyHexes`) : 4 couleurs homogènes d'une même palette (`homogeneousFour` : on écarte celle qui étale le plus les teintes) + **1 couleur tranchante** (`accentFor` : teinte la plus éloignée, très saturée) affectée à `colorValid`.
- **Contours** : règle de design du client — contour fin de **1 px noir en mode clair / blanc en mode sombre** sur tous les éléments (listes `:is(...)` dans le CSS pour les tuiles ; bordures `var(--ink-base)` pour les petits boutons : coches, flèches, ✕/↺, appareil photo, ronds de validation…). Texte en noir/blanc absolu. Fond translucide non négociable.

---

## 3. Fonctionnalités et règles métier confirmées

- Séances/exercices/séries avec charge, reps, repos ; chrono flottant (repos, échauffement, durée de séance) ; photos de réglage machine ; historique par semaine ; Bilan (calendrier du mois, stats, progression par exercice, badge ×N pour plusieurs séances un même jour).
- **Semaine automatique** (`checkAutoWeeksAll`) ou **manuelle** : le bouton « + Ajouter une semaine à toutes les séances » (v3.48) crée la nouvelle semaine pour **toutes** les séances à la fois (coches retirées, historique intact).
- **Meilleure perf d'une semaine à l'autre** : `buildBestPerfSnapshot()` + `defaultWeek()` reprennent la charge la plus haute (et ses reps) pour un même exercice (par nom), toutes séances confondues.
- **Charge augmentée en cours d'exercice** (v3.50) : si on augmente la charge d'une série (à partir de la série 2), les séries suivantes **non validées et plus basses** passent au même poids. Une baisse ne se propage pas. Les reps de la série 1 définissent celles des suivantes.
- **Remplacement d'exercice** (v3.50, `applyExerciseReplace`) : si l'exercice existe déjà (même nom, toutes séances, actifs ou archivés), on reprend ses données les plus récentes (nombre de séries, charge/reps/repos par série, photos, repos entre exercices) en relevant les séries à la meilleure charge connue ; les semaines passées gardent l'ancien nom (`nameAtTime`).
- **Cohérence des sessions** (`ensureSessionStarted`, `resolveSessionConflict`) : impossible de démarrer une séance si une autre est restée en cours.
- **Retour automatique à droite** des fenêtres d'exercice (effet ressort) : v3.49 = « chien de garde » (`setInterval` 0,8 s) qui ramène toute fenêtre au repos tout à droite, + pas de recopie du scroll au réaffichage, cible du ressort recalculée à chaque image. Une fenêtre touchée récemment (< 2,5 s) n'est jamais tirée de force.
- **Tendance charge/reps** : encadrés vert fixe `#1FBF5B` (hausse) / rouge fixe `#D90429` (baisse), indépendants des couleurs choisies.
- **Validation d'une série** (v3.47) : cercle + coche dans la couleur de validation sur fond translucide, coche cerclée de noir/blanc.
- Retour de fin de chrono : l'app fait un **flash plein écran** (2 pulsations) + pulsation du chrono — à éviter dans les montages vidéo accélérés.

---

## 4. Historique des versions (résumé)

| Version | Contenu |
|---|---|
| v3.5 | Base stable de départ (ancienne référence). |
| v3.15–3.22 | Dates réelles de séance, affichage de la semaine (du…au…), mise à jour automatique, tuile « couleurs au hasard » (roue). |
| v3.23–3.31 | Contour 1 px noir/blanc sur toutes les tuiles et paramètres ; palettes harmonieuses ; roue 4 secteurs ; transitions de couleur instantanées ; flamme d'échauffement (PNG). |
| v3.32–3.38 | Texte noir/blanc auto-contrasté, mise à jour auto fiabilisée, bug session fantôme corrigé. |
| v3.39–3.41 | Bilan cohérent (mois calendaire, séances fantômes), néon vert/rouge fixe. |
| v3.42–3.45 | Contours des icônes (soleil/lune/↺, coches, flèches, ✕/↺), coches visibles quel que soit le thème, « NO BS » et numéro d'exercice en noir/blanc. |
| v3.46–3.47 | 5ᵉ couleur (validation), roue 5 secteurs, règle « 4 homogènes + 1 tranchante ». |
| v3.48 | Ajout manuel d'une semaine pour toutes les séances. |
| v3.49 | Retour à droite forcé des fenêtres d'exercice. |
| v3.50 | Charge augmentée → séries suivantes alignées ; remplacement d'exercice = reprise des vraies données. |
| v3.51 | Vérification de licence Gumroad par `product_id`. |

---

## 5. Site, Gumroad, réseaux

- **Site** (`site/` sur la branche de travail, publié dans `mic67420.github.io`) : page FR/EN, vidéo de démonstration (36 s, sans son, sans clignotement), 4 captures (cadre téléphone au ratio 900/1805), FAQ, achat → Gumroad. Pour publier : copier `site/index.html`, `site/img/*`, `site/video/demo.mp4` et `demo.webm` dans le clone de `mic67420.github.io`, commit, push `main` (déploiement automatique, 1 à 3 minutes).
- **Gumroad** : produit « OVERBOLT | NO BS », 3 couvertures (`site/gumroad/couverture-1..3.png`), vignette diurne, texte `description.txt`, onglet Contenu (lien de l'app + clé de licence). Achat test à 100 % validé de bout en bout ; le code `test100` est épuisé. **Ne jamais coller le lien de l'app dans la description publique** (uniquement dans Contenu).
- **TikTok** : compte personnel `@mickwave_67` (e-mail `contact.micapps@gmail.com`), avatar `site/gumroad/avatar-reseaux.png`, adresse du site en texte dans la bio (lien cliquable seulement à 1 000 abonnés). 2 vidéos publiées : environ 600 vues chacune, **temps moyen regardé 1,4–1,5 s**, 0,5–0,9 % regardées en entier → problème d'accroche (écran d'appli peu lisible, rien ne bouge). Plan : tester des accroches immédiates (texte choc dès la 1ʳᵉ image, comparaison appli surchargée / OVERBOLT, plans réels de salle) et comparer le temps moyen regardé (TikTok Studio sur ordinateur : `tiktok.com/tiktokstudio`).
- **Facebook** : mis en pause (il faut un compte personnel au vrai nom pour créer une Page).
- **Montage vidéo** (`site/montage/`) : `edit2/3/4.py` (ffmpeg : recadrage 720×1280 sans barres Android, sous-titres, fin de vidéo avec prix), `intro2.html` + `render.js` (intro « appli de fitness surchargée → surchauffe → explosion à particules → logo », rendue image par image avec Playwright), `sfx.py` (bruitages synthétiques, **abandonnés** : jugés ridicules, le client ajoute des sons TikTok lui-même). Les enregistrements d'écran d'origine du client ne sont **pas** dans le dépôt (à redemander au client).

---

## 6. Procédures

**Git (obligatoire)** — ne jamais force-push, jamais de `site/` sur `main` :
1. Travailler et committer sur la branche de travail.
2. Publication de l'app : `git fetch origin main && git checkout -b tmp-main origin/main && git cherry-pick <commit(s)> && git push origin tmp-main:main`, puis revenir sur la branche, `git merge origin/main`, pousser la branche, supprimer `tmp-main`.
3. À chaque publication : incrémenter la version dans `<title>` ET dans `<span class="ver" id="verTag">`, incrémenter `CACHE_NAME` dans `sw.js`.

**Contrôles avant de pousser** :
- Syntaxe JS : extraire chaque `<script>` inline et lancer `node --check` ; `node --check sw.js`.
- CSS : compter `{`/`}` et `(`/`)` du bloc `<style>` (un `)` mal placé a déjà cassé toute la feuille de style).
- **Piège déjà rencontré (2 fois)** : `open('sw.js','w').write(open('sw.js').read()...)` **vide le fichier** (l'écriture tronque avant la lecture). Toujours lire dans une variable avant d'ouvrir en écriture, puis vérifier `wc -l sw.js` (56 lignes) avant de commiter.

**Tests** : Playwright (chromium dans `/opt/pw-browsers`), `page.clock.install`, état injecté dans `localStorage` à partir d'une sauvegarde JSON du client, captures avec `#floatTimer` et `.ver` masqués pour des images propres. Les appels réseau vers `api.gumroad.com` et `github.io` sont bloqués par le proxy du bac à sable : simuler avec `page.route`.

**Conventions client** : version `vX.Y` à incrémenter à chaque modification ; instructions manuelles détaillées pas à pas, en français, avec les libellés exacts des interfaces (Gumroad, TikTok et GitHub sont affichés en français, parfois par traduction automatique du navigateur) ; toujours garder la dernière version stable comme référence ; aperçu en image avant toute publication visuelle.

---

## 7. En attente / idées

- **Vidéos B et C pour TikTok** (accroche immédiate) : besoin d'un nouvel enregistrement d'écran du client ; plans réels de salle facultatifs.
- Suivre les statistiques TikTok Studio (temps moyen regardé) pour choisir l'accroche gagnante.
- Facebook : reprendre plus tard (Page « OVERBOLT | NO BS »).
- Compatibilité iPhone/Safari : testée seulement via Playwright (WebKit non disponible) ; pas de test sur vrai appareil.
- L'effet ressort a été testé uniquement avec des événements simulés ; un test réel sur le téléphone du client reste le juge de paix.
