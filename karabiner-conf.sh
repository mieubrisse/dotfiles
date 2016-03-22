#!/bin/sh

cli=/Applications/Karabiner.app/Contents/Library/bin/karabiner

$cli set remap.fkeys_to_consumer_f10 1
/bin/echo -n .
$cli set parameter.keyoverlaidmodifier_initial_modifier_wait 20
/bin/echo -n .
$cli set remap.fkeys_to_consumer_f1 1
/bin/echo -n .
$cli set remap.escape2capslock 1
/bin/echo -n .
$cli set remap.controlL2controlL_escape 1
/bin/echo -n .
$cli set parameter.keyoverlaidmodifier_timeout 300
/bin/echo -n .
$cli set remap.fkeys_to_consumer_f7 1
/bin/echo -n .
/bin/echo
