#!/bin/bash

kill $(ps -x | grep notify_me | sed -rn 's/^\s+([0-9]*).*notify_me\.py$/\1/p')
