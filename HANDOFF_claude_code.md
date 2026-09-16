# OVERBOLT | NO BS — Document de transfert vers Claude Code

Dernière version stable de référence : **v3.5** (fichier `OVERBOLT_v3.5.html`, à utiliser comme `index.html`).

Ce document résume l'état complet de l'application pour permettre une reprise du travail dans Claude Code sans perdre le contexte accumulé.

---

## 1. Architecture générale

- **Fichier unique** : toute l'app (HTML + CSS + JS) tient dans un seul fichier `index.html` autonome, sans dépendance externe (sauf polices/scripts CDN éventuels).
- **PWA** : accompagnée de `sw.js` (service worker, stratégie stale-while-revalidate, nom de cache à incrémenter à chaque changement de fichiers) et `manifest.json` (nom affiché à l'installation).
- **Hébergement** : GitHub Pages, dépôt `mic67420/OVERBOLT` (renommé depuis `only-fonte`), publié à l'adresse `mic67420.github.io/overbolt/` (à confirmer — un problème de casse/404 a été rencontré lors du renommage, résolu depuis).
- **Stockage** : données 100% locales (`localStorage`), pas de backend.
- **Licence** : verrouillage par clé Gumroad (`api.gumroad.com/v2/licenses/verify`), avec un déblocage local caché (5 taps sur le titre en moins de 4s) pour les tests — ce déblocage n'affiche plus aucun retour visuel depuis la v3.1 (discret, indétectable).
- **Modèle de données clé** :
  - `state.dayOrder` : liste des noms de séances (ex: "Séance 1", "Séance 2"...)
  - `state.days[nom]` : objet par séance, avec `.exercises[]` (liste d'exercices actifs), `.archivedExercises[]` (exercices supprimés mais historique préservé), `.weeks[]` (semaines, chacune avec `.rows[]` = une ligne par exercice, chaque ligne a `.series[]` = les séries avec `charge`/`reps`/`rest`/`validated`)
  - Chaque semaine a `.locked` (verrouillée = passée, non modifiable) et `.session` (`startAt`/`endAt`/`lastActivityAt`)
  - Un exercice est identifié par un `id` unique par séance ; son nom (`exo.name`) est stocké UNE SEULE FOIS de façon centrale (pas par semaine) — sauf exception ajoutée en v3.3 (voir plus bas)

---

## 2. Fonctionnalités confirmées OK dans la v3.5 (base stable)

- Suivi des séances/exercices/séries avec charge, reps, temps de repos
- Historique complet par semaine, calendrier de suivi (Bilan)
- Archivage des exercices supprimés (historique jamais perdu)
- **Reprise cross-séance du meilleur poids/reps** : à la création d'une nouvelle semaine (auto ou bouton manuel "+ Ajouter une semaine"), chaque exercice compare sa propre valeur précédente avec toutes les autres séances ayant fait le même exercice (par nom) la semaine passée, et retient le poids le plus élevé (avec les reps associées). Un "instantané" des performances est figé AVANT toute rotation pour éviter les effets d'ordre entre séances. Fonction clé : `buildBestPerfSnapshot()`, utilisée dans `defaultWeek()`.
- **Règle de cohérence entre séances** : impossible de démarrer une séance (échauffement ou validation de série) si une AUTRE séance ou une semaine passée non résolue est encore "en cours" (démarrée, ni terminée ni annulée) — propose d'annuler ou de terminer l'autre avant de continuer. Fonction clé : `ensureSessionStarted()`.
- **Verrouillage des semaines passées contre les taps accidentels** : le clic sur une case de série d'une semaine `locked` est bloqué (garde ajoutée dans le handler `role === "validate"`).
- **Coche de tuile automatique uniquement** : la coche verte sur les tuiles Séance 1/2/3/4 ne peut plus être cochée manuellement (le tap sur `data-role="day-check-toggle"` a été neutralisé) — elle ne se déclenche que via la logique existante (tous les exercices + toutes les séries de la semaine validés → `toggleSeanceFinished()` appelé automatiquement).
- **Remplacement d'exercice avec historique préservé** (v3.3-3.4) : en tapant sur le nom d'un exercice, un choix apparaît — remplacer par un exercice déjà existant dans l'historique (ouvre un sélecteur, mode `"replace"` de `openExoPicker()`) ou par un nouveau nom (saisie libre). Mécanique :
  - Les semaines **déjà verrouillées** sont "gelées" : leur ligne reçoit un champ `row.nameAtTime` = ancien nom, affiché en **rouge, sur la même ligne que la date** (ex: "S.34 2026 · 17/08 · Développé couché"), tronqué avec ellipsis si trop long (`max-width:70px`, `title=` pour le nom complet).
  - La semaine **en cours** (non verrouillée) passe au nouveau nom. Si ce nom existe déjà ailleurs dans l'historique (actif OU archivé, toutes séances), ses meilleures valeurs connues sont reprises automatiquement (`applyExerciseReplace()`, recherche via nom en minuscule/trim). Sinon, la semaine en cours repart à zéro.
  - Fonction centrale : `applyExerciseReplace(exoR, newName)`, appelée depuis le handler `exo-rename` ET depuis le picker en mode replace.
- **Total "kg soulevés" par semaine** — *attention, cette fonctionnalité a été retirée lors d'un retour arrière à la v3.5 (le total avait été ajouté en v2.44, avant que la branche v3.x ne reparte d'une version antérieure). Si le client la redemande, il faudra la recoder : total = somme(charge × reps) des séries VALIDÉES uniquement, affiché sous les tuiles de série, mis à jour en direct à chaque validation sans réinitialiser le scroll.*
- **Badge semaine record 🏆** : la semaine avec le plus gros volume (charge×reps, toutes séries additionnées) d'un exercice est mise en avant, recalculée en direct à chaque validation (`refreshBestWeekBadge()`).
- Icônes SÉRIES (mascotte custom) et BILAN (image custom fournie par l'utilisateur), titre "OVERBOLT | **NO BS**" (NO BS en gras blanc).
- Rappel de notification en arrière-plan si une séance est en cours (fonctionne uniquement tant que l'onglet reste ouvert — limite technique navigateur, voir section 5).
- 16 langues traduites pour toutes les chaînes de texte de l'interface.

## 3. Fonctionnalité NON aboutie : l'effet "ressort" au scroll — retirée de la v3.5

### 3.1 Spécification précise attendue par le client (à respecter à la lettre)

Contexte : chaque exercice affiche son historique de semaines dans une rangée à défilement horizontal (`.exo-series-scroll`). L'utilisateur peut faire glisser vers la gauche pour consulter les semaines passées.

Comportement demandé :

1. **Scroll indépendant par exercice** — chaque carte d'exercice défile de façon totalement autonome. Aucune synchronisation entre les différentes cartes (contrairement à ce qui existait avant : `syncSeriesScrollers()` recopiait le `scrollLeft` d'une carte vers toutes les autres). Seule la ligne physiquement touchée doit bouger.
2. **Gel total tant que le doigt est posé** — dès que l'utilisateur touche l'écran sur une carte (même sans bouger le doigt, y compris en le laissant immobile plusieurs secondes), rien ne doit se déclencher. Aucun minuteur, aucune animation.
3. **Déclenchement quasi immédiat au relâchement** — dès que le doigt quitte l'écran, le retour doit démarrer avec un délai minimal (quelques dizaines de ms maximum, pas de longue attente).
4. **Mouvement de retour lent et doux** — le scroll doit revenir progressivement vers la position la plus à droite (semaine actuelle), sur une durée de l'ordre de 2 à 2,5 secondes, avec un easing doux du début à la fin (pas de démarrage brusque). Testé avec `easeInOutSine`.
5. **Interruption immédiate si retouché** — si l'utilisateur touche à nouveau l'écran PENDANT l'animation de retour (à tout moment), celle-ci doit s'arrêter instantanément et rendre le contrôle total au doigt, sans à-coup ni délai.
6. **Cycle répétable** — après une interruption et un nouveau relâchement, un nouveau retour doit se programmer selon les mêmes règles (2 à 5), indéfiniment.

### 3.2 Historique des tentatives (v3.6 à v3.13) et de leurs échecs

| Version | Approche tentée | Résultat |
|---|---|---|
| v3.6 | Détection basée sur les événements `scroll` (debounce 1.8s), easing `easeOutCubic`, durée 1.1s | Trop lent à démarrer, mouvement pas assez doux |
| v3.7 | Délai réduit à 150ms, durée allongée à 2.4s, easing `easeInOutSine` | Mieux, mais le "gel doigt posé" ne fonctionnait pas de façon fiable |
| v3.8 | Ajout de `touchstart`/`pointerdown` → `interruptSpring()` pour annuler l'animation en cours au retouché | Amélioration partielle, mais problème persistant : la barre "finit toujours par tirer" même doigt posé |
| v3.9 | Passage d'une détection basée sur `scroll` à une détection basée sur `touchstart`/`touchend` réels (`isPointerDown`), délai réduit à 100ms | Toujours peu fiable selon le client |
| v3.10 | Découverte que `touchstart`/`touchend` est documenté comme "peu fiable" par Chrome pour ce cas d'usage. Passage à l'événement natif **`scrollend`** (avec repli `touchend` pour Safari < 26.2), délai réduit à 40ms | Toujours signalé comme ne fonctionnant pas |
| v3.11 | Découverte que la **synchronisation entre toutes les cartes** (`syncSeriesScrollers` recopiant le scroll d'une carte sur toutes les autres) provoquait des faux déclenchements croisés. Suppression totale de cette synchronisation, état (`_isPointerDown`, `_isSpringAnimating`, `_springTimer`, `_springAnimId`) rendu propre à CHAQUE élément (stocké directement sur le DOM element, plus de variables globales partagées) | Toujours signalé comme ne fonctionnant pas |
| v3.12 | Ajout d'un **panneau de débogage visible à l'écran** (activé en tapant sur le numéro de version dans l'en-tête), qui journalise chaque événement avec horodatage relatif, pour diagnostiquer sans avoir besoin de vidéo (une seule capture d'écran suffit à voir tout l'historique) | Outil de diagnostic, a permis de trouver le bug ci-dessous |
| v3.13 | **Bug réel identifié via les logs** : l'animation de retour elle-même (qui modifie `scrollLeft` à chaque frame via `requestAnimationFrame`, ~60 fois/seconde) déclenchait ses propres événements `scrollend` — chaque assignation programmatique de `scrollLeft` étant interprétée par le navigateur comme un "geste de scroll qui vient de se terminer". Résultat observé dans les logs : boucle infinie `minuteur programmé (40ms)` → `scrollend REÇU` → `minuteur programmé` → ... toutes les ~15-20ms, sans jamais laisser le minuteur de 40ms aller à son terme. Pire : un `scrollend` "fantôme" issu de l'animation pouvait arriver juste après un `touchstart`, et écraser par erreur le flag `_isPointerDown` remis à `false`, expliquant que le gel ne tenait jamais. **Correctif appliqué** : garde `if(el._isSpringAnimating) return;` ajoutée en première ligne du handler `scrollend`, pour ignorer les événements auto-provoqués par notre propre animation. | **Le client a signalé "ça ne marche pas" même après ce correctif** — la cause exacte de cet échec persistant après la v3.13 reste **non identifiée**. C'est le point de reprise pour Claude Code. |

### 3.3 Point de reprise pour Claude Code

Le correctif de la v3.13 (garde `_isSpringAnimating` dans le handler `scrollend`) est **logiquement correct** au vu des logs collectés et corrige un bug réel et confirmé (boucle infinie de re-déclenchement). Pourtant le client a signalé que le problème persistait. Hypothèses à explorer en priorité, non testées faute de nouvelle capture de logs après la v3.13 :

1. **Un nouveau test avec le panneau de débogage (v3.12/v3.13) donnant des logs POST-correctif** n'a pas été obtenu avant l'abandon de cette branche — c'est la toute première chose à faire : redemander une capture d'écran du panneau après le correctif de la v3.13, pour voir si la boucle a bien disparu ou si un autre pattern est apparu.
2. Possibilité que **plusieurs éléments `.exo-series-scroll` soient à nouveau synchronisés involontairement** par un autre mécanisme non identifié (ex: `focusedWeekKey` / `detectFocusedWeek()` qui pourrait indirectement provoquer un rendu ou un recalcul affectant plusieurs cartes à la fois).
3. Vérifier si le **CSS `scroll-snap-type: x proximity`** (présent sur `.exo-series-scroll`, voir ligne CSS `.exo-series-scroll{...scroll-snap-type:x proximity;}`) interfère avec `scrollend` ou avec l'assignation manuelle de `scrollLeft` (le snapping natif du navigateur pourrait entrer en conflit avec l'animation programmatique, ou déclencher SES PROPRES `scrollend` après coup une fois l'utilisateur relâché, décalant légèrement la position finale de façon imprévisible).
4. Vérifier le comportement sur le **navigateur/OS exact du client** (Android Chrome d'après les captures précédentes) — la version précise de Chrome et d'Android pourrait avoir un comportement `scrollend` différent de ce qui est documenté.
5. Envisager d'abandonner `scrollend` et de repartir sur une architecture différente : par exemple, ne PAS utiliser `requestAnimationFrame` + assignation directe de `scrollLeft` pour l'animation de retour, mais plutôt `scrollTo({left, behavior:'smooth'})` natif avec une seule instruction (laisser le navigateur gérer l'animation en interne plutôt que de la piloter manuellement image par image) — ce qui éviterait de générer un flot d'événements `scroll`/`scrollend` auto-provoqués. Contrepartie : moins de contrôle fin sur l'easing/la durée exacte, et l'interruption au retouché (point 5 du cahier des charges) devra être testée avec cette approche (`el.scrollTo({left:0, behavior:'auto'})` pour couper court immédiatement si besoin).

Fonctions concernées (recherche par nom dans le fichier v3.13 conservé si besoin de comparaison, sinon reconstruire depuis zéro sur la base de la v3.5) : `syncSeriesScrollers()`, `interruptSpringLocal()`, `scheduleSpringBackLocal()`, `startSpringBackLocal()`, `springLog()` (outil de diagnostic, à garder si utile).

### 3.5 Tentative v3.14 (Claude Code) — reconstruction propre à partir de la v3.5

Nouvelle implémentation directement dans `OVERBOLT_v3.5.html`, en repartant de zéro sur cette base (donc `syncSeriesScrollers()` — présent tel quel dans le fichier v3.5 — a été entièrement supprimé).

**Changement d'architecture par rapport à toutes les tentatives précédentes (v3.6-v3.13)** : abandon total de l'événement `scroll`/`scrollend` comme déclencheur du ressort. Le relâchement du doigt est désormais détecté via `pointerup`/`pointercancel` (Pointer Events), et le gel via `pointerdown` — jamais via un événement que notre propre animation pourrait re-déclencher elle-même. Cela élimine par construction la classe de bug identifiée en v3.13 (boucle `scrollend` auto-provoquée).

- `initSeriesScroller(el)` : attaché à chaque `.exo-series-scroll` individuellement dans `renderSeriesList()` (remplace l'appel à `syncSeriesScrollers()`). Aucune référence croisée entre éléments — tout l'état (`_isPointerDown`, `_activePointerId`, `_isSpringAnimating`, `_springTimer`, `_springAnimId`, `_focusDetectTimer`) est stocké directement sur le DOM element concerné.
- `pointerdown` → `interruptSpringLocal(el)` (annule minuteur + rAF en cours) et pose le flag `_isPointerDown`.
- `pointerup`/`pointercancel` → `scheduleSpringBackLocal(el)`, qui programme `startSpringBackLocal(el)` après `SPRING_RELEASE_DELAY_MS` (50ms).
- `startSpringBackLocal(el)` anime `scrollLeft` vers `el.scrollWidth - el.clientWidth` (= semaine actuelle, la plus à droite) via `requestAnimationFrame`, easing `easeInOutSine`, durée `SPRING_DURATION_MS` (2300ms). Désactive `scroll-snap-type` le temps de l'animation (remis à vide ensuite) pour écarter l'hypothèse du point 3.3.3.
- La détection de semaine centrée (`detectFocusedWeek`) reste indépendante par carte (debounce `_focusDetectTimer` propre à chaque élément, plus de debounce global partagé).
- Panneau de débogage reconstruit : `#springDebugPanel` (bandeau vert/noir fixe en haut d'écran), activé/désactivé par **5 taps sur le numéro de version dans l'en-tête** (`#verTag`, en moins de 3s) via `toggleSpringDebug()`. Log horodaté via `springLog(el, msg)`.

**Vérifié en session (via injection JS de `PointerEvent` synthétiques dans le navigateur, logs du panneau de débogage à l'appui)** :
- Minuteur de 50ms respecté exactement entre le relâchement et le démarrage du ressort.
- Durée du ressort mesurée à 2.31s (conforme à la spec 2-2.5s), retour exact à la position cible.
- Interruption : un `pointerdown` en plein milieu de l'animation (à 800ms sur 2300ms) fige `scrollLeft` instantanément et il reste figé (vérifié 600ms plus tard) — aucune reprise ni saut.
- Cycle répété plusieurs fois de suite dans les logs sans dérive ni blocage.
- Aucune synchronisation croisée possible entre cartes : `syncSeriesScrollers()` était le seul mécanisme de partage de `scrollLeft` entre éléments et il a été supprimé sans remplacement équivalent.

**Reste à faire** : ce test a été fait en injectant des `PointerEvent` synthétiques dans un navigateur desktop (pas de vrai écran tactile disponible dans cet environnement). **Le point de reprise pour la prochaine session est un test réel sur le téléphone Android du client**, avec le panneau de débogage (5 taps sur `v3.14`) pour capturer une capture d'écran des logs en cas de souci — en particulier vérifier que Chrome Android envoie bien `pointerup`/`pointercancel` de façon fiable à la fin d'un vrai geste tactile (y compris en cas de scroll avec inertie), ce qui n'a pu être vérifié qu'en théorie ici.

### 3.4 Outil de diagnostic disponible

Un panneau de débogage a été développé (v3.12) : bandeau vert sur fond noir en haut de l'écran, activé/désactivé en tapant sur le numéro de version dans l'en-tête, qui journalise chaque événement clé (doigt posé, scrollend reçu ou ignoré, minuteur programmé, démarrage/interruption/fin du ressort) avec horodatage relatif en secondes. Conçu pour fonctionner avec une simple capture d'écran (accumule l'historique complet, pas juste l'état instantané) puisque le client ne peut pas fournir de vidéo. **Recommandé de reconstruire cet outil en premier** dans la nouvelle tentative, avant même de retoucher la logique du ressort, pour obtenir des données réelles à chaque itération plutôt que de deviner.

---

## 4. Autres points en attente / non résolus

- **Compatibilité iPhone** : jamais testée sur un vrai appareil. Le code contient déjà de bonnes pratiques (vibration API protégée, AudioContext avec repli webkit + déverrouillage au premier tap, dates au format ISO strict, meta tags Apple PWA) mais aucune garantie réelle sans test physique. Notifications limitées à iOS 16.4+ ET app installée sur écran d'accueil ET **indisponibles dans l'UE depuis iOS 17.4** (retrait forcé par Apple, raisons DMA).
- **Total "kg soulevés"** : retiré lors du retour à la v3.5 (voir section 2), à réintégrer si le client le redemande.
- **GitHub** : dépôt renommé `only-fonte` → `OVERBOLT`, un problème de 404 a été rencontré juste après le renommage (résolu en réessayant après quelques minutes + vérification de Settings > Pages). Le client n'est pas technique, toute instruction de publication doit être détaillée pas à pas.

---

## 5. Conventions établies avec le client

- Numérotation de version : format `vX.Y` (ex: `v3.5`), affiché dans l'en-tête à côté du titre.
- Toujours vérifier la syntaxe JS (`node --check`) et la validité HTML après chaque modification avant de livrer.
- Le client teste sur téléphone Android réel (Chrome), pas très à l'aise techniquement — donner des instructions très détaillées, étape par étape, pour toute manipulation GitHub.
- Préférence exprimée : garder toujours une version de référence fonctionnelle de côté avant d'expérimenter (pratique déjà suivie : v2.43.0, puis v3.5 comme points de restauration successifs).
