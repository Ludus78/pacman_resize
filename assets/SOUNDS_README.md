# Guide d'intégration des sons du jeu Pacman

## Description

Le système de gestion des sons a été intégré dans la boucle de jeu. Les effets sonores et la musique de fond s'activent automatiquement durant le jeu.

## Sons intégrés

### Effets sonores

1. **pellet_eat** - Joué quand Pacman mange une pastille normale
2. **power_pellet** - Joué quand Pacman mange une super-pastille (power-up)
3. **ghost_eaten** - Joué quand Pacman mange un fantôme
4. **death** - Joué quand Pacman meurt
5. **victory** - Joué quand un niveau est complété

### Musique de fond

6. **background** - Musique de fond, jouée en boucle pendant le jeu

## Installation des fichiers son

Les fichiers son doivent être placés dans le dossier `assets/sounds/`.

### Noms de fichiers acceptés

Le gestionnaire de sons recherche automatiquement les fichiers avec ces noms (dans cet ordre) :

#### Pour les pastilles

- `pellet.wav`
- `eat_pellet.wav`
- `chomp.wav`

#### Pour les super-pastilles

- `power_pellet.wav`
- `power.wav`
- `boost.wav`

#### Pour les fantômes mangés

- `ghost_eaten.wav`
- `eat_ghost.wav`
- `ghost.wav`

#### Pour la mort

- `death.wav`
- `die.wav`
- `gameover.wav`

#### Pour la victoire

- `victory.wav`
- `level_complete.wav`
- `win.wav`

#### Pour la musique de fond

- `background.wav`
- `music.wav`
- `theme.wav`

## Structure du dossier

```
pacman_resize/
├── assets/
│   └── sounds/
│       ├── pellet.wav              (ou eat_pellet.wav, chomp.wav)
│       ├── power_pellet.wav        (ou power.wav, boost.wav)
│       ├── ghost_eaten.wav         (ou eat_ghost.wav, ghost.wav)
│       ├── death.wav               (ou die.wav, gameover.wav)
│       ├── victory.wav             (ou level_complete.wav, win.wav)
│       └── background.wav          (ou music.wav, theme.wav)
├── game/
│   ├── sound_manager.py            (nouveau module)
│   ├── game_loop.py                (modifié)
│   └── collision_manager.py        (modifié)
└── ...
```

## Format des fichiers

Les fichiers son doivent être au format **WAV** (Waveform Audio File Format).

### Recommendations

- **Pastilles & Effets court** : 0.2-0.5 secondes
- **Musique de fond** : Qualité de jeu standard (44100 Hz, stéréo recommandé)
- **Tous les fichiers** : Format mono ou stéréo accepté

## Comment ça fonctionne

### Intégration dans la boucle de jeu

1. À l'initialisation du jeu, le `SoundManager` est créé et charge tous les sons disponibles
2. La musique de fond se lance automatiquement au démarrage
3. À chaque action du joueur, le son correspondant est joué :
   - Manger une pastille → `play_pellet_eat()`
   - Manger une super-pastille → `play_power_pellet()`
   - Manger un fantôme → `play_ghost_eaten()`
   - Mourir → `play_death()`
   - Compléter un niveau → `play_victory()`

### Appels dans le code

**game_loop.py** :

- Initialise et lance `SoundManager`
- Lance la musique au démarrage
- Arrête la musique à la fin du jeu
- Gère les sons de victoire et game over

**collision_manager.py** :

- Joue les sons lors des collisions avec pastilles, super-pastilles, fantômes

## Contrôle du volume

Le gestionnaire de sons permet de contrôler le volume :

```python
sound_manager.set_music_volume(0.5)      # Volume musique : 50%
sound_manager.set_effects_volume(0.7)    # Volume effets : 70%
sound_manager.stop_all()                 # Arrête tous les sons
```

## Messages de chargement

Au démarrage du jeu, le console affichera :

```
✓ Son chargé: pellet_eat (pellet.wav)
✓ Son chargé: power_pellet (power_pellet.wav)
✓ Son chargé: ghost_eaten (ghost_eaten.wav)
✓ Son chargé: death (death.wav)
✓ Son chargé: victory (victory.wav)
✓ Son chargé: background (background.wav)
```

Si un fichier est manquant :

```
⚠ Pas de fichier trouvé pour: pellet_eat
```

## Dépendances

- `pygame` (déjà dans requirements.txt) - utilisé pour la lecture audio

## Fichiers modifiés

- `game/game_loop.py` - Intégration du SoundManager
- `game/collision_manager.py` - Ajout des appels audio aux collisions
- `game/sound_manager.py` - **NOUVEAU** - Gestionnaire de sons

## Notes

- Les sons sont chargés de manière flexible : si un fichier manque, le jeu continue sans erreur
- La musique de fond boucle automatiquement
- Les effets sonores sont joués une seule fois (non boucle)
- En mode tournoi, les sons continuent de fonctionner normalement
