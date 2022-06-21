#!/bin/bash

# prepare test script
mv $HOME/.github/test/test_all.py $HOME
# prepare config
mkdir $HOME/config
gpg --quiet --batch --yes --decrypt --passphrase="$PASSPHRASE" --output $HOME/config/config.yaml $HOME/.github/test/config.yaml.gpg
