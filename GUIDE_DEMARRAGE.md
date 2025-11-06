# 🎮 Guide de Démarrage Rapide - Pacman

## 🚀 Lancer le jeu

```bash
cd /home/ahmad/Documents/Ecole/pacmanresize/pacman_resize
python3 main.py
```

## 🎯 Contrôles

### Déplacement
- **Flèches** ou **ZQSD** : Déplacer Pacman
- **Entrée** : Valider / Relancer / Niveau suivant
- **Échap** : Quitter le jeu

### Debug
- **P** : Force la victoire (pour tester)

## 📖 Règles du Jeu

### Objectif
Manger **TOUS** les points (`.`) et super-points (`O`) sans se faire attraper par les fantômes !

### Pastilles
- **Petits points (`.`)** : +1 point
- **Super-pastilles (`O`)** : +10 points + pouvoir temporaire

### Pouvoirs des Super-Pastilles
Quand vous mangez une super-pastille :
1. 🔵 Les fantômes deviennent **violets** et fuient
2. ⚡ Vous devenez **50% plus rapide**
3. 👁️ Votre **champ de vision s'élargit** de 5 tuiles
4. 🎯 Vous pouvez **manger les fantômes** pour des points bonus

### Système de Combo
Mangez plusieurs fantômes pendant un pouvoir pour des points croissants :
- 1er fantôme : **10 points**
- 2ème fantôme : **20 points**
- 3ème fantôme : **40 points**
- 4ème fantôme+ : **80 points**

### Progression
1. **Niveaux 1-3** : Cartes statiques prédéfinies
2. **Niveaux 4+** : Cartes générées aléatoirement
   - Taille variable
   - Difficulté croissante
   - Fantômes de plus en plus rapides

### Champ de Vision
- Commence large au début du niveau
- **Rétrécit progressivement** au fil du temps
- Plus rapide à chaque niveau
- Minimum : 5 tuiles de rayon
- S'élargit avec les super-pastilles

## 🎨 Interface

### Barre Supérieure
```
┌─────────────────────────────────────────┐
│ Level X     PACMAN     Score XXXXX   MM:SS  Boost: Xs │
└─────────────────────────────────────────┘
```

- **Level** : Niveau actuel
- **PACMAN** : Titre du jeu
- **Score** : Points accumulés
- **Temps** : Durée de la partie (MM:SS)
- **Boost** : Temps restant du pouvoir (si actif)

## 🏆 Victoire

Vous gagnez quand **TOUS** les points sont mangés :
- ✅ Tous les petits points (`.`)
- ✅ Toutes les super-pastilles (`O`)

Un écran de victoire s'affiche avec :
- Votre score
- Un bouton "Niveau suivant"

## ☠️ Game Over

Si un fantôme vous touche en dehors d'un pouvoir :
- Écran "GAME OVER"
- Affichage du score final
- **Entrée** : Recommencer au niveau 1
- **Échap** : Quitter

## 📊 Éléments Visuels

### Couleurs
- 🟡 **Pacman** : Jaune doré
- 🔴 **Fantôme rouge** : Chef, agressif
- 🔵 **Fantôme bleu** : Embuscade
- 💗 **Fantôme rose** : Rapide
- 🟠 **Fantôme orange** : Imprévisible
- 🟣 **Fantômes apeurés** : Violet (mangeable)
- ⚪ **Petits points** : Blancs
- ⚪ **Super-pastilles** : Plus gros, blancs brillants
- 🔵 **Murs** : Bleu foncé

## 🎯 Stratégies

### Pour Débutants
1. 🎯 Mémorisez les positions des super-pastilles
2. 👻 Gardez un œil sur les fantômes
3. 🔄 Utilisez les bords de la carte pour échapper
4. ⚡ Économisez les super-pastilles pour les moments critiques

### Pour Experts
1. 🎮 **Combo de fantômes** : Mangez-les tous pendant un pouvoir
2. ⏱️ **Gestion du temps** : Finissez avant que le FOV soit trop petit
3. 🗺️ **Planification** : Tracez un chemin optimal
4. 🏃 **Vitesse** : Profitez du boost pour nettoyer rapidement

## 🛠️ Développement

### Structure du Code
```
main.py              → Point d'entrée (29 lignes)
game/
  ├── constants.py   → Constantes du jeu
  ├── utils.py       → Fonctions utilitaires
  ├── level_manager.py → Gestion des niveaux
  ├── game_state.py  → État du jeu
  ├── renderer.py    → Rendu visuel
  ├── collision_manager.py → Collisions
  └── game_loop.py   → Boucle principale
```

### Modifier les Paramètres
Éditez `game/constants.py` pour ajuster :
- Vitesses (Pacman, fantômes)
- Durée des pouvoirs
- Champ de vision
- Points des collectibles
- Couleurs

### Ajouter des Niveaux
Placez vos fichiers `.map` dans `assets/maps/` :
- `maplv1.map` (niveau 1)
- `maplv2.map` (niveau 2)
- `maplv3.map` (niveau 3)

Format des cartes :
- `#` : Mur
- `.` : Pastille normale
- `O` ou `o` : Super-pastille
- `P` : Position de départ de Pacman
- `G` : Position de départ d'un fantôme
- `C` : Cage (respawn des fantômes)
- ` ` : Espace vide

## 📚 Documentation Complète

- **REFACTORING.md** : Détails de la refactorisation
- **game/README.md** : Architecture des modules
- **requirements.txt** : Dépendances Python

## 🐛 Problèmes Connus

Aucun ! Le système de victoire et toutes les fonctionnalités ont été testés et corrigés.

## 💡 Astuces

1. **Les fantômes poursuivent activement** : Ils ne bougent pas au hasard !
2. **Le FOV rétrécit plus vite** à chaque niveau
3. **La vitesse des fantômes augmente** de 10% par niveau
4. **Les pouvoirs durent moins longtemps** aux niveaux élevés
5. **Mangez les fantômes** pour maximiser votre score

## 🎉 Amusez-vous bien !

Le jeu a été entièrement refactorisé pour une expérience optimale :
- ✅ Code propre et modulaire
- ✅ Performance optimisée
- ✅ Bugs corrigés
- ✅ Gameplay fluide

**Bon jeu ! 🎮**

