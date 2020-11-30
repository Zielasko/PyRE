# PyRE
Python scripts for parsing, processing and modifying various special file formats

# Example Commands

Shuffle DS3 Bullet Param
```
python .\main.py --name Bullet --random_self_refs 26 --chance 1 --shuffle --random_bullet_multiplier 32 --mult_max 3 --adjust_bullet_angle --visible_bullets 1 -p "../resources/DS3_params/" -l "../resources/DS3/Layouts/"
```

Shuffle Sekiro Bullet Param
```
 python -i .\main.py --name Bullet --random_self_refs 26 --chance 0.5 --shuffle --shuffle_safe --random_bullet_multiplier 32 --mult_max 3 --adjust_bullet_angle --visible_bullets 1 -p "../resources/default_gameparam-parambnd-dcx/param/GameParam/" -l "../resources/SDT/Layouts/"
```

