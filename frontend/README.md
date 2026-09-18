# Interface web locale

React, TypeScript et Glide Data Grid. Le serveur Python sert `dist/` sur la même origine que `/api` ; les données et le chat proviennent de ce serveur.

Le cockpit connecté est la destination `/`. La copie intégrée du visuel se trouve dans `src/cockpit` ; les vues branchées au serveur sont dans `src/connected`. `/demo` conserve une démonstration explicite sans API métier, tandis que `/atelier` ouvre les trois panneaux historiques pour la maintenance du modèle. Le dossier original fourni n’est pas modifié.

```powershell
cd frontend
npm ci
npm run build
```

Le serveur doit démarrer après le premier build pour monter les fichiers statiques. Le mode Vite (`npm run dev`) écoute sur `127.0.0.1:5173` et relaie `/api` vers `127.0.0.1:8765` ; la politique d’origine du serveur doit autoriser ce mode de développement. `VITE_API_TARGET` permet de choisir la cible du proxy. Pour une utilisation normale, ouvrir l’URL du serveur Python.

Dans le cockpit, les formulaires et la grille utilisent les champs métier et les permissions du modèle courant. Les modifications restent sourcées, liées à leur révision et réunies au brouillon. La grille charge des fenêtres de 100 lignes × 26 colonnes. L’atelier historique conserve ses trois panneaux redimensionnables, les propositions de formules et les actions structurelles. Leur calcul appartient au serveur et à Excel.

L’aperçu montre les valeurs/formules avant et après. L’application reste désactivée avant un état `READY` sans conflit. Les tâches échouées ou interrompues peuvent être reprises explicitement ; le serveur contrôle leur contexte. Les graphiques sont une représentation des données mises en cache dans le classeur et affichent leur état de calcul.

## Tests navigateur

```powershell
npx playwright install chromium
npm test
```

Ces tests utilisent des réponses API fictives pour vérifier les parcours de l’interface : ils n’exécutent ni Excel ni un fournisseur d’IA.

Les tests historiques sont conservés sur `/atelier`. Les tests `connected-*.spec.ts` couvrent le nouveau cockpit. `node --test tests/cockpit-state.test.mjs` vérifie le modèle d’état démo ; les scripts `cockpit-demo-browser.mjs` et `cockpit-demo-ui.mjs` utilisent un serveur Vite de recette pour ses parcours et son accessibilité. Les vérifications d’installation s’exécutent sur les fichiers réellement extraits du pack.

Une recette distincte utilise un vrai serveur local configuré avec un espace de données de test. Elle **crée un dossier fictif, une source et un brouillon**, puis vérifie la reprise et le téléchargement. Elle ne lance ni aperçu, ni application, ni recalcul, ni requête au fournisseur de chat.

```powershell
$env:TCA_WEB_LIVE_URL='http://127.0.0.1:8766'
npx playwright test --config playwright.live.config.ts
```

Ses reçus et captures sont dans `test-results/live-*`. Les téléchargements temporaires du navigateur utilisent un chemin court hors OneDrive pour éviter les erreurs de copie observées dans les artefacts du harnais. Les tests conservent la taille et l’empreinte du flux téléchargé, sans ouvrir le classeur.
