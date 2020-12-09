# PyRE
Python scripts for parsing, processing and modifying various special file formats

Currently the main purpose is to massedit Sekiro or DS3 Paramfiles
The scripts can be either used as a library or directly by running the main.py script in a console

Example commands to create randomized  projectile setttings are listed below
For more detailed instructions use `--help` or take a look at main.py or paramops.py
There exist a range of functions to help prevent gamebreaking combinations caused by the randomizer + selfreferences (for example or infinite loops)

The scripts were tested for 50% of DS3 and Sekiro params
To load params you need to provide either Soulsformat Layout files or have a CE representation of the param already parsed

`https://github.com/soulsmods/Paramdex`
This will repository probably be added as a submodule at a later point
The paths are specified in main.py and can be dynamically changed using console args

# Example Commands

Shuffle DS3 Bullet Param
```
python .\main.py --name Bullet --random_self_refs 26 --chance 1 --shuffle --random_bullet_multiplier 32 --mult_max 3 --adjust_bullet_angle --visible_bullets 1 -p "../resources/DS3_params/" -l "../resources/DS3/Layouts/"
```

Shuffle Sekiro Bullet Param
```
 python -i .\main.py --name Bullet --random_self_refs 26 --chance 0.5 --shuffle --shuffle_safe --random_bullet_multiplier 32 --mult_max 3 --adjust_bullet_angle --visible_bullets 1 -p "../resources/default_gameparam-parambnd-dcx/param/GameParam/" -l "../resources/SDT/Layouts/"
```

```
python .\main.py --name Bullet --random_self_refs 26 --chance 1 --shuffle --shuffle_safe --secondary_only --random_bullet_multiplier 32 --mult_max 3 --adjust_bullet_angle --visible_bullets 1 -p "../resources/default_gameparam-parambnd-dcx/param/Gameparam/" -l "../resources/SDT/Layouts/" --limit 4 0.1 30 0.1 4
```